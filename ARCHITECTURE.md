# SYSTEM ARCHITECTURE SPECIFICATION

## 1. Executive Summary & Design Core

The **AI-Powered Personalized Restaurant Menu** system is engineered around a strict separation of concerns between **Deterministic Hard Constraints** (safety and dietary enforcement) and **Weighted Soft Preferences** (personalization scoring).

### Core Architectural Principle
> **Never hide or replace the restaurant's full menu.**

The system operates as an **enhancement layer** over any input menu. Dishes that violate safety constraints are **not hidden**; instead, they are placed in a flagged compatibility state with explicit reasons (e.g., `"Incompatible: Contains peanuts (User Allergen)"`), ensuring total transparency for the diner.

---

## 2. End-to-End Core System Flow

```text
               +-----------------------------------+
               |  Restaurant Menu Input            |
               |  (PDF / Scanned Image / Manual /  |
               |   QR Code Endpoint)               |
               +-----------------------------------+
                                 │
                                 ▼
               +-----------------------------------+
               |  Menu Processing & Ingestion      |
               |  - PyMuPDF (PDF text extraction)  |
               |  - Tesseract / EasyOCR (Images)   |
               |  - Gemini API (Normalization)     |
               +-----------------------------------+
                                 │
                                 ▼
               +-----------------------------------+
               |  Structured Dish Objects (JSON)   |
               |  (Ingredients, Diet, Spice, etc.) |
               +-----------------------------------+
                                 │
                                 ▼
               +-----------------------------------+
               |  User Profile Context             |
               |  (Allergies, Diets, Budget, etc.) |
               +-----------------------------------+
                                 │
                                 ▼
               +-----------------------------------+
               |  Phase 1: Hard Constraint Filter  |
               |  Excludes dishes matching:        |
               |  - User Allergies                 |
               |  - Strict Dietary Exclusions      |
               +-----------------------------------+
                   │                           │
         Violates  │                           │  Compatible
        Constraint │                           │  Dishes
                   ▼                           ▼
       +-----------------------+   +------------------------------------+
       | Flagged Dish List     |   | Phase 2: V1 Weighted Recommender   |
       | (Displayed with       |   | Evaluates:                         |
       |  exclusion rationale) |   | - Cuisine Match       (20%)        |
       +-----------------------+   | - Ingredient Match    (20%)        |
                                   | - Diet Match          (20%)        |
                                   | - Budget Match        (15%)        |
                                   | - Spice Tolerance     (10%)        |
                                   | - Health Goal Match   (10%)        |
                                   | - Historical Feedback (5%)        |
                                   +------------------------------------+
                                               │
                                               ▼
                                   +------------------------------------+
                                   | Ranked Recommendation Output       |
                                   | - Match Score percentage (0-100%)  |
                                   | - Deterministic Bullet Reasons     |
                                   | - Categorized Menu Presentation    |
                                   +------------------------------------+
                                               │
                                               ▼
                                   +------------------------------------+
                                   | User Interaction & Feedback Loop   |
                                   | (Likes, Dislikes, 1-5 Star Ratings)|
                                   +------------------------------------+
```

---

## 3. Recommender Subsystem Architecture

The recommendation engine is located in `backend/app/recommender/` and follows a 3-stage pipeline:

```text
backend/app/recommender/
├── filtering.py       # Hard constraint filtering (allergies, diets)
├── scoring.py         # Configurable weighted preference scoring
└── recommender.py     # Pipeline orchestrator & ranking sorter
```

### Stage 1: Hard Constraint Filtering (`filtering.py`)
Dishes are evaluated against user safety rules **before** any preference scoring occurs.
- **Allergy Check**: Case-insensitive substring and semantic match between `user.allergies` and `dish.ingredients`.
- **Dietary Exclusions**: Enforces strict dietary boundaries (e.g., if `user.diet == "vegetarian"`, dishes tagged as `non-vegetarian` are flagged as incompatible).
- **Output**: `(compatible_dishes, filtered_dishes)` tuple.

> ⚠️ **Safety Notice**: All warning labels specify: *"No matching allergen was detected in menu metadata. Please verify ingredients with staff for severe allergies."*

### Stage 2: Weighted Preference Scoring (`scoring.py`)
Each compatible dish is scored between `0.0` and `1.0` (scaled to `0% - 100%`) using configurable weighting parameters:

$$\text{Score} = \sum_{k} w_k \cdot S_k$$

