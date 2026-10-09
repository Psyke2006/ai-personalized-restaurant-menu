# Backend Architecture Guide

## Principle

Use a small, understandable layered FastAPI backend. Route handlers should not contain the recommendation algorithm, OCR pipeline, or raw SQL logic. Follow the actual repository structure; this document defines responsibilities, not a mandate to move files.

## Repository documentation mismatch to resolve

The root `README.md` describes modules such as `backend/api/`, `backend/database/`, `backend/models/`, `backend/schemas/`, `backend/recommender/`, and `backend/menu_processing/`. The root `ARCHITECTURE.md` describes `backend/app/recommender/`. Before coding, inspect the actual tree and select the existing layout as the source of truth. Update documentation with the team if needed. Do not duplicate packages or relocate working code without a migration plan.

## Logical layers

### API/router layer

Responsibilities:
- Define versioned endpoints.
- Validate inputs using Pydantic request schemas.
- Call service functions.
- Translate known domain errors to HTTP errors.
- Return response models matching `API.md`.

Keep route functions thin.

### Schemas

Define request/response types for:
- User profile create/read
- Dish input/read
- Manual menu input/result
- Upload result
- Recommendation result and dish statuses
- Feedback input/result
- Standard error envelope

Use explicit constraints: budget >= 0, spice level 1–5, rating 1–5, bounded upload size, valid list/string values. Do not silently coerce invalid payloads into plausible values.

### Database/models/repositories

Persist:
- User profiles and preference arrays/relations
- Menus/restaurants
- Dishes with stable IDs and a parent menu ID
- Feedback linked to user and dish

Use the existing SQLAlchemy conventions. Use migrations if already configured; if no migration tooling exists, propose a minimal migration approach before introducing it. Add indexes/constraints where useful. Avoid storing the same dish independently in ways that break its menu identity.

### Menu processing

Suggested responsibilities:
1. Validate upload and file type.
2. Extract PDF text with PyMuPDF.
3. Run OCR for scanned PDFs/images using the configured OCR dependency.
4. Normalize extracted text to structured fields.
5. Optionally call Gemini for parsing/normalization.
6. Validate model output against a schema.
7. Persist menu and dish records with stable IDs.
8. Return extracted records and warnings.

Do not couple OCR to recommendation ranking. A menu should be parsed once, stored, and then ranked for different profiles.

### Recommendation engine

Keep pure logic testable without database or network:
- `filtering`: deterministic hard constraints and uncertainty flags.
- `scoring`: weighted preference scoring.
- `recommender`: orchestration and stable sorting.
- `explanations`: reasons derived from the same score/filter signals, if this separation is useful.

Pipeline:
1. Validate/load profile and menu.
2. Apply hard allergy and strict diet filters.
3. Keep flagged dishes in output with reasons.
4. Score only eligible dishes.
5. Sort by score with deterministic tie-breaker.
6. Return recommendations and enough information to preserve the entire menu.

Weights from `ARCHITECTURE.md`:
- Cuisine: 0.20
- Ingredient preference: 0.20
- Diet compatibility: 0.20
- Budget: 0.15
- Spice tolerance: 0.10
- Health goal: 0.10
- Historical feedback: 0.05

Weights sum to 1.0. Handle missing values consistently and test the boundaries. Do not invent nutritional values. If feedback is absent, document whether that component contributes zero or is renormalized; choose and test one behavior.

### Configuration

Load from environment:
- `DATABASE_URL`
- `GEMINI_API_KEY` (only if Gemini processing is enabled)
- CORS allowed origins
- upload size/type limits
- other settings only when required

Keep `.env` out of version control. `.env.example` contains placeholder values only. Avoid logging raw API keys, uploaded documents, or full user allergy profiles.

## Gemini boundary

Gemini is for parsing/normalizing menu text and optionally wording explanations from known facts. It must not:
- decide whether a dish is safe for an allergy,
- perform the final hard filter,
- generate match scores,
- invent ingredients/nutrition facts as confirmed facts,
- bypass schema validation.

Prompt output is untrusted. Validate JSON, reject malformed fields, handle timeouts/rate limits, and provide useful errors. The application should fail gracefully if Gemini is unavailable; whether menu ingestion can fall back to text-only/manual mode should be explicit.

## Stable API contract

Use root `API.md` as canonical. Do not rename endpoints, request fields, response fields, or status values without coordinating with the frontend owner. Resolve the documented gaps around stable dish IDs, manual-menu response contents, complete-menu access, status values, and ID format before final integration.

## Observability and security

- Structured logs for route failures and processing stages.
- No secret logging.
- Validate upload size, file type, and file content where practical.
- Use temporary files safely and clean them up.
- Avoid returning internal exceptions to clients.
- Configure CORS for the frontend origin.
- Set database transactions so partially persisted menus do not leave inconsistent records.
- Use timeouts for external API calls.
