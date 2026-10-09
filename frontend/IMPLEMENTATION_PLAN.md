# Frontend Implementation Plan

Implement in small increments. Do not attempt a large one-shot rewrite.

## Phase 0 — Audit

- [ ] Read root `API.md`, `ARCHITECTURE.md`, `README.md`, `CONTRIBUTING.md`, and `OWNERS.md`.
- [ ] Inspect current frontend tree and package scripts.
- [ ] Identify Next.js version, App Router/pages structure, Tailwind version, lint/typecheck/build commands.
- [ ] Report API contract questions before coding.
- [ ] Keep changes inside `frontend/` unless approved.

## Phase 1 — Foundation

- [ ] Preserve existing scaffold.
- [ ] Establish page layout and reusable UI primitives using existing dependencies.
- [ ] Add centralized environment-based API client.
- [ ] Add API TypeScript types.
- [ ] Add shared loading, error, empty, and status components.
- [ ] Verify app starts and builds.

## Phase 2 — Preferences

- [ ] Build profile form with fields from `API_INTEGRATION.md`.
- [ ] Add validation and accessible field errors.
- [ ] POST to `/users/profile`.
- [ ] Keep returned `id` as an opaque string.
- [ ] Support fetching a profile by ID if the UI has a known ID.
- [ ] Handle API failure without losing entered values.

## Phase 3 — Menu ingestion

- [ ] Build manual dish-entry UI.
- [ ] POST structured menu to `/menu/manual`.
- [ ] Build PDF/image upload UI.
- [ ] POST `FormData` to `/menu/upload` without manually setting multipart content type.
- [ ] Store returned menu ID and dish records in application state.
- [ ] Render the full returned menu before recommendations are requested.

## Phase 4 — Recommendation display

- [ ] POST `{ user_id, menu_id }` to `/recommendations/rank`.
- [ ] Display recommended dishes with backend scores/reasons.
- [ ] Display filtered dishes with explicit exclusion reasons.
- [ ] Preserve complete menu access by merging ranking data with the original menu using stable IDs.
- [ ] If the backend response lacks the records/IDs required to show the complete menu, document the blocker and ask the backend owner to resolve it. Do not invent identifiers.
- [ ] Show clear states for no recommendations and backend errors.

## Phase 5 — Feedback

- [ ] Add like/dislike and rating controls.
- [ ] POST to `/feedback`.
- [ ] Show confirmed success only after a successful response.
- [ ] Prevent duplicate in-flight submissions.

## Phase 6 — Verification

- [ ] Run the existing lint command.
- [ ] Run TypeScript typecheck if configured.
- [ ] Run the production build.
- [ ] Test the UI with the backend running.
- [ ] Test backend unavailable, invalid inputs, empty menu, upload failure, no compatible dishes, and malformed error response.
- [ ] Check mobile layout and keyboard navigation.
- [ ] Check that filtered dishes are still visible with warnings.
- [ ] Summarize actual results and remaining limitations.

## Definition of done

A phase is done only when its acceptance checks pass. Do not claim API integration is complete if it was tested only with mock data. Clearly label any mock/demo mode.
