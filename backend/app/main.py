from fastapi import FastAPI, Depends, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .db import supabase, current_user
from .schemas import Onboarding, Rating, NaturalRequest
from .tmdb import search_movies, movie_details
from .recommender import Recommender
from .deepseek import explain_recommendation, interpret_preference

app = FastAPI(title="Maple Movies API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=[settings.frontend_origin], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

def auth_user(authorization: str | None = Header(default=None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Please sign in first.")
    try:
        return current_user(authorization.split(" ",1)[1])
    except Exception:
        raise HTTPException(401, "Your session has expired. Please sign in again.")

def rows(table, columns="*"):
    return supabase.table(table).select(columns).execute().data

def user_profile(uid):
    result = supabase.table("profiles").select("*").eq("id", uid).maybe_single().execute()
    return result.data or {"id": uid, "genres": [], "favourite_movie_ids": []}

def build_engine():
    movies = rows("movies")
    ratings = rows("ratings", "user_id,movie_id,rating")
    return Recommender(movies, ratings)

@app.get("/health")
def health(): return {"ok": True}

@app.get("/movies/search")
async def movie_search(q: str = Query(min_length=1, max_length=100)):
    local = supabase.table("movies").select("*").ilike("title", f"%{q}%").limit(20).execute().data
    if local: return {"source":"database", "results":local}
    if not settings.tmdb_access_token: return {"source":"database", "results":[]}
    data = await search_movies(q)
    return {"source":"tmdb", "results": data.get("results", [])[:20]}

@app.get("/movies/{movie_id}")
async def movie(movie_id: int):
    local = supabase.table("movies").select("*").eq("id", movie_id).maybe_single().execute().data
    if local: return local
    if settings.tmdb_access_token:
        m = await movie_details(movie_id)
        credits=m.get("credits",{})
        row={"id":m["id"],"title":m.get("title"),"overview":m.get("overview"),"release_date":m.get("release_date") or None,"genres":[g["name"] for g in m.get("genres",[])],"cast":[x["name"] for x in credits.get("cast",[])[:8]],"director":next((x["name"] for x in credits.get("crew",[]) if x.get("job")=="Director"),None),"keywords":[x["name"] for x in m.get("keywords",{}).get("keywords",[])[:20]],"poster_path":m.get("poster_path"),"source":"tmdb"}
        supabase.table("movies").upsert(row).execute()
        return row
    raise HTTPException(404, "Movie not found in the catalogue.")

@app.post("/onboarding")
def onboarding(payload: Onboarding, user=Depends(auth_user)):
    data={"id":str(user.id),"age_group":payload.age_group,"genres":payload.genres,"favourite_movie_ids":payload.favourite_movie_ids}
    supabase.table("profiles").upsert(data).execute()
    return {"ok":True}

@app.post("/ratings")
def rating(payload: Rating, user=Depends(auth_user)):
    data={"user_id":str(user.id),"movie_id":payload.movie_id,"rating":payload.rating}
    supabase.table("ratings").upsert(data, on_conflict="user_id,movie_id").execute()
    return {"ok":True}

@app.get("/recommendations")
async def recommendations(user=Depends(auth_user)):
    uid=str(user.id); profile=user_profile(uid); engine=build_engine()
    recs=engine.recommend(uid, profile.get("genres",[]), profile.get("favourite_movie_ids",[]))
    for i, r in enumerate(recs):
        reason = await explain_recommendation(r["movie"], r["signals"]) if i < 5 else None
        r["reason"] = reason or fallback_reason(r["movie"], r["signals"], profile.get("genres",[]))
    return {"recommendations":recs}

def fallback_reason(movie, signals, genres):
    matched=[g for g in movie.get("genres",[]) if g.lower() in {x.lower() for x in genres}]
    if matched: return f"It fits your interest in {matched[0].lower()} stories."
    if signals["content_score"] >= .55: return "Its story and themes are close to movies you have enjoyed."
    if signals["collaborative_score"] >= .55: return "Its rating pattern is close to titles that fit your taste."
    return "It is a good title to explore from the current movie collection."

@app.post("/preferences/interpret")
async def preferences(payload: NaturalRequest, user=Depends(auth_user)):
    return await interpret_preference(payload.request)
