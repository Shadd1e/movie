# Maple Movies

A senior-friendly web movie recommendation system built around a transparent hybrid recommender: TF-IDF + cosine similarity for content, matrix factorisation for collaborative signals, onboarding for cold start, TMDB for movie metadata, Supabase for data/auth, and DeepSeek as an optional language/AI layer for natural-language preference interpretation and recommendation explanations.

## Design principles

- **Senior-friendly, not childish:** readable typography, generous controls, calm hierarchy, plain language.
- **Evidence before AI:** movie facts come from TMDB/database records. DeepSeek does not invent factual metadata.
- **Algorithm first:** recommendations are produced by the implemented recommender. AI explains or interprets the result rather than replacing the ranking model.
- **Natural language:** avoid repetitive template phrases such as “Based on your preferences, we recommend…”. Explanations use concrete signals from the recommendation engine and vary their wording.
- **No fake evaluation:** metrics remain “not run” until the actual dataset and test run are executed.

## Stack

- Frontend: Next.js, React, TypeScript, CSS
- Backend: FastAPI, Python
- Database/Auth: Supabase PostgreSQL + Supabase Auth
- Movie metadata: TMDB API
- AI: DeepSeek API
- Recommendation: scikit-learn TF-IDF/cosine + TruncatedSVD hybrid

## Environment

Backend `.env`:

```env
SUPABASE_URL=https://YOUR_PROJECT.supabase.co
SUPABASE_SERVICE_ROLE_KEY=YOUR_SERVER_ONLY_KEY
TMDB_ACCESS_TOKEN=YOUR_TMDB_V4_READ_ACCESS_TOKEN
DEEPSEEK_API_KEY=YOUR_DEEPSEEK_KEY
DEEPSEEK_MODEL=deepseek-flash
FRONTEND_ORIGIN=http://localhost:3000
```

Frontend `.env.local`:

```env
NEXT_PUBLIC_SUPABASE_URL=https://YOUR_PROJECT.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=YOUR_PUBLIC_ANON_KEY
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Never put `SUPABASE_SERVICE_ROLE_KEY`, `TMDB_ACCESS_TOKEN`, or `DEEPSEEK_API_KEY` in the frontend.

## Run

### 1. Supabase

Run `supabase/schema.sql` in the Supabase SQL editor. Then enable email/password authentication in Supabase Auth.

### 2. Backend

```bash
cd backend
python -m venv .venv
# Windows Git Bash:
source .venv/Scripts/activate
# macOS/Linux:
# source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

Open `http://localhost:3000`.

### 4. Seed movie data

With the backend running and TMDB token configured:

```bash
cd backend
python scripts/seed_tmdb.py --query "The Intern" --query "The Shawshank Redemption" --query "Hidden Figures"
```

You can also add more titles through the same script.

## Academic alignment

The implementation preserves the project's stated core method: content-based filtering with TF-IDF and cosine similarity, collaborative filtering through matrix factorisation, weighted hybrid scoring, onboarding-based cold-start handling, and short explanations. The age definition used in the implementation is **60 years and above**, matching the report's current definition and making the interface target explicit.

## Revised academic/report material

The `docs/REPORT_TABLES.md` file contains the rebuilt tables for the report, including the corrected age-range definition, database design, API endpoints, functional tests and evaluation metrics. `docs/CITATION_POLICY.md` records the literature rule: keep at least 25 academic sources dated 2021 through the current year, with the current report's 28 academic references retained where appropriate.

The current report's academic bibliography contains 28 sources dated 2021–2025. Undated framework/API documentation is treated separately from the academic literature count.
# movie
