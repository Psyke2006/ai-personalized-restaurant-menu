# REPOSITORY CODE OWNERSHIP & MODULE ASSIGNMENTS

> **Strict responsibility boundaries to prevent code overlap during development.**

---

## 👥 Team Roles & Assigned Directory Ownership

### 1. Backend & Recommendation Subsystem
- **Lead**: Laksh
- **Assigned Directories**:
  - `backend/api/` (FastAPI REST endpoints and routers)
  - `backend/database/` (PostgreSQL connection and SQLAlchemy ORM models)
  - `backend/models/` (Core domain objects)
  - `backend/schemas/` (Pydantic validation schemas)
  - `backend/recommender/` (Hard filtering & weighted recommendation engine)

### 2. Frontend Subsystem
- **Lead**: Pragya
- **Assigned Directories**:
  - `frontend/` (Next.js application, TypeScript components, Tailwind CSS styling)

### 3. AI, Menu Ingestion & Quality Assurance
- **Lead**: Tanishkk
- **Assigned Directories**:
  - `backend/menu_processing/` (PyMuPDF parser, OCR pipeline, Gemini normalization)
  - `data/` (Seed menus and mock user profile datasets)
  - `tests/` (Unit and integration test suites)

---

## 🛡 Code Ownership Rules

1. **Scope Integrity**: Members must work strictly within their assigned module directories unless cross-module changes are coordinated via Pull Request reviews.
2. **Pull Requests**: All feature branches must be merged into `main` via PRs reviewed by the relevant code owner.
3. **PBL Viva Readiness**: Every team member must understand how their component integrates into the complete end-to-end system flow.
