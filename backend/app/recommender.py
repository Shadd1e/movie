from collections import defaultdict
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD

class Recommender:
    def __init__(self, movies: list[dict], ratings: list[dict]):
        self.movies = movies
        self.ratings = ratings
        self.movie_index = {m["id"]: i for i, m in enumerate(movies)}
        self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1,2), min_df=1)
        docs = [self._doc(m) for m in movies]
        self.matrix = self.vectorizer.fit_transform(docs) if docs else None
        self.rating_map = {(r["user_id"], r["movie_id"]): float(r["rating"]) for r in ratings}
        self.user_ids = sorted({r["user_id"] for r in ratings})
        self.user_index = {u:i for i,u in enumerate(self.user_ids)}
        self.svd = None
        self.predicted = None
        if len(self.user_ids) >= 2 and movies:
            R = np.zeros((len(self.user_ids), len(movies)))
            for r in ratings:
                if r["movie_id"] in self.movie_index:
                    R[self.user_index[r["user_id"]], self.movie_index[r["movie_id"]]] = r["rating"]
            k = max(1, min(20, min(R.shape)-1))
            if k >= 1 and np.count_nonzero(R) >= 3:
                self.svd = TruncatedSVD(n_components=k, random_state=42)
                self.predicted = self.svd.inverse_transform(self.svd.fit_transform(R))

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

    def recommend(self, user_id: str, genres: list[str], favourite_ids: list[int], limit=12):
        if not self.movies:
            return []
        profile_parts = []
        for g in genres: profile_parts.append(g)
        for mid in favourite_ids:
            if mid in self.movie_index: profile_parts.append(self._doc(self.movies[self.movie_index[mid]]))
        user_ratings = [r for r in self.ratings if r["user_id"] == user_id]
        for r in user_ratings:
            if r["rating"] >= 4 and r["movie_id"] in self.movie_index:
                profile_parts.append(self._doc(self.movies[self.movie_index[r["movie_id"]]]))
        if profile_parts:
            profile = self.vectorizer.transform([" ".join(profile_parts)])
            content = cosine_similarity(profile, self.matrix).ravel()
        else:
            content = np.zeros(len(self.movies))
        if self.predicted is not None and user_id in self.user_index:
            collab = self.predicted[self.user_index[user_id]].copy()
            mn, mx = collab.min(), collab.max()
            collab = (collab-mn)/(mx-mn) if mx > mn else np.zeros_like(collab)
        else:
            collab = np.zeros(len(self.movies))
        rating_count = len(user_ratings)
        alpha = 1.0 if rating_count < 3 else max(0.35, 1 - rating_count/20)
        beta = 1 - alpha
        genre_set = {g.lower() for g in genres}
        results = []
        rated = {r["movie_id"] for r in user_ratings}
        for i,m in enumerate(self.movies):
            if m["id"] in rated: continue
            genre_match = len(genre_set.intersection({g.lower() for g in (m.get("genres") or [])}))
            score = alpha*float(content[i]) + beta*float(collab[i]) + min(0.12, genre_match*0.04)
            signals = {"content_score": round(float(content[i]),3), "collaborative_score": round(float(collab[i]),3), "genre_match": genre_match, "ratings_used": rating_count}
            results.append({"movie": m, "score": round(score,4), "signals": signals})
        return sorted(results, key=lambda x:x["score"], reverse=True)[:limit]
