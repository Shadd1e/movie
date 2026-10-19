from collections import Counter
import math
import re
import numpy as np

_TOKEN_RE = re.compile(r"[a-z0-9]+")
_STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "has",
    "he", "in", "is", "it", "its", "of", "on", "that", "the", "to", "was",
    "were", "will", "with", "this", "they", "their", "or", "but", "not",
}
YEAR_RANGES = {
    "before_1980": (0, 1979),
    "1980_1999": (1980, 1999),
    "2000_2009": (2000, 2009),
    "2010_2019": (2010, 2019),
    "2020_onwards": (2020, 2100),
}


def _tokens(text: str) -> list[str]:
    words = [w for w in _TOKEN_RE.findall(text.lower()) if w not in _STOP_WORDS]
    return words + [f"{a} {b}" for a, b in zip(words, words[1:])]


def _year(movie: dict) -> int | None:
    release_date = movie.get("release_date")
    if not release_date:
        return None
    try:
        year = int(str(release_date)[:4])
        return year if 1800 <= year <= 2100 else None
    except (TypeError, ValueError):
        return None


def _year_match(movie: dict, preferences: list[str]) -> bool | None:
    year = _year(movie)
    if not preferences or year is None:
        return None
    return any(key in YEAR_RANGES and YEAR_RANGES[key][0] <= year <= YEAR_RANGES[key][1] for key in preferences)


class Recommender:
    def __init__(self, movies: list[dict], ratings: list[dict]):
        self.movies = movies
        self.ratings = ratings
        self.movie_index = {m["id"]: i for i, m in enumerate(movies)}
        self.docs = [_tokens(self._doc(m)) for m in movies]
        self.idf = self._build_idf(self.docs)
        self.matrix = np.array([self._vector(doc) for doc in self.docs], dtype=float) if self.docs else np.empty((0, 0))
        self.rating_map = {(str(r["user_id"]), r["movie_id"]): float(r["rating"]) for r in ratings}
        self.user_ids = sorted({str(r["user_id"]) for r in ratings})
        self.user_index = {u: i for i, u in enumerate(self.user_ids)}
        self.predicted = None

        if len(self.user_ids) >= 2 and movies:
            R = np.zeros((len(self.user_ids), len(movies)), dtype=float)
            for r in ratings:
                if r["movie_id"] in self.movie_index:
                    R[self.user_index[str(r["user_id"])], self.movie_index[r["movie_id"]]] = float(r["rating"])
            k = max(1, min(20, min(R.shape) - 1))
            if np.count_nonzero(R) >= 3:
                try:
                    U, s, Vt = np.linalg.svd(R, full_matrices=False)
                    k = min(k, len(s))
                    self.predicted = (U[:, :k] * s[:k]) @ Vt[:k, :]
                except np.linalg.LinAlgError:
                    self.predicted = None

    @staticmethod
    def _doc(m):
        genres = m.get("genres") or []
        keywords = m.get("keywords") or []
        cast = m.get("cast") or []
        if not isinstance(genres, list): genres = []
        if not isinstance(keywords, list): keywords = []
        if not isinstance(cast, list): cast = []
        return " ".join([
            str(m.get("title") or ""), " ".join(map(str, genres)),
            str(m.get("overview") or ""), " ".join(map(str, keywords)),
            " ".join(map(str, cast)), str(m.get("director") or ""),
        ])

    @staticmethod
    def _build_idf(docs: list[list[str]]) -> dict[str, float]:
        n = len(docs)
        if not n: return {}
        df = Counter()
        for doc in docs: df.update(set(doc))
        return {term: math.log((1 + n) / (1 + count)) + 1.0 for term, count in df.items()}

    def _vector(self, tokens: list[str]) -> np.ndarray:
        terms = list(self.idf)
        if not terms: return np.zeros(0, dtype=float)
        counts = Counter(tokens)
        total = max(1, len(tokens))
        vec = np.array([(counts[t] / total) * self.idf[t] for t in terms], dtype=float)
        norm = np.linalg.norm(vec)
        return vec / norm if norm else vec

    def _profile_similarity(self, text: str) -> np.ndarray:
        if not self.movies or not self.idf: return np.zeros(len(self.movies), dtype=float)
        profile = self._vector(_tokens(text))
        if profile.size == 0: return np.zeros(len(self.movies), dtype=float)
        return self.matrix @ profile

    def recommend(self, user_id: str, genres: list[str], favourite_ids: list[int], limit=12,
                  preferred_movie_years: list[str] | None = None):
        if not self.movies: return []
        preferred_movie_years = preferred_movie_years or []
        profile_parts = list(genres)
        for mid in favourite_ids:
            if mid in self.movie_index:
                profile_parts.append(self._doc(self.movies[self.movie_index[mid]]))
        user_ratings = [r for r in self.ratings if str(r["user_id"]) == str(user_id)]
        for r in user_ratings:
            if float(r["rating"]) >= 4 and r["movie_id"] in self.movie_index:
                profile_parts.append(self._doc(self.movies[self.movie_index[r["movie_id"]]]))
        content = self._profile_similarity(" ".join(profile_parts)) if profile_parts else np.zeros(len(self.movies))

        if self.predicted is not None and str(user_id) in self.user_index:
            collab = self.predicted[self.user_index[str(user_id)]].copy()
            mn, mx = collab.min(), collab.max()
            collab = (collab - mn) / (mx - mn) if mx > mn else np.zeros_like(collab)
        else:
            collab = np.zeros(len(self.movies))

        rating_count = len(user_ratings)
        alpha = 1.0 if rating_count < 3 else max(0.35, 1 - rating_count / 20)
        beta = 1 - alpha
        genre_set = {g.casefold() for g in genres}
        rated = {r["movie_id"] for r in user_ratings}
        results = []
        for i, movie in enumerate(self.movies):
            if movie.get("id") in rated: continue
            movie_genres = movie.get("genres") or []
            if not isinstance(movie_genres, list): movie_genres = []
            genre_match = len(genre_set.intersection({str(g).casefold() for g in movie_genres}))
            year_match = _year_match(movie, preferred_movie_years)
            year_adjustment = (0.18 if year_match else -0.08) if year_match is not None else 0.0
            score = alpha * float(content[i]) + beta * float(collab[i]) + min(0.12, genre_match * 0.04) + year_adjustment
            signals = {
                "content_score": round(float(content[i]), 3),
                "collaborative_score": round(float(collab[i]), 3),
                "genre_match": genre_match,
                "ratings_used": rating_count,
                "preferred_year_match": year_match,
                "year_adjustment": year_adjustment,
            }
            results.append({"movie": movie, "score": round(score, 4), "signals": signals})
        return sorted(results, key=lambda x: x["score"], reverse=True)[:limit]
