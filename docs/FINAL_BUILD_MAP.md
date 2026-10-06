# Final build map

This is the build order used for the corrected version. It is intentionally written in plain language so the project can be explained during a demonstration or defence.

1. **Start with the person, not the algorithm.** The interface asks for an age range within the study population and a few genres. The age range is 60–69, 70–79 or 80+, while the recommendation model does not assume that age determines taste.
2. **Give a new user something useful immediately.** The selected genres and favourite movies form the first content profile, so the system does not wait for a rating history.
3. **Bring in trustworthy movie facts.** TMDB supplies movie metadata. The backend caches the records in Supabase so the recommendation engine works from a consistent local catalogue.
4. **Build the content signal.** Movie text is combined and represented with TF-IDF. Cosine similarity measures how closely candidate movies match the user's current content profile.
5. **Add the collaborative signal when it becomes meaningful.** Ratings are stored per user/movie pair. Matrix factorisation contributes only when enough interaction data exists.
6. **Combine the signals.** A new user leans heavily on content. As ratings accumulate, the collaborative component can have more influence. The exact final weights must be reported from the executed experiment.
7. **Keep DeepSeek in the right place.** It can interpret a plain-language movie request and turn the actual recommendation signals into a short explanation. It is not allowed to invent movie facts or replace the academic ranking method.
8. **Protect personal data.** Supabase Auth handles identity. RLS policies restrict user-owned profiles, ratings and interactions. Server-only secrets stay out of the browser.
9. **Test the actual system.** Registration, login, onboarding, search, details, ratings, recommendation, explanations, authorization, RLS and cold-start behaviour all get explicit tests.
10. **Measure before making claims.** Precision@K, Recall@K, MAP@K, coverage and cold-start success are measured against a documented split and baseline. No invented result goes into the report.
11. **Capture the real screens.** Chapter Four screenshots come from the executed build, not placeholders.
12. **Rebuild the report around what was actually implemented.** Tables, architecture, methodology, implementation and evaluation are updated together so the report does not describe an older version of the software.

## Human-sounding rule

If a sentence would sound strange when a person says it to another person, it should not appear in the interface. The product should be calm, adult and respectful, without treating older adults as children or repeatedly announcing that an algorithm has made a decision.
