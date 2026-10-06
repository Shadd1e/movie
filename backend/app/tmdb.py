import httpx
from .config import settings

BASE = "https://api.themoviedb.org/3"

async def tmdb_get(path: str, params: dict | None = None):
    if not settings.tmdb_access_token:
        raise RuntimeError("TMDB_ACCESS_TOKEN is not configured")
    headers = {"Authorization": f"Bearer {settings.tmdb_access_token}", "accept": "application/json"}
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(f"{BASE}{path}", headers=headers, params=params or {})
        r.raise_for_status()
        return r.json()

async def search_movies(query: str):
    return await tmdb_get("/search/movie", {"query": query, "include_adult": "false", "language": "en-US", "page": 1})

async def movie_details(movie_id: int):
    return await tmdb_get(f"/movie/{movie_id}", {"language": "en-US", "append_to_response": "credits,keywords"})

async def discover_movies(genre_id: int | None = None, page: int = 1):
    params = {"include_adult": "false", "include_video": "false", "language": "en-US", "sort_by": "popularity.desc", "page": page}
    if genre_id:
        params["with_genres"] = genre_id
    return await tmdb_get("/discover/movie", params)