| Factor ($k$) | Weight ($w_k$) | Evaluation Criteria |
|---|---|---|
| **Cuisine Preference** | `0.20` (20%) | $1.0$ if dish cuisine matches user favorited cuisines, else $0.0$. |
| **Ingredient Preference** | `0.20` (20%) | Ratio of dish ingredients present in `user.favorite_ingredients`. |
| **Diet Compatibility** | `0.20` (20%) | Perfect match score for aligned dietary attributes. |
| **Budget Match** | `0.15` (15%) | $1.0$ if `dish.price <= user.budget`, decaying score if price exceeds budget. |
| **Spice Tolerance** | `0.10` (10%) | $1.0 - |dish.spice\_level - user.spice\_tolerance| / 5$. |
| **Health Goal Match** | `0.10` (10%) | Overlap ratio between `dish.health_tags` and `user.health_goal`. |
| **Historical Feedback** | `0.05` (5%) | Score boost for positive prior ratings, penalty for prior dislikes. |

*Note: All weights are fully configurable in `backend/app/recommender/scoring.py`.*

---

## 4. Database Schema (PostgreSQL / SQLAlchemy)

The database schema manages user profiles, menu items, and interaction records.

```text
 +-----------------------+        +--------------------------+
 | users                 |        | dietary_preferences      |
 +-----------------------+        +--------------------------+
 | id (PK, UUID)         |───<    | id (PK)                  |
 | name (VARCHAR)        |        | user_id (FK -> users.id) |
 | budget (NUMERIC)      |        | diet (VARCHAR)           |
 | spice_tolerance (INT) |        +--------------------------+
 | health_goal (VARCHAR) |
 | created_at (TIMESTAMP)|        +--------------------------+
 +-----------------------+        | allergies                |
             │                    +--------------------------+
             │                    | id (PK)                  |
             │───<                | user_id (FK -> users.id) |
             │                    | allergen (VARCHAR)       |
             │                    +--------------------------+
             │
             │                    +--------------------------+
             │                    | favorite_cuisines        |
             │                    +--------------------------+
             │───<                | id (PK)                  |
             │                    | user_id (FK -> users.id) |
             │                    | cuisine (VARCHAR)        |
             │                    +--------------------------+
             │
             │                    +--------------------------+
             │                    | favorite_ingredients     |
             │                    +--------------------------+
             │───<                | id (PK)                  |
                                  | user_id (FK -> users.id) |
                                  | ingredient (VARCHAR)     |
                                  +--------------------------+

 +-------------------------+      +--------------------------+
 | dishes                  |      | feedback                 |
 +-------------------------+      +--------------------------+
 | id (PK, UUID)           |      | id (PK, UUID)            |
 | name (VARCHAR)          |───<  | user_id (FK -> users.id) |
 | description (TEXT)      |      | dish_id (FK -> dishes.id)|
 | price (NUMERIC)         |      | liked (BOOLEAN)          |
 | cuisine (VARCHAR)       |      | rating (INT, 1-5)        |
 | ingredients (JSONB)     |      | created_at (TIMESTAMP)   |
 | diet_type (VARCHAR)     |      +--------------------------+
 | spice_level (INT)       |
 | health_tags (JSONB)     |
 +-------------------------+
```

---

## 5. Role & Boundary of Google Gemini API

Google Gemini API is integrated **strictly for ingestion and explanation tasks**:

### ✅ Allowed Gemini Tasks
1. **Menu Structuring**: Converting unstructured OCR text or PDF layouts into JSON dish schema (`name`, `price`, `ingredients`, `diet_type`, `spice_level`, `health_tags`).
2. **Metadata Enrichment**: Inferring likely ingredient lists or health tags when raw menu items lack detail.
3. **Natural Language Explanations**: Transforming deterministic scoring rules into human-readable match summaries.

### ❌ Prohibited Gemini Tasks
1. **No Black-Box Ranking**: Gemini does not decide which dish is recommended.
2. **No Hard Filtering**: Gemini does not serve as the primary safety/allergy gatekeeper.
3. **No Fake Scores**: Gemini does not generate or invent match percentages.

---

## 6. Development Strategy & Evolution

### Phase 1 (MVP - Days 1 & 2)
- Rule-based weighted scoring engine.
- Deterministic allergy & dietary exclusion filters.
- Pre-seeded & manual JSON menu ingestion.
- Next.js responsive presentation cards & feedback persistence.

### Phase 2 (Future Research Roadmap)
- Content-based vector similarity matching using TF-IDF / Scikit-Learn.
- `pgvector` integration for semantic dish embeddings.
- ML classification models (Logistic Regression / Random Forest) trained on user feedback data.
- Formal offline evaluation (Precision@K, Recall@K, F1@K, MAP@K, NDCG@K).
