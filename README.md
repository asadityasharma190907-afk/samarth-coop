# Samarth — Cooperative Gig Services Platform

> **SIH Problem #26089** | Ministry of Cooperation / NCCT  
> A fairness-weighted dispatch algorithm for cooperative workers. The closest, best-rated worker doesn't always win — the one who needs work most does.

---

## What is Samarth?

Citizens book a cooperative worker (electrician, plumber, etc.). Samarth ranks available workers by a **dispatch score** — not just by distance or rating, but also by how much they've earned this week. Workers who haven't earned much this week rank higher. This ensures fair income distribution across the cooperative.

**The demo proof point:** Meena Verma is closest and best-rated. She ranks last. Suresh Kumar, who has barely earned this week, ranks first. The math is visible in the audit trail.

---

## Team Setup (No Docker Required)

### Backend (FastAPI + Python)

```bash
cd backend

# 1. Create a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up the database (SQLite for local dev — zero install!)
cp .env.example .env
alembic upgrade head

# 4. Seed test data
python app/seed.py

# 5. Start the server
uvicorn app.main:app --reload
# API docs: http://localhost:8000/docs
```

### Frontend (React + Vite)

```bash
cd frontend

# 1. Install dependencies
npm install

# 2. Start the dev server
npm run dev
# App: http://localhost:5173
```

### Run Backend Tests

```bash
cd backend
pytest
```

---

## Project Structure

```
samarth/
├── backend/
│   ├── app/
│   │   ├── main.py          ← FastAPI app entry point
│   │   ├── database.py      ← Database connection
│   │   ├── models/          ← SQLAlchemy ORM models
│   │   ├── schemas/         ← Pydantic request/response models
│   │   ├── routers/         ← API route handlers
│   │   ├── services/        ← Business logic (dispatch.py lives here)
│   │   └── seed.py          ← Test data seeder
│   ├── tests/               ← pytest tests
│   ├── alembic/             ← Database migrations
│   ├── .env.example         ← Environment variable template
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── tokens.css       ← Design tokens (all colors, fonts, spacing)
│   │   ├── components/      ← Shared UI components
│   │   ├── pages/           ← Page-level components
│   │   ├── hooks/           ← TanStack Query data hooks
│   │   └── lib/api.ts       ← Typed API client
│   └── package.json
├── .github/workflows/       ← CI/CD (GitHub Actions)
├── docs/                    ← Setup guides and architecture notes
└── AGENTS.md                ← Instructions for AI coding assistants
```

---

## Dispatch Algorithm

```
Score = (5000 − WeeklyEarnings) × 2
      + (1000 × Rating)        ← null rating defaults to 4.0
      − (500 × Distance_km)    ← Haversine, max 5km radius
      − ReliabilityPenalty     ← 3000 points if acceptance rate < 50% (after 5+ offers)
```

**Seed data expected ranking:**

| Worker | Weekly Earnings | Rating | Distance | Score |
|---|---|---|---|---|
| Suresh Kumar | ₹200 | 4.2 | 2.5 km | ~12,550 |
| Priya Gupta | ₹0 | 4.0 (default) | 4.0 km | ~12,000 |
| Anil Yadav | ₹2,000 | 4.5 | 1.5 km | ~9,750 |
| Meena Verma | ₹4,500 | 4.9 | 0.3 km | ~5,750 |

---

## Key Rules (All Team Members Read This)

1. **Never store `weekly_earnings`** on `worker_profiles`. Always compute from `bookings` table.
2. **Always use a row lock** (`with_for_update()`) when accepting a booking offer.
3. **`dispatch_score` on an offer is write-once.** Never update it after INSERT.
4. **No background jobs** (no Celery). Offer expiry is checked lazily on each request.
5. **No hardcoded hex colors** in CSS. Use design tokens from `frontend/src/tokens.css`.
6. **No UI library** (no MUI, shadcn). Build components from the design tokens.

---

## Links

- [Planning docs](./_bmad-output/planning-artifacts/)
- [All issues](https://github.com/asadityasharma190907-afk/samarth-coop/issues)
- [Sprint status](./_bmad-output/implementation-artifacts/sprint-status.yaml)
- [Architecture decisions](./_bmad-output/planning-artifacts/architecture/architecture-Samarth-2026-08-29/ARCHITECTURE-SPINE.md)
