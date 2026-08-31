# Samarth — Cooperative Gig Services Platform

> **SIH Problem #26089** | Ministry of Cooperation / NCCT  
> A fairness-weighted dispatch algorithm for cooperative workers. The closest, best-rated worker doesn't always win — the one who needs work most does.

---

## What is Samarth?

Citizens book a cooperative worker (electrician, plumber, etc.). Samarth ranks available workers by a **dispatch score** — not just by distance or rating, but also by how much they've earned this week. Workers who haven't earned much this week rank higher. This ensures fair income distribution across the cooperative.

**The demo proof point:** Meena Verma is closest and best-rated. She ranks last. Suresh Kumar, who has barely earned this week, ranks first. The math is visible in the audit trail.

---

## Team Setup (Manual Dev Setup — Local PostgreSQL)

### Step 0: Install PostgreSQL 15 & Create Database (One-time setup per machine)
Install PostgreSQL 15: [https://www.postgresql.org/download/](https://www.postgresql.org/download/)  
Create the local database in terminal or pgAdmin:
```sql
CREATE USER samarth WITH PASSWORD 'samarth';
CREATE DATABASE samarth OWNER samarth;
```

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

# 3. Copy .env template & run migrations
copy .env.example .env    # Windows
# cp .env.example .env    # Mac/Linux

alembic upgrade head

# 4. Seed test data (first run only)
python app/seed.py

# 5. Start the server
uvicorn app.main:app --reload --port 8000
# Health check: http://localhost:8000/health
# API docs: http://localhost:8000/docs
```

### Frontend (React + Vite)

```bash
cd frontend

# 1. Install dependencies
npm install

# 2. Start the dev server
npm run dev
# App running at: http://localhost:3000

# 3. Run Formatting & Linting
npm run format
npm run lint:es

# 4. Run Unit Tests (Vitest)
npm run test
```

### Run Backend Tests & Linting

```bash
cd backend
pytest
ruff check .
ruff format --check .
```

### Run Local QA Checks (Pre-push)

To prevent failing CI builds, run the QA check script locally before pushing:

```powershell
# Run checks (Ruff, Pyright, Pytest, TSC)
.\qa_check.ps1

# Auto-fix linting/formatting errors
.\qa_check.ps1 -Fix
```

**Git Hook setup (For all team members)**: 
We have automated this check so it runs before every `git push`. Because git hooks are not tracked by default, **every teammate must run this command once** after pulling this code:

```bash
git config core.hooksPath .githooks
```
Once run, your pushes will automatically be blocked if QA checks fail locally.

### Run Frontend Linting & Build

```bash
cd frontend
npm run lint
npm run build
```

---

## Deployment & CI

- **Backend & Frontend CI:** Automatically run tests, linting, and builds via GitHub Actions on PRs and pushes to `master`, `main`, and `develop`.
- **Render Production Deploy:** The deploy workflow triggers via Render Deploy Hook. Add `RENDER_DEPLOY_HOOK_URL` in repository **Settings > Secrets and variables > Actions**. If not configured, the workflow gracefully skips without failing.

---

## Project Structure

```
samarth/
├── backend/
│   ├── app/
│   │   ├── main.py          ← FastAPI app entry point (health & CORS)
│   │   ├── database.py      ← Database connection & session factory
│   │   ├── config.py        ← Pydantic settings
│   │   ├── models/          ← SQLAlchemy ORM models (users, worker_profiles, bookings, booking_offers)
│   │   ├── schemas/         ← Pydantic request/response models
│   │   ├── routers/         ← API route handlers
│   │   ├── services/        ← Business logic (dispatch.py lives here)
│   │   └── seed.py          ← Test data seeder
│   ├── tests/               ← pytest tests
│   ├── alembic/             ← Database migrations (0001_initial_schema.py)
│   ├── .env.example         ← Environment variable template
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── tokens.css       ← Design tokens (all colors, fonts, spacing)
│   │   ├── components/      ← Shared UI components
│   │   ├── pages/           ← Page-level components
│   │   ├── hooks/           ← TanStack Query data hooks
│   │   └── lib/api.ts       ← Typed API client
│   ├── index.html
│   ├── vite.config.ts
│   └── package.json
└── AGENTS.md                ← Instructions for AI coding assistants
```

---

## Key Rules (All Team Members Read This)

1. **Never store `weekly_earnings`** on `worker_profiles`. Always compute from `bookings` table.
2. **Always use a row lock** (`with_for_update()`) when accepting a booking offer.
3. **`dispatch_score` on an offer is write-once.** Never update it after INSERT.
4. **No background jobs** (no Celery). Offer expiry is checked lazily on each request.
5. **No hardcoded hex colors** in CSS. Use design tokens from `frontend/src/tokens.css`.
6. **No UI library** (no MUI, shadcn). Build components from the design tokens.
