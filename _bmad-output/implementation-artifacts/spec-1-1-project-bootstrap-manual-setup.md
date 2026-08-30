---
title: 'Story 1.1: Project Bootstrap & Manual Dev Setup (Local PostgreSQL)'
type: 'chore'
created: '2026-08-31'
status: 'done'
review_loop_iteration: 0
context:
  - _bmad-output/implementation-artifacts/epic-1-context.md
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** The project has no source code or runnable environment. Team members cannot start development because backend, database, and frontend skeletons do not exist.

**Approach:** Set up the full local development environment so every team member can clone the repo and run the stack locally — PostgreSQL database, backend FastAPI API with Alembic migrations creating 4 core tables, and React Vite frontend.

## Boundaries & Constraints

**Always:**
- Directory structure must match AD-9 layout: `backend/app/{main.py, config.py, database.py, models/, schemas/, routers/, services/}`, `backend/alembic/`, `backend/tests/`, `backend/requirements.txt`, `backend/.env.example`; `frontend/src/{main.tsx, App.tsx, tokens.css, components/, pages/, hooks/, lib/}`, `frontend/index.html`, `frontend/vite.config.ts`, `frontend/package.json`.
- Tables created ONLY by Alembic migrations (`alembic upgrade head`). Never use `Base.metadata.create_all()` in any backend execution path.
- Exactly 4 tables created: `users`, `worker_profiles`, `bookings`, `booking_offers`. Schema matching ARCHITECTURE-SPINE.md verbatim.
- `.env` must NOT be committed — only `.env.example` with pre-filled default local connection string (`postgresql://samarth:samarth@localhost:5432/samarth`).
- FastAPI must have CORS enabled for `http://localhost:3000`.

**Ask First:**
- If any 5th database table or extra top-level folder is needed.

**Never:**
- Using `Base.metadata.create_all()`.
- Committing `.env` file.
- Adding Celery, Redis, or background schedulers.
- Creating a `weekly_earnings` column on `worker_profiles`.
- Using external UI frameworks (MUI, shadcn, Ant Design).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Health check | `GET /health` | `{"status": "ok"}` | 500 error if backend misconfigured |
| Docs UI | `GET /docs` | Swagger UI rendered | HTTP 404 if docs disabled |
| Database migration | `alembic upgrade head` | 4 tables created in local DB | Alembic error output |
| React dev server | `GET http://localhost:3000` | Vite React app loads | Console error |

</frozen-after-approval>

## Code Map

- `backend/requirements.txt` -- Python dependencies (fastapi, uvicorn, sqlalchemy, alembic, psycopg2-binary, python-jose, passlib, pydantic-settings, pytest, httpx)
- `backend/.env.example` -- Pre-filled default environment variables
- `backend/app/config.py` -- Pydantic BaseSettings loading env vars
- `backend/app/database.py` -- SQLAlchemy engine, SessionLocal, Base, get_db dependency
- `backend/app/main.py` -- FastAPI application with CORS and GET /health
- `backend/app/models/user.py` -- User ORM model
- `backend/app/models/worker_profile.py` -- WorkerProfile ORM model
- `backend/app/models/booking.py` -- Booking ORM model
- `backend/app/models/booking_offer.py` -- BookingOffer ORM model
- `backend/app/models/__init__.py` -- Model exports for Alembic
- `backend/alembic/env.py` -- Alembic environment configuration
- `backend/alembic/versions/0001_initial_schema.py` -- Initial migration creating all 4 tables
- `frontend/package.json` -- Frontend dependencies (react, react-dom, vite, @tanstack/react-query, react-router-dom)
- `frontend/vite.config.ts` -- Vite configuration with proxy to http://localhost:8000
- `frontend/index.html` -- HTML shell
- `frontend/src/main.tsx` -- React entrypoint with QueryClientProvider
- `frontend/src/App.tsx` -- Initial root component
- `README.md` -- Manual setup instructions for developers

## Tasks & Acceptance

**Execution:**
- [x] `backend/requirements.txt` -- CREATE -- Python dependencies list
- [x] `backend/.env.example` -- CREATE -- Pre-filled environment template
- [x] `backend/app/config.py` -- CREATE -- Pydantic Settings class
- [x] `backend/app/database.py` -- CREATE -- DB engine, sessionmaker, Base
- [x] `backend/app/models/user.py` -- CREATE -- User model (id, phone, name, password_hash, role, created_at)
- [x] `backend/app/models/worker_profile.py` -- CREATE -- WorkerProfile model (id, user_id, skill, lat, lng, rating, availability, verified, created_at)
- [x] `backend/app/models/booking.py` -- CREATE -- Booking model (id, citizen_id, worker_id, skill, lat, lng, description, job_price, platform_fee, status, created_at)
- [x] `backend/app/models/booking_offer.py` -- CREATE -- BookingOffer model (id, booking_id, worker_id, rank_at_offer, dispatch_score, status, expires_at, created_at)
- [x] `backend/app/models/__init__.py` -- CREATE -- Exports all 4 models
- [x] `backend/app/main.py` -- CREATE -- FastAPI app with CORSMiddleware and GET /health
- [x] `backend/alembic/env.py` & `backend/alembic/script.py.mako` -- CREATE -- Alembic environment setup
- [x] `backend/alembic/versions/0001_initial_schema.py` -- CREATE -- Alembic migration for 4 tables
- [x] `frontend/package.json` -- CREATE -- React 18 & Vite setup
- [x] `frontend/vite.config.ts` -- CREATE -- Vite config
- [x] `frontend/index.html` -- CREATE -- HTML entry shell
- [x] `frontend/src/main.tsx` -- CREATE -- React root setup
- [x] `frontend/src/App.tsx` -- CREATE -- React root component
- [x] `frontend/src/tokens.css` -- CREATE -- Design token placeholder
- [x] `README.md` -- UPDATE/CREATE -- Local setup instructions for team members

**Acceptance Criteria:**
- Given the backend virtual environment is active, when `alembic upgrade head` is executed, then all 4 tables (`users`, `worker_profiles`, `bookings`, `booking_offers`) are created in PostgreSQL without errors.
- Given the FastAPI dev server is running on port 8000, when `GET /health` is requested, then response is `{"status": "ok"}`.
- Given the FastAPI dev server is running on port 8000, when `GET /docs` is requested in browser, Swagger UI loads.
- Given `frontend/`, when `npm run dev` is executed, React dev server starts on port 3000.

## Verification

**Commands:**
- `alembic upgrade head` (from backend directory) -- expected: migration 0001 applies cleanly
- `uvicorn app.main:app --port 8000` -- expected: server starts on 8000
- `curl http://localhost:8000/health` -- expected: `{"status": "ok"}`
- `npm run dev` (from frontend directory) -- expected: Vite server starts on 3000
