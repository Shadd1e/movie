# Supervisor Fix Map

This map turns the visible handwritten corrections and the current report into implementation changes. It is deliberately conservative: anything not supported by the marked pages or the existing report is treated as an implementation decision, not as a claim about the supervisor's wording.

## 1. Define “Senior Citizen” clearly

**Correction:** The report must state the age boundary used by the study.

**Implementation:** The system is designed for users aged **60 years and above**. The wording is kept respectful and does not assume every person in that age group has the same abilities or tastes.

**Report locations:** Definition of Terms, Scope, accessibility discussion, requirements and evaluation.

## 2. Explain why the selected recommendation measures/features are used

**Correction:** Do not simply list TF-IDF, cosine similarity, SVD, cold-start and explanations. Explain what each contributes and why it belongs in this particular system.

**Implementation:**
- TF-IDF represents movie text in a transparent way.
- Cosine similarity compares content representations.
- Matrix factorisation adds interaction-based evidence when enough ratings exist.
- Onboarding supplies an initial signal before ratings exist.
- Hybrid weighting prevents the collaborative component from dominating a new user's recommendations.
- Explanations expose the strongest observable reason for a recommendation.

## 3. Avoid making the AI the recommender

**Correction/quality safeguard:** DeepSeek is auxiliary. It must not replace the academic recommendation method.

**Implementation:** TF-IDF/cosine and collaborative scores produce the ranking. DeepSeek can interpret natural-language requests and write a concise explanation from supplied signals.

## 4. Use a real movie-data source

**Implementation:** TMDB is the external metadata source. The database caches imported records so recommendation requests do not depend on a live external call every time.

## 5. Do not fabricate evaluation results

The current report itself says final numerical evaluation results and screenshots should be populated from the executed implementation. This build therefore keeps evaluation as a reproducible step rather than inventing numbers.

## 6. Make the interface sound human

The interface avoids corporate or AI-generated phrasing. It uses short, natural sentences, avoids patronising language, and gives users a reason for a recommendation rather than a generic system message.

## 7. Make explanations grounded

DeepSeek receives only movie facts and computed recommendation signals. It is instructed not to invent facts, mention algorithms, or make exaggerated claims.

## 8. Keep the report and software aligned

The final report should describe the actual deployed architecture: Next.js/React frontend, FastAPI backend, Supabase PostgreSQL/Auth, TMDB metadata service, Python recommendation engine, and DeepSeek auxiliary AI service.
