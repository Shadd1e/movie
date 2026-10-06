import json
import httpx
from .config import settings

async def explain_recommendation(movie: dict, signals: dict) -> str | None:
    if not settings.deepseek_api_key:
        return None
    prompt = f"""Write one warm, natural sentence explaining why this movie may suit the user.
Do not mention algorithms, scores, AI, databases, or 'based on your preferences'.
Do not invent facts. Use only the supplied movie facts and recommendation signals.
Avoid sales language and avoid sounding like a system notification.
Movie: {movie.get('title')}
Genres: {', '.join(movie.get('genres') or [])}
Overview: {movie.get('overview') or ''}
Signals: {json.dumps(signals)}
"""
    payload = {
        "model": settings.deepseek_model,
        "messages": [
            {"role": "system", "content": "You write concise, human-sounding movie recommendation reasons for older adults. Be respectful and specific."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
        "max_tokens": 90,
    }
    headers = {"Authorization": f"Bearer {settings.deepseek_api_key}", "Content-Type": "application/json"}
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.post("https://api.deepseek.com/chat/completions", headers=headers, json=payload)
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"].strip()
    except Exception:
        return None

async def interpret_preference(request: str) -> dict:
    if not settings.deepseek_api_key:
        return {"genres": [], "keywords": [], "mood": None}
    tools = [{"type": "function", "function": {"name": "extract_movie_preferences", "description": "Extract structured movie preferences from a natural-language request.", "parameters": {"type": "object", "properties": {"genres": {"type": "array", "items": {"type": "string"}}, "keywords": {"type": "array", "items": {"type": "string"}}, "mood": {"type": ["string", "null"]}}, "required": ["genres", "keywords", "mood"], "additionalProperties": False}, "strict": True}}]
    payload = {"model": settings.deepseek_model, "messages": [{"role": "system", "content": "Extract movie preferences. Do not infer sensitive personal traits."}, {"role": "user", "content": request}], "tools": tools, "tool_choice": {"type": "function", "function": {"name": "extract_movie_preferences"}}, "temperature": 0}
    headers = {"Authorization": f"Bearer {settings.deepseek_api_key}", "Content-Type": "application/json"}
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.post("https://api.deepseek.com/chat/completions", headers=headers, json=payload)
            r.raise_for_status()
            call = r.json()["choices"][0]["message"]["tool_calls"][0]
            return json.loads(call["function"]["arguments"])
    except Exception:
        return {"genres": [], "keywords": [], "mood": None}
