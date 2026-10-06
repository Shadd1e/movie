# Revised Report Tables

These are the tables to use when the report is rebuilt around the executed system. They are deliberately tied to what the software actually does. Numerical evaluation cells must be filled only after the test run.

## Table 1.1: Definition of Terms

| Term | Definition used in this study |
|---|---|
| Senior Citizen | An adult aged 60 years or above. For interface evaluation, the study groups participants as 60–69, 70–79 and 80+. |
| Collaborative Filtering | A recommendation approach that uses patterns in user-item interactions to estimate preferences. |
| Content-Based Filtering | A recommendation approach that compares item characteristics with a user's expressed or observed interests. |
| Cosine Similarity | A measure used to compare the orientation of numerical vectors. |
| Cold Start | The lack of sufficient interaction information needed to personalise recommendations for a new user or item. |
| Hybrid Recommendation | A recommendation method that combines two or more recommendation signals. |
| Movie Metadata | Descriptive information about a movie, including title, genres, overview, release date, cast and director. |
| TF-IDF | A text representation method that gives greater weight to terms that are informative within a document but less common across documents. |
| User Profile | Stored information representing a user's selected preferences and interactions. |
| AI-Derived Metadata | Non-authoritative classifications or interpretations produced by the AI layer from supplied movie information. |

## Table 2.1: Summary of Related Literature

| Author(s) | Year | Focus | Method / contribution | Relevance |
|---|---:|---|---|---|
| Hssina et al. | 2021 | Collaborative recommendation | KNN and SVD | Supports interaction-based recommendation. |
| Anwar et al. | 2021 | SVD recommendation | Collaborative filtering and SVD++ | Supports matrix-factorisation methods. |
| Roy & Dutta | 2022 | Recommender systems | Systematic review | Provides broad design context. |
| Zangerle & Bauer | 2022 | Evaluation | Recommender evaluation framework | Supports reproducible evaluation. |
| Gelemet et al. | 2022 | Movie recommendation | TF-IDF and cosine similarity | Supports the content-based component. |
| Chen et al. | 2022 | Explainable recommendation | Explanation evaluation | Supports recommendation explanations. |
| Ge et al. | 2022 | Trustworthy recommendation | Survey | Supports transparency and trust considerations. |
| Hossain et al. | 2022 | Recommendation techniques | Survey | Provides comparison of recommendation approaches. |
| Tripathy et al. | 2022 | Matrix factorisation | Latent-factor recommendation | Supports the collaborative component. |
| Wang et al. | 2022 | Recommender fairness | Survey | Provides a caution against treating demographic groups as uniform. |
| Jafri et al. | 2023 | Cold start | Hybrid recommendation | Supports explicit cold-start handling. |
| Fernandes et al. | 2023 | Cold start | Hybrid recommendation | Supports combining complementary signals. |
| Permana & Wibowo | 2023 | Movie recommendation | TF-IDF and cosine similarity | Directly relevant to movie-content similarity. |
| Lu et al. | 2023 | Explanations | User perception of explanations | Supports user-facing recommendation reasons. |
| Patro et al. | 2023 | Cold start | Hybrid recommendation | Supports handling limited initial information. |
| Santosa et al. | 2023 | Hybrid recommendation | Cold-start mitigation | Supports hybrid scoring. |
| Hariyale & Raghuwanshi | 2024 | Hybrid recommendation | Precision and cold-start challenges | Supports hybrid design. |
| Huang et al. | 2024 | Retrieval in recommendation | Retrieval methods survey | Supports candidate retrieval considerations. |
| Uta et al. | 2024 | Knowledge-based recommendation | Review and research directions | Supports explicit preference/rule signals. |
| Kowald et al. | 2024 | Recommender research | Review | Provides current field context. |
| Wandhekar et al. | 2025 | Movie recommendation | TF-IDF and cosine similarity | Recent direct support for content similarity. |
| Chiriboga-Casanova et al. | 2025 | Older-adult web design | Accessibility-oriented design | Supports readable, clear interaction. |

The existing reference list contains additional 2021–2025 sources. The final bibliography should retain only sources actually cited in the report and should be checked for complete bibliographic details before submission.

## Table 3.1: Development Methodology Stages

| Stage | Activities | Output |
|---|---|---|
| Requirements analysis | Define target group, functions, constraints and supervisor corrections | Requirements specification |
| Data preparation | Obtain movie metadata, clean text and prepare ratings | Processed data |
| Design | Architecture, database, interface, recommendation logic and security | Design specification |
| Recommendation development | Implement TF-IDF, cosine similarity, SVD and hybrid ranking | Recommendation service |
| AI/API integration | Integrate TMDB and DeepSeek behind backend controls | External-service layer |
| Backend development | Authentication, API endpoints and database access | FastAPI service |
| Frontend development | Accessible pages and reusable components | Next.js application |
| Integration | Connect frontend, backend, database and external services | Integrated system |
| Testing | Functional, security, usability and recommendation tests | Test records |
| Refinement | Fix defects and improve wording and interaction | Final candidate build |

## Table 3.2: Input Specification

| Input | Source | Purpose |
|---|---|---|
| Account details | Registration | Create/authenticate account |
| Age range | Onboarding | Confirm study target group and support evaluation grouping |
| Genre preferences | Onboarding | Create initial content profile |
| Favourite movies | Onboarding | Strengthen initial content profile |
| Natural-language request | Preference helper | Convert plain-language requests into structured movie preferences |
| Movie rating | Movie detail | Record explicit preference |
| Search query | Discovery | Find movies |
| Preference changes | Profile/onboarding | Update recommendation inputs |

