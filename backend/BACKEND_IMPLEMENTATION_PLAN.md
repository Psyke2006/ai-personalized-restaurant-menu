# Backend Implementation Plan

Work in small phases. Complete and verify one phase before starting the next.

## Phase 0 — Audit and contract

- [ ] Inspect repository tree and current backend code.
- [ ] Read root `API.md`, `ARCHITECTURE.md`, `README.md`, `CONTRIBUTING.md`, `OWNERS.md`.
- [ ] Identify current dependency manager and test setup.
- [ ] Compare actual endpoint implementation to API documentation.
- [ ] Resolve the folder-layout mismatch without unnecessary restructuring.
- [ ] Write down API contract gaps and agree them with frontend owner.

## Phase 1 — API and persistence foundation

- [ ] Ensure FastAPI app starts.
- [ ] Ensure router prefix/base URL matches `/api/v1`.
- [ ] Implement health endpoint.
- [ ] Configure environment settings and CORS.
- [ ] Establish SQLAlchemy database connection and models.
- [ ] Persist and retrieve user profiles.
- [ ] Persist menus and dishes with stable IDs.
- [ ] Implement structured errors.
- [ ] Verify `/docs` and OpenAPI schemas.

## Phase 2 — Manual menu ingestion

- [ ] Validate manual menu payload.
- [ ] Validate prices and spice levels.
- [ ] Persist restaurant/menu/dishes transactionally.
- [ ] Return menu ID and stable dish IDs/records needed by frontend.
- [ ] Keep API response compatible with canonical documentation or coordinate an additive change.
- [ ] Add unit and API tests.

## Phase 3 — Upload and extraction

- [ ] Validate file type, size, and empty files.
- [ ] Extract text from PDF with PyMuPDF.
- [ ] Run OCR for scanned content where configured.
- [ ] Integrate Gemini only for schema-constrained normalization if configured.
- [ ] Validate normalized results with Pydantic.
- [ ] Persist extracted dishes and return stable IDs.
- [ ] Handle low-confidence/missing ingredients with warnings.
- [ ] Test provider failure, invalid output, empty extraction, and malformed file.

## Phase 4 — Recommendation pipeline

- [ ] Implement normalized ingredient/allergen matching.
- [ ] Apply allergy and strict dietary filters before scoring.
- [ ] Represent missing safety metadata as uncertainty.
- [ ] Implement documented weighted baseline.
- [ ] Derive explanation reasons from actual rule signals.
- [ ] Sort deterministically.
- [ ] Return recommendations, filtered dishes, and complete-menu information.
- [ ] Add edge-case tests and fixed examples.

## Phase 5 — Feedback

- [ ] Validate user/dish references and rating 1–5.
- [ ] Persist feedback.
- [ ] Return documented response.
- [ ] Make feedback available to the scoring component only through an explicit, tested rule.
- [ ] Do not claim the system learns a model unless model training is implemented.

## Phase 6 — Frontend integration

- [ ] Run frontend and backend locally together.
- [ ] Verify every endpoint from the browser origin.
- [ ] Confirm CORS and multipart upload behavior.
- [ ] Confirm exact request/response schemas with frontend owner.
- [ ] Confirm complete menu remains accessible after ranking.
- [ ] Test no recommendations, all dishes filtered, and incomplete ingredient metadata.

## Phase 7 — Final verification

- [ ] Run pytest and existing lint/type checks.
- [ ] Run API integration tests against a test database.
- [ ] Verify no secrets or local data are committed.
- [ ] Update API docs if contract changes were approved.
- [ ] Report commands, real results, and remaining limitations.

Do not mark features complete solely because code was generated. A feature is complete when tests or a documented manual verification actually pass.
