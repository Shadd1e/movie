from fastapi import FastAPI, Depends, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .db import supabase, current_user
from .schemas import Onboarding, Rating, NaturalRequest
from .tmdb import search_movies, movie_details
from .recommender import Recommender
from .deepseek import (
    explain_recommendation,
    interpret_preference,
    recommend_movies_with_deepseek,
)

app = FastAPI(title="Maple Movies API", version="1.0.0")

# Allow deployed Vercel frontends to call the API.
# CORS matches the browser origin, not the full page URL.
# Example page: https://movie-henna-omega.vercel.app/movies
# Its origin is: https://movie-henna-omega.vercel.app
_allowed_origins = list(dict.fromkeys([
    "https://movie-henna-omega.vercel.app",
    settings.frontend_origin.rstrip("/"),
]))
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_origin_regex=r"^https://[A-Za-z0-9-]+\.vercel\.app$",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)

def auth_user(authorization: str | None = Header(default=None)):
    """Resolve the authenticated Supabase user from the frontend access token."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Please sign in first.")

    token = authorization.split(" ", 1)[1].strip()
    if not token:
        raise HTTPException(status_code=401, detail="Please sign in first.")

    try:
        user = current_user(token)
        if not user or not getattr(user, "id", None):
            raise HTTPException(
                status_code=401,
                detail="Your session has expired. Please sign in again.",
            )
        return user
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Your session has expired. Please sign in again.",
        )

def rows(table, columns="*"):
    return supabase.table(table).select(columns).execute().data

def user_profile(uid):
    result = supabase.table("profiles").select("*").eq("id", uid).maybe_single().execute()
    return result.data or {
        "id": uid, "name": None, "age_group": None, "region": None,
        "country": None, "genres": [], "favourite_movie_ids": [],
        "preferred_movie_years": [],
    }


def save_profile(uid: str, fields: dict, fallback_name: str | None = None):
    """Persist only supplied fields so older clients cannot erase newer preferences."""
    existing_result = supabase.table("profiles").select("id,name").eq("id", uid).maybe_single().execute()
    data = {key: value for key, value in fields.items() if key != "id"}
    if not data.get("name") and fallback_name and not (existing_result.data or {}).get("name"):
        data["name"] = fallback_name.strip()[:100] or None
    if existing_result.data:
        if data:
            result = supabase.table("profiles").update(data).eq("id", uid).execute()
            profile = (result.data or [None])[0]
        else:
            profile = user_profile(uid)
    else:
        initial = {
            "id": uid,
            "genres": [],
            "favourite_movie_ids": [],
            "preferred_movie_years": [],
            **data,
        }
        result = supabase.table("profiles").insert(initial).execute()
        profile = (result.data or [initial])[0]
    return profile or user_profile(uid)


def user_display_name(user) -> str | None:
    metadata = getattr(user, "user_metadata", None) or {}
    value = metadata.get("display_name") or metadata.get("full_name") or metadata.get("name")
    return str(value).strip()[:100] if value and str(value).strip() else None

def build_engine():
    movies = rows("movies")
    ratings = rows("ratings", "user_id,movie_id,rating")
    return Recommender(movies, ratings)

@app.get("/health")
def health():
    # Liveness only; external service credentials are never exposed here.
    return {"ok": True, "service": "maple-movies-api", "version": app.version}

@app.get("/movies/search")
async def movie_search(q: str = Query(min_length=1, max_length=100)):
    local = supabase.table("movies").select("*").ilike("title", f"%{q}%").limit(20).execute().data
    if local:
        return {"source": "database", "results": local}
    if not settings.tmdb_access_token:
        return {"source": "database", "results": []}
    data = await search_movies(q)
    return {"source": "tmdb", "results": data.get("results", [])[:20]}

@app.get("/movies/{movie_id}")
async def movie(movie_id: int):
    local = supabase.table("movies").select("*").eq("id", movie_id).maybe_single().execute().data
    if local:
        return local
    if settings.tmdb_access_token:
        m = await movie_details(movie_id)
        credits = m.get("credits", {})
        row = {
            "id": m["id"],
            "title": m.get("title"),
            "overview": m.get("overview"),
            "release_date": m.get("release_date") or None,
            "genres": [g["name"] for g in m.get("genres", [])],
            "cast": [x["name"] for x in credits.get("cast", [])[:8]],
            "director": next((x["name"] for x in credits.get("crew", []) if x.get("job") == "Director"), None),
            "keywords": [x["name"] for x in m.get("keywords", {}).get("keywords", [])[:20]],
            "poster_path": m.get("poster_path"),
            "source": "tmdb",
        }
        supabase.table("movies").upsert(row).execute()
        return row
    raise HTTPException(404, "Movie not found in the catalogue.")

@app.get("/profile")
def get_profile(user=Depends(auth_user)):
    try:
        profile = user_profile(str(user.id))
        if not profile.get("name"):
            profile["name"] = user_display_name(user)
        return profile
    except Exception:
        raise HTTPException(status_code=503, detail="Your profile could not be loaded. Please try again.")


@app.put("/profile")
def update_profile(payload: Onboarding, user=Depends(auth_user)):
    try:
        profile = save_profile(str(user.id), payload.model_dump(exclude_unset=True), user_display_name(user))
        return {"ok": True, "profile": profile}
    except Exception:
        raise HTTPException(status_code=503, detail="Your profile could not be saved. Check the database configuration and try again.")


@app.patch("/profile")
def patch_profile(payload: Onboarding, user=Depends(auth_user)):
    return update_profile(payload, user)


@app.post("/onboarding")
def onboarding(payload: Onboarding, user=Depends(auth_user)):
    try:
        profile = save_profile(str(user.id), payload.model_dump(exclude_unset=True), user_display_name(user))
        return {"ok": True, "profile": profile}
    except Exception:
        raise HTTPException(status_code=503, detail="Your preferences could not be saved. Check the database configuration and try again.")

@app.post("/ratings")
def rating(payload: Rating, user=Depends(auth_user)):
    data = {
        "user_id": str(user.id),
        "movie_id": payload.movie_id,
        "rating": payload.rating,
    }
    supabase.table("ratings").upsert(data, on_conflict="user_id,movie_id").execute()
    return {"ok": True}

@app.get("/recommendations")
async def recommendations(user=Depends(auth_user)):
    uid = str(user.id)
    profile = user_profile(uid)
    genres = profile.get("genres", []) or []
    favourite_ids = profile.get("favourite_movie_ids", []) or []
    preferred_years = profile.get("preferred_movie_years", []) or []

    movies = rows("movies")
    ratings = rows("ratings", "user_id,movie_id,rating")

    # Normal path: rank the local catalogue.
    if movies:
        engine = Recommender(movies, ratings)
        recs = engine.recommend(uid, genres, favourite_ids, preferred_movie_years=preferred_years)
        for i, r in enumerate(recs):
            reason = await explain_recommendation(r["movie"], r["signals"]) if i < 5 else None
            r["reason"] = reason or fallback_reason(r["movie"], r["signals"], genres)
        if recs:
            return {"source": "hybrid", "recommendations": recs}

    # Emergency path: do not leave the recommendation screen empty. Ask DeepSeek
    # for real movie candidates immediately, then enrich them from TMDB when possible.
    favourite_titles = []
    for movie_id in favourite_ids:
        local = next((m for m in movies if m.get("id") == movie_id), None)
        if local and local.get("title"):
            favourite_titles.append(local["title"])

    rated_ids = {r["movie_id"] for r in ratings if r["user_id"] == uid}
    rated_titles = [m.get("title") for m in movies if m.get("id") in rated_ids and m.get("title")]
    fallback = await recommend_movies_with_deepseek(
        genres, favourite_titles, rated_titles, limit=12,
        preferred_movie_years=preferred_years,
    )

    if fallback and settings.tmdb_access_token:
        # Turn DeepSeek's titles into canonical TMDB movie records where possible.
        enriched = []
        for candidate in fallback:
            try:
                data = await search_movies(candidate["title"])
                match = next((x for x in data.get("results", []) if x.get("id")), None)
                if match:
                    details = await movie_details(int(match["id"]))
                    credits = details.get("credits", {})
                    candidate.update({
                        "id": details.get("id"),
                        "title": details.get("title") or candidate["title"],
                        "overview": details.get("overview") or candidate.get("overview"),
                        "release_date": details.get("release_date") or candidate.get("release_date"),
                        "genres": [g["name"] for g in details.get("genres", [])] or candidate.get("genres", []),
                        "cast": [x["name"] for x in credits.get("cast", [])[:8]],
                        "director": next((x["name"] for x in credits.get("crew", []) if x.get("job") == "Director"), None),
                        "keywords": [x["name"] for x in details.get("keywords", {}).get("keywords", [])[:20]],
                        "poster_path": details.get("poster_path"),
                        "source": "deepseek+tmdb",
                    })
                    enriched.append(candidate)
                    continue
            except Exception:
                pass
            enriched.append(candidate)
        fallback = enriched

    # Keep the same response contract as the hybrid path: every recommendation
    # has a `movie` object, a reason, a score, and signals.
    normalized = []
    for candidate in fallback:
        reason = candidate.pop("deepseek_reason", None)
        if not reason:
            reason = (f"A strong match for your interest in {', '.join(genres[:2]).lower()}."
                      if genres else "A movie worth exploring based on your current choices.")
        normalized.append({
            "movie": candidate,
            "reason": reason,
            "score": 1.0,
            "signals": {"source": "deepseek", "ratings_used": len(rated_ids)},
        })

    return {"source": "deepseek", "recommendations": normalized}

def fallback_reason(movie, signals, genres):
    matched = [g for g in movie.get("genres", []) if g.lower() in {x.lower() for x in genres}]
    if matched:
        return f"It fits your interest in {matched[0].lower()} stories."
    if signals["content_score"] >= 0.55:
        return "Its story and themes are close to movies you have enjoyed."
    if signals["collaborative_score"] >= 0.55:
        return "Its rating pattern is close to titles that fit your taste."
    return "It is a good title to explore from the current movie collection."

@app.post("/preferences/interpret")
async def preferences(payload: NaturalRequest, user=Depends(auth_user)):
    return await interpret_preference(payload.request)