## Table 3.3: Output Specification

| Output | Description |
|---|---|
| Recommendation list | Ranked movies produced by the hybrid model |
| Recommendation reason | Short explanation grounded in available recommendation signals |
| Movie details | Title, release date, genres, overview, cast and director when available |
| Search results | Matching catalogue/API results |
| Profile information | Stored preferences and account information |
| Feedback message | Plain-language confirmation or error message |

## Table 3.4: Database Entities and Relationships

| Entity | Key fields | Relationship |
|---|---|---|
| profiles | id, display_name, age_group, genres, favourite_movie_ids | One profile per authenticated user |
| movies | id, title, overview, genres, cast, director | Referenced by ratings and interactions |
| ratings | user_id, movie_id, rating | Many ratings across users and movies; one rating per user/movie pair |
| interactions | id, user_id, movie_id, action, metadata | Records relevant application interactions |

## Table 4.1: Implementation Tools

| Tool | Role |
|---|---|
| Next.js / React | Frontend application |
| TypeScript | Frontend type safety |
| CSS | Senior-friendly visual design |
| FastAPI | Python backend/API |
| Pydantic | Request validation |
| Supabase Auth | Authentication |
| Supabase PostgreSQL | Persistent relational storage |
| TMDB API | Movie metadata source |
| DeepSeek API | Natural-language interpretation and grounded explanation |
| pandas / NumPy | Data processing |
| scikit-learn | TF-IDF, cosine similarity and matrix factorisation |
| Git | Version control |

## Table 4.2: Hardware Requirements

| Component | Minimum | Recommended |
|---|---|---|
| Processor | Dual-core CPU | Modern quad-core or better |
| RAM | 4 GB | 8 GB or more |
| Storage | 10 GB available | 20 GB or more |
| Display | 1366 × 768 | 1920 × 1080 |
| Network | Internet connection | Stable broadband |

## Table 4.3: Software Requirements

| Software | Requirement |
|---|---|
| Operating system | Windows, Linux or macOS |
| Python | 3.11 or compatible |
| Node.js | Current LTS |
| Database | Supabase PostgreSQL |
| Browser | Current Chrome, Edge, Firefox or Safari |
| Editor | VS Code or equivalent |

## Table 4.4: Technology Justification

| Technology | Reason for selection |
|---|---|
| Python | Mature ecosystem for text processing, numerical work and recommendation models. |
| FastAPI | Lightweight API layer that integrates directly with Python recommendation logic. |
| Next.js / React | Reusable components and a maintainable interactive web interface. |
| Supabase | Managed PostgreSQL and authentication with database-level access controls. |
| TMDB | Current movie metadata and catalogue information. |
| DeepSeek | Natural-language interpretation and concise explanation generation without replacing the core recommender. |
| scikit-learn | Established implementations of TF-IDF, cosine similarity and matrix decomposition. |

## Table 4.5: Backend API Endpoints

| Endpoint | Method | Purpose | Authentication |
|---|---|---|---|
| /health | GET | Service health check | No |
| /movies/search | GET | Search local catalogue/TMDB | No |
| /movies/{movie_id} | GET | Retrieve movie details | No |
| /onboarding | POST | Save age group and preferences | Yes |
| /ratings | POST | Save/update a rating | Yes |
| /recommendations | GET | Produce personalised recommendations | Yes |
| /preferences/interpret | POST | Interpret a natural-language movie request | Yes |

## Table 4.6: Functional Test Cases

| ID | Function | Test | Expected result | Status |
|---|---|---|---|---|
| TC01 | Registration | Valid email/password | Account created | To be run |
| TC02 | Login | Valid credentials | User authenticated | To be run |
| TC03 | Onboarding | Age group + genres selected | Preferences stored | To be run |
| TC04 | Search | Valid movie query | Matching results returned | To be run |
| TC05 | Details | Valid movie ID | Movie information displayed | To be run |
| TC06 | Rating | Movie + 1–5 rating | Rating stored | To be run |
| TC07 | Recommendation | Authenticated user | Ranked results returned | To be run |
| TC08 | Explanation | Recommended movie | Grounded reason displayed | To be run |
| TC09 | Profile | Changed preferences | New inputs stored | To be run |
| TC10 | Authorization | Missing/invalid token | Request rejected | To be run |
| TC11 | RLS | User accesses another user's rating | Access denied | To be run |
| TC12 | Cold start | New user with no ratings | Content-based recommendations returned | To be run |

## Table 4.7: Recommendation Evaluation Metrics

| Metric | Purpose | Result |
|---|---|---|
| Precision@K | Measures relevant items in the top K | To be measured |
| Recall@K | Measures relevant items retrieved in the top K | To be measured |
| MAP@K | Measures ranking quality across relevant items | To be measured |
| Coverage | Measures how much of the catalogue can be recommended | To be measured |
| Cold-start success | Confirms that recommendations are produced without prior ratings | To be measured |

## Table 4.8: Comparison with Existing System

| Criterion | Conventional approach | Proposed system |
|---|---|---|
| Personalisation | General/category ranking | Preferences + interactions |
| Content similarity | Manual inspection or opaque ranking | TF-IDF + cosine similarity |
| Collaborative signal | Varies | SVD when sufficient ratings exist |
| Cold start | Generic browsing | Onboarding preferences |
| Explanation | Often limited | Short grounded explanation |
| Interface | General-purpose | Designed for readability and clear controls |
| Movie data | Platform-specific | Cached external movie metadata + application data |
| AI assistance | Not necessarily available | DeepSeek used as an auxiliary layer |
