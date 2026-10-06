# Build and evaluation checklist

1. Create Supabase project and run `supabase/schema.sql`.
2. Enable email/password Auth.
3. Obtain TMDB API Read Access Token and place it only in backend `.env`.
4. Place the existing DeepSeek API key only in backend `.env`.
5. Start FastAPI and seed a reproducible movie subset.
6. Create a controlled ratings dataset or import the selected public ratings dataset.
7. Verify onboarding recommendations with zero ratings.
8. Add ratings and verify collaborative signal activation.
9. Compare popularity/content-only/hybrid models using the same held-out split.
10. Record Precision@K, Recall@K, MAP@K and catalogue coverage.
11. Test authentication, authorization, validation and rate/error handling.
12. Test the interface with the senior-friendly criteria in the UX guide.
13. Capture real screenshots from the finished build for Chapter Four.
14. Replace every “to be measured” statement in the report only after the run is complete.

## Recommended test split

Use a fixed random seed and a documented train/test split. Keep the test interactions hidden from model fitting. Report K values, number of users, number of movies, number of interactions, preprocessing settings and hybrid weights.

## Human-sounding acceptance check

Before submission, read every user-facing sentence aloud. Remove phrases that sound like system status messages, exaggerated claims, or generic AI prose. The interface should sound calm and useful, not promotional.
