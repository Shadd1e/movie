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

def _normal_title(value: str) -> str:
    """Normalize a title for matching DeepSeek candidates against TMDB results."""
    import re
    return re.sub(r"[^a-z0-9]+", "", (value or "").casefold())


def _year_from_date(value):
    try:
        return int(str(value)[:4])
    except (TypeError, ValueError):
        return None


def _tmdb_match(results: list[dict], title: str, release_year: int | None):
    """Choose the closest title/year match instead of blindly taking the first search result."""
    target = _normal_title(title)
    if not target:
        return None

    def rank(item):
        candidate_title = _normal_title(item.get("title") or item.get("original_title") or "")
        candidate_year = _year_from_date(item.get("release_date"))
        exact = candidate_title == target
        related = target in candidate_title or candidate_title in target
        year_match = release_year is not None and candidate_year == release_year
        year_distance = abs(candidate_year - release_year) if release_year and candidate_year else 999
        popularity = float(item.get("popularity") or 0)
        return (int(exact), int(year_match), int(related), -year_distance, popularity)

    valid = [x for x in results if x.get("id") and (x.get("title") or x.get("original_title"))]
    if not valid:
        return None
    best = max(valid, key=rank)
    best_title = _normal_title(best.get("title") or best.get("original_title") or "")
    if best_title != target and target not in best_title and best_title not in target:
        return None
    return best


async def _enrich_deepseek_candidate(candidate: dict) -> dict:
    """Use TMDB as the source of truth for poster, release date, overview and credits."""
    title = str(candidate.get("title") or "").strip()
    if not title or not settings.tmdb_access_token:
        return candidate

    year = _year_from_date(candidate.get("release_date")) or candidate.get("release_year")
    try:
        search_data = await search_movies(title)
        match = _tmdb_match(search_data.get("results", []), title, year)
        if not match:
            return candidate

        details = await movie_details(int(match["id"]))
        credits = details.get("credits") or {}
        genres = [g.get("name") for g in details.get("genres", []) if g.get("name")]
        cast = [x.get("name") for x in credits.get("cast", [])[:8] if x.get("name")]
        director = next((x.get("name") for x in credits.get("crew", [])
                         if x.get("job") == "Director" and x.get("name")), None)
        keywords = [x.get("name") for x in (details.get("keywords") or {}).get("keywords", [])[:20]
                    if x.get("name")]
        enriched = {
            "id": details.get("id"),
            "title": details.get("title") or title,
            "overview": details.get("overview") or candidate.get("overview"),
            "release_date": details.get("release_date") or candidate.get("release_date"),
            "genres": genres or candidate.get("genres", []),
            "cast": cast,
            "director": director,
            "keywords": keywords,
            "poster_path": details.get("poster_path"),
            "source": "deepseek+tmdb",
            "deepseek_reason": candidate.get("deepseek_reason"),
        }
        try:
            supabase.table("movies").upsert({k: v for k, v in enriched.items() if k != "deepseek_reason"}).execute()
        except Exception:
            pass  # A cache-write failure must not break recommendations.
        return enriched
    except Exception:
        return candidate  # Keep the DeepSeek candidate if TMDB is temporarily unavailable.


@app.get("/recommendations")
async def recommendations(user=Depends(auth_user)):
    """Generate candidates with DeepSeek first, then enrich each candidate with TMDB."""
    uid = str(user.id)
    try:
        profile = user_profile(uid)
    except Exception:
        profile = {"genres": [], "favourite_movie_ids": [], "preferred_movie_years": []}

    genres = profile.get("genres", []) or []
    favourite_ids = profile.get("favourite_movie_ids", []) or []
    preferred_years = profile.get("preferred_movie_years", []) or []
    try:
        movies = rows("movies")
    except Exception:
        movies = []
    try:
        ratings = rows("ratings", "user_id,movie_id,rating")
    except Exception:
        ratings = []

    favourite_titles = [str(m["title"]) for m in movies
                        if m.get("id") in favourite_ids and m.get("title")]
    rated_ids = {str(r.get("movie_id")) for r in ratings
                 if str(r.get("user_id")) == uid and r.get("movie_id") is not None}
    rated_titles = [str(m["title"]) for m in movies
                    if str(m.get("id")) in rated_ids and m.get("title")]

    candidates = await recommend_movies_with_deepseek(
        genres, favourite_titles, rated_titles, limit=12,
        preferred_movie_years=preferred_years,
    )
    source = "deepseek"

    # If DeepSeek is unavailable, retain the existing hybrid engine as a fallback.
    if not candidates and movies:
        try:
            engine = Recommender(movies, ratings)
            local_recs = engine.recommend(uid, genres, favourite_ids,
                                          preferred_movie_years=preferred_years)
            candidates = []
            for item in local_recs[:12]:
                movie_data = item.get("movie") or {}
                signals = item.get("signals") or {"content_score": 0, "collaborative_score": 0}
                candidates.append({
                    **movie_data,
                    "deepseek_reason": item.get("reason") or fallback_reason(movie_data, signals, genres),
                    "_existing_score": item.get("score", 0),
                    "_existing_signals": signals,
                })
            source = "hybrid_fallback"
        except Exception:
            candidates = []

    if not candidates:
        if not settings.deepseek_api_key:
            raise HTTPException(status_code=503,
                detail="Recommendations are unavailable because DEEPSEEK_API_KEY is not configured.")
        raise HTTPException(status_code=502,
            detail="The recommendation service returned no usable movies. Please try again.")

    import asyncio
    enriched = await asyncio.gather(
        *(_enrich_deepseek_candidate(item) for item in candidates[:12]),
        return_exceptions=True,
    )
    normalized = []
    for index, result in enumerate(enriched):
        candidate = candidates[index] if isinstance(result, Exception) else result
        title = str(candidate.get("title") or "").strip()
        if not title:
            continue
        reason = str(candidate.get("deepseek_reason") or "").strip()
        if not reason:
            reason = (f"A thoughtful match for your interest in {', '.join(genres[:2]).lower()}."
                      if genres else "A movie selected to give you something worthwhile to explore.")
        normalized.append({
            "movie": {
                "id": candidate.get("id"), "title": title,
                "overview": candidate.get("overview"),
                "release_date": candidate.get("release_date"),
                "genres": candidate.get("genres") or [],
                "cast": candidate.get("cast") or [],
                "director": candidate.get("director"),
                "keywords": candidate.get("keywords") or [],
                "poster_path": candidate.get("poster_path"),
                "source": candidate.get("source") or "deepseek",
            },
            "reason": reason,
            "score": candidate.get("_existing_score", max(0.5, 1.0 - index * 0.025)),
            "signals": candidate.get("_existing_signals") or {
                "source": source, "ratings_used": len(rated_ids),
                "genres_used": genres, "preferred_movie_years": preferred_years,
            },
        })
    if not normalized:
        raise HTTPException(status_code=502,
            detail="The recommendation service did not return valid movie titles. Please try again.")
    return {"source": source + ("+tmdb" if settings.tmdb_access_token else ""),
            "recommendations": normalized}

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
