# CONTRIBUTING GUIDELINES & GIT WORKFLOW

Welcome to the **AI-Powered Personalized Restaurant Menu** project. Please follow these guidelines to maintain high code quality and smooth team collaboration.

---

## 🌿 Git Branching Strategy

We use short-lived feature branches targeting the `main` branch:

```text
main
 ├── feature/backend-user-profile
 ├── feature/frontend-menu-ui
 └── feature/menu-ocr-extraction
```

### Branch Naming Conventions
- `feature/<module>-<short-description>` (e.g., `feature/backend-scoring-rules`)
- `fix/<module>-<short-description>` (e.g., `fix/recommender-allergy-filter`)
- `docs/<short-description>` (e.g., `docs/update-api-spec`)

---

## 📝 Commit Conventions

Make small, incremental commits with descriptive imperative messages:

- `feat: add hard allergy filtering logic`
- `feat: add user preference creation API`
- `fix: correct case-insensitive allergen matching`
- `test: add unit tests for weighted scoring engine`
- `docs: update system flow in ARCHITECTURE.md`

---

## 🔄 Pull Request Guidelines

1. Create a Pull Request from your feature branch to `main`.
2. Fill out the PR template (`.github/pull_request_template.md`).
3. Ensure all tests in `tests/` pass before requesting review.
4. Obtain approval from the designated module owner (`OWNERS.md`).
