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


def _tokens(text: str) -> list[str]:
    words = [w for w in _TOKEN_RE.findall(text.lower()) if w not in _STOP_WORDS]
    return words + [f"{a} {b}" for a, b in zip(words, words[1:])]


class Recommender:
    def __init__(self, movies: list[dict], ratings: list[dict]):
        self.movies = movies
        self.ratings = ratings
        self.movie_index = {m["id"]: i for i, m in enumerate(movies)}
        self.docs = [_tokens(self._doc(m)) for m in movies]
        self.idf = self._build_idf(self.docs)
        self.matrix = np.array([self._vector(doc) for doc in self.docs], dtype=float) if self.docs else np.empty((0, 0))
        self.rating_map = {(r["user_id"], r["movie_id"]): float(r["rating"]) for r in ratings}
        self.user_ids = sorted({r["user_id"] for r in ratings})
        self.user_index = {u: i for i, u in enumerate(self.user_ids)}
        self.predicted = None

        if len(self.user_ids) >= 2 and movies:
            R = np.zeros((len(self.user_ids), len(movies)), dtype=float)
            for r in ratings:
                if r["movie_id"] in self.movie_index:
                    R[self.user_index[r["user_id"]], self.movie_index[r["movie_id"]]] = float(r["rating"])
            k = max(1, min(20, min(R.shape) - 1))
            if k >= 1 and np.count_nonzero(R) >= 3:
                try:
                    U, s, Vt = np.linalg.svd(R, full_matrices=False)
                    k = min(k, len(s))
                    self.predicted = (U[:, :k] * s[:k]) @ Vt[:k, :]
                except np.linalg.LinAlgError:
                    self.predicted = None

    @staticmethod
    def _doc(m):
        return " ".join([
            str(m.get("title") or ""),
            " ".join(m.get("genres") or []),
            str(m.get("overview") or ""),
            " ".join(m.get("keywords") or []),
            " ".join(m.get("cast") or []),
            str(m.get("director") or ""),
        ])

    @staticmethod
    def _build_idf(docs: list[list[str]]) -> dict[str, float]:
        n = len(docs)
        if not n:
            return {}
        df = Counter()
        for doc in docs:
            df.update(set(doc))
        return {term: math.log((1 + n) / (1 + count)) + 1.0 for term, count in df.items()}

    def _vector(self, tokens: list[str]) -> np.ndarray:
        terms = list(self.idf)
        if not terms:
            return np.zeros(0, dtype=float)
        counts = Counter(tokens)
        total = max(1, len(tokens))
        vec = np.array([(counts[t] / total) * self.idf[t] for t in terms], dtype=float)
        norm = np.linalg.norm(vec)
        return vec / norm if norm else vec

    def _profile_similarity(self, text: str) -> np.ndarray:
        if not len(self.movies) or not self.idf:
            return np.zeros(len(self.movies), dtype=float)
        profile = self._vector(_tokens(text))
        if profile.size == 0:
            return np.zeros(len(self.movies), dtype=float)
        return self.matrix @ profile

    def recommend(self, user_id: str, genres: list[str], favourite_ids: list[int], limit=12):
        if not self.movies:
            return []
        profile_parts = list(genres)
        for mid in favourite_ids:
            if mid in self.movie_index:
                profile_parts.append(self._doc(self.movies[self.movie_index[mid]]))
        user_ratings = [r for r in self.ratings if r["user_id"] == user_id]
        for r in user_ratings:
            if r["rating"] >= 4 and r["movie_id"] in self.movie_index:
                profile_parts.append(self._doc(self.movies[self.movie_index[r["movie_id"]]]))
        content = self._profile_similarity(" ".join(profile_parts)) if profile_parts else np.zeros(len(self.movies))

        if self.predicted is not None and user_id in self.user_index:
            collab = self.predicted[self.user_index[user_id]].copy()
            mn, mx = collab.min(), collab.max()
            collab = (collab - mn) / (mx - mn) if mx > mn else np.zeros_like(collab)
        else:
            collab = np.zeros(len(self.movies))

        rating_count = len(user_ratings)
        alpha = 1.0 if rating_count < 3 else max(0.35, 1 - rating_count / 20)
        beta = 1 - alpha
        genre_set = {g.lower() for g in genres}
        results = []
        rated = {r["movie_id"] for r in user_ratings}
        for i, m in enumerate(self.movies):
            if m["id"] in rated:
                continue
            genre_match = len(genre_set.intersection({g.lower() for g in (m.get("genres") or [])}))
            score = alpha * float(content[i]) + beta * float(collab[i]) + min(0.12, genre_match * 0.04)
            signals = {
                "content_score": round(float(content[i]), 3),
                "collaborative_score": round(float(collab[i]), 3),
                "genre_match": genre_match,
                "ratings_used": rating_count,
            }
            results.append({"movie": m, "score": round(score, 4), "signals": signals})
        return sorted(results, key=lambda x: x["score"], reverse=True)[:limit]
