# AI-Powered Personalized Restaurant Menu

> **Enhancing dining experiences through explainable, constraint-aware recommendation without hiding the restaurant's original menu.**

---

## 📌 Project Overview

The **AI-Powered Personalized Restaurant Menu** is a college PBL (Project-Based Learning) project designed to transform traditional static restaurant menus into personalized, dynamic dining guides.

Instead of generic food recommendation apps that suggest random restaurants, this system takes a specific restaurant's existing menu and tailors its presentation for an individual diner based on their unique profile, safety constraints, and taste preferences.

---

## 🎯 Key Product Principle

> **Never hide or replace the restaurant's full menu.**

Personalization **enhances** the menu rather than restricting it. Users can easily discover their best matching dishes while retaining full access to the complete menu, alongside transparent safety compatibility flags and explainable scoring details.

---

## 🚀 Core Features

1. **Safety & Dietary Hard Filtering**: Strictly excludes dishes containing user allergens (e.g., peanuts, shellfish) or violating strict diets (e.g., Vegetarian, Vegan, Jain, Halal).
2. **Deterministic Rule-Based Ranking**: Scores compatible dishes using a weighted preference algorithm (Cuisine, Ingredients, Spice Tolerance, Budget, Health Goals, Past Ratings).
3. **Transparent Match Scores**: Calculates human-readable, deterministic match scores (e.g., `91% Match`).
4. **Explainable Recommendations**: Breaks down exactly *why* a dish is recommended with verifiable rule-based match bullets.
5. **Multi-Input Menu Ingestion**: Supports manual menu entry, PDF documents (PyMuPDF), scanned images (OCR), and QR link access.
6. **AI-Assisted Semantic Normalization**: Employs Google Gemini API strictly for parsing messy menu text and enriching dish metadata—never for black-box recommendation or safety filtering.
7. **Feedback & Learning Loop**: Collects user interactions (Likes, Dislikes, 1–5 star ratings) to refine future recommendations.

---

## 🏗 System Architecture & Flow

```text
Restaurant Menu (PDF / Image / QR / Manual)
                    │
                    ▼
          Menu Ingestion Pipeline
         (PyMuPDF + OCR + Gemini)
                    │
                    ▼
          Structured Dish Objects
                    │
                    ▼
       Hard Constraint Filtering (Safety)
   ┌────────────────┼────────────────┐
   │ Allergic /     │ Compatible     │
   ▼ Incompatible   ▼ Dishes         ▼
[FILTERED LIST]               Deterministic Weighted
(Shown with reason)            Scoring Model (0-100%)
                                     │
                                     ▼
                           Ranked Recommendations
                           (Score + Explanations)
                                     │
                                     ▼
                            User Feedback Loop
                         (Likes, Dislikes, Ratings)
```

---

## 🛠 Tech Stack

| Component | Technology | Rationale |
|---|---|---|
| **Frontend** | Next.js (TypeScript), Tailwind CSS | Clean, responsive UI for displaying ranked menu sections |
| **Backend** | Python, FastAPI | High-performance async APIs, strong ML/NLP ecosystem |
| **Database** | PostgreSQL + SQLAlchemy | Relational storage for users, menus, dishes, and feedback |
| **ML & Scoring** | NumPy, pandas, scikit-learn | Fast, deterministic rule-based vector & matrix operations |
| **Menu Ingestion**| PyMuPDF, Tesseract OCR, Gemini API | PDF extraction, image OCR, and semantic schema normalization |

---

## 👥 Team & Responsibilities

- **Laksh**: Backend & Recommendation Engine (`FastAPI`, PostgreSQL, Filtering, Weighted Scoring)
- **Pragya**: Frontend (`Next.js`, Tailwind CSS, User Profile UI, Menu & Recommendation UI)
- **Tanishkk**: AI & Menu Ingestion (`PyMuPDF`, OCR, Gemini Extraction, Datasets, Testing)

---

## 📂 Repository Structure

```text
ai-personalized-restaurant-menu/
├── .github/
│   └── pull_request_template.md  # Standard PR template
├── frontend/                     # Next.js frontend application
├── backend/                      # FastAPI backend application
│   ├── api/                      # REST endpoints & router setup
│   ├── database/                 # DB connections & ORM models
│   ├── models/                   # Pydantic core models
│   ├── schemas/                  # API request/response schemas
│   ├── recommender/              # Hard filtering & scoring pipeline
│   └── menu_processing/          # PDF, OCR, and Gemini parsers
├── tests/                        # Unit and integration test suites
├── data/                         # Seed menu datasets & mock profiles
├── README.md                     # Project Overview & setup
├── ARCHITECTURE.md               # In-depth architectural specification
├── API.md                        # API Endpoints & schema specification
├── OWNERS.md                     # Code ownership & module assignments
└── CONTRIBUTING.md               # Git workflow & coding rules
```

---

## 📜 License & Acknowledgments

Built as a 2-semester college PBL project.
