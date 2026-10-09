# Backend AI Coding Instructions

These files guide AI-assisted development of the FastAPI backend for the AI-Powered Personalized Restaurant Menu PBL.

## Read in order

1. `AI_BACKEND_MASTER_PROMPT.md` — primary prompt for Codex/Antigravity.
2. `BACKEND_API_CONTRACT.md` — requirements to preserve compatibility with the root `API.md` and frontend.
3. `BACKEND_ARCHITECTURE_GUIDE.md` — architecture and module boundaries.
4. `BACKEND_IMPLEMENTATION_PLAN.md` — incremental implementation sequence.
5. `BACKEND_TESTING_CHECKLIST.md` — safety, API, and integration tests.

## Canonical documents

The root `API.md` is the canonical HTTP contract. `ARCHITECTURE.md` is the canonical high-level system design. Do not silently create competing versions or change their public contract. If implementation reveals a necessary correction, propose the change, update the root document with the team, and notify the frontend developer.

## Before coding

Inspect the actual repository tree, `backend/`, `tests/`, dependency files, `.env.example`, root `API.md`, root `ARCHITECTURE.md`, `README.md`, `CONTRIBUTING.md`, and `OWNERS.md`. Some existing documentation describes different backend subfolder layouts. Preserve the existing working structure and reconcile the docs rather than moving files blindly.
