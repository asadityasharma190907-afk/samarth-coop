---
title: 'Story 1.1: Project Bootstrap & Docker Compose Setup'
type: 'chore'
created: '2026-08-30'
status: 'draft'
review_loop_iteration: 0
context:
  - _bmad-output/implementation-artifacts/epic-1-context.md
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** The project has no source code, no directory structure, and no runnable environment. Team members cannot start working because there is nothing to run or build on.

**Approach:** Create the canonical directory layout (AD-9), Docker Compose configuration, and minimal working FastAPI + React Vite skeletons so that `docker-compose up` brings the full stack online and all four database tables are created via Alembic migration. This is the unblocking story for all 26 stories that follow.

## Boundaries & Constraints

**Always:**
- Directory structure must exactly match AD-9 layout: `backend/app/{main.py, config.py, database.py, models/, schemas/, routers/, services/, seed.py}`, `backend/alembic/`, `backend/tests/`, `backend/Dockerfile`, `backend/requirements.txt`; `frontend/src/{main.tsx, App.tsx, tokens.css, components/, pages/, hooks/, lib/}`, `frontend/index.html`, `frontend/vite.config.ts`, `frontend/Dockerfile`, `frontend/package.json`; `docker-compose.yml` at root.
- Backend Docker entrypoint must run `alembic upgrade head` before `uvicorn` starts. Never use `Base.metadata.create_all()` anywhere.
- Exactly 4 tables created: `users`, `worker_profiles`, `bookings`, `booking_offers`. Schema from ARCHITECTURE-SPINE.md verbatim.
- SECRET_KEY and DATABASE_URL come from environment variables (`.env` file, not committed); `.env.example` is committed.
- FastAPI must have CORS configured for `http://localhost:3000`.
- All services must have hot-reload in dev: uvicorn --reload for backend, vite dev server for frontend.

**Ask First:**
- If a 5th table or additional top-level folder is needed for any technical reason.
- If the team wants to use a different Python package for JWT (default plan: python-jose + passlib[bcrypt]).

**Never:**
- `Base.metadata.create_all()` in any application startup path.
- Committing `.env` (only `.env.example`).
- Adding Celery, Redis, or any background task runner.
- Creating `weekly_earnings` column on `worker_profiles`.
- Using any UI framework (MUI, shadcn, Ant Design) in frontend scaffold.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Fresh clone, Docker running | `docker-compose up` | PostgreSQL on 5432, FastAPI on 8000 (`/docs` loads), React dev server on 3000 | Container logs show clear errors; backend waits for DB healthy before starting |
| Alembic migration | Backend starts | All 4 tables exist in DB | If migration fails, backend exits with non-zero code so compose fails visibly |
| DB not yet ready | Backend starts before postgres is healthy | Backend entrypoint waits/retries | Use `depends_on` with `condition: service_healthy` |
| FastAPI /docs | GET http://localhost:8000/docs | OpenAPI UI loads with 0 routes (placeholder) | N/A |
| React dev server | GET http://localhost:3000 | Vite default React page loads | N/A |

</frozen-after-approval>

## Code Map

This is a greenfield story — no existing source files. All paths below are to-be-created:

- `docker-compose.yml` (root) — orchestrates db, backend, frontend services
- `backend/Dockerfile` — Python 3.11 slim image; copies app; runs entrypoint.sh
- `backend/entrypoint.sh` — runs `alembic upgrade head` then `uvicorn app.main:app --reload`
- `backend/requirements.txt` — fastapi, uvicorn, sqlalchemy, alembic, psycopg2-binary, python-jose[cryptography], passlib[bcrypt], pydantic-settings
- `backend/app/main.py` — FastAPI() init, CORS middleware, router stubs
- `backend/app/config.py` — pydantic-settings BaseSettings reading DATABASE_URL, SECRET_KEY, etc.
- `backend/app/database.py` — SQLAlchemy engine + SessionLocal + Base
- `backend/app/models/__init__.py` — imports all models so Alembic autogenerate sees them
- `backend/app/models/user.py` — User ORM model
- `backend/app/models/worker_profile.py` — WorkerProfile ORM model
- `backend/app/models/booking.py` — Booking ORM model
- `backend/app/models/booking_offer.py` — BookingOffer ORM model
- `backend/alembic/` — `alembic init`-generated structure; `env.py` wired to app.database.Base
- `backend/alembic/versions/0001_initial_schema.py` — initial migration for all 4 tables
- `backend/tests/` — empty `__init__.py` placeholder
- `backend/app/schemas/` — empty `__init__.py`
- `backend/app/routers/` — empty `__init__.py`
- `backend/app/services/` — empty `__init__.py`
- `backend/app/seed.py` — placeholder (implemented in Story 2.1)
- `frontend/Dockerfile` — Node 20 alpine; installs deps; runs vite dev server
- `frontend/package.json` — react 18, react-dom, vite, @tanstack/react-query, react-router-dom
- `frontend/vite.config.ts` — minimal vite config, proxy `/api` to backend:8000
- `frontend/index.html` — HTML shell loading main.tsx
- `frontend/src/main.tsx` — ReactDOM.createRoot + QueryClientProvider
- `frontend/src/App.tsx` — placeholder root component
- `frontend/src/tokens.css` — empty for now (implemented in Story 1.2)
- `frontend/src/components/` — empty placeholder
- `frontend/src/pages/` — empty placeholder
- `frontend/src/hooks/` — empty placeholder
- `frontend/src/lib/` — empty placeholder (api.ts added in Story 1.3)
- `.env.example` — template with all required env vars

## Tasks & Acceptance

**Execution:**
- [ ] `docker-compose.yml` -- CREATE -- defines db (postgres:15 with healthcheck), backend (build ./backend, depends_on db healthy, ports 8000:8000, env_file .env), frontend (build ./frontend, depends_on backend, ports 3000:3000, volumes for hot-reload)
- [ ] `backend/Dockerfile` -- CREATE -- Python 3.11-slim, WORKDIR /app, copies requirements.txt + installs, copies app, exposes 8000, ENTRYPOINT ["/app/entrypoint.sh"]
- [ ] `backend/entrypoint.sh` -- CREATE -- `#!/bin/sh\nalembic upgrade head\nuvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`
- [ ] `backend/requirements.txt` -- CREATE -- fastapi>=0.111, uvicorn[standard], sqlalchemy>=2.0, alembic, psycopg2-binary, python-jose[cryptography], passlib[bcrypt], pydantic-settings, pytest, httpx
- [ ] `backend/app/config.py` -- CREATE -- pydantic BaseSettings with DATABASE_URL, SECRET_KEY, ALGORITHM="HS256", ACCESS_TOKEN_EXPIRE_MINUTES=60
- [ ] `backend/app/database.py` -- CREATE -- engine from DATABASE_URL, SessionLocal = sessionmaker, Base = declarative_base(), get_db dependency
- [ ] `backend/app/models/user.py` -- CREATE -- User ORM model matching schema in ARCHITECTURE-SPINE.md (id UUID, phone VARCHAR(15) UNIQUE, name, password_hash, role CHECK, created_at)
- [ ] `backend/app/models/worker_profile.py` -- CREATE -- WorkerProfile ORM model (id, user_id FK, skill, lat DECIMAL(9,6), lng DECIMAL(9,6), rating DECIMAL(2,1) nullable, availability BOOLEAN, verified BOOLEAN, created_at)
- [ ] `backend/app/models/booking.py` -- CREATE -- Booking ORM model (id, citizen_id FK, worker_id FK nullable, skill, lat, lng, description, job_price DECIMAL(10,2), platform_fee DECIMAL(10,2) nullable, status CHECK, created_at)
- [ ] `backend/app/models/booking_offer.py` -- CREATE -- BookingOffer ORM model (id, booking_id FK, worker_id FK, rank_at_offer INTEGER, dispatch_score DECIMAL(12,2), status CHECK, expires_at TIMESTAMPTZ, created_at)
- [ ] `backend/app/models/__init__.py` -- CREATE -- imports User, WorkerProfile, Booking, BookingOffer so Alembic autogenerate works
- [ ] `backend/app/main.py` -- CREATE -- FastAPI app, CORSMiddleware (allow_origins=["http://localhost:3000"]), include_router stubs (empty for now), health endpoint GET /health -> {"status": "ok"}
- [ ] `backend/alembic/env.py` -- CREATE via alembic init + modify -- import Base from app.database, set target_metadata = Base.metadata, use DATABASE_URL from env
- [ ] `backend/alembic/versions/0001_initial_schema.py` -- CREATE -- hand-written migration creating all 4 tables with exact DDL from ARCHITECTURE-SPINE.md (no autogenerate to avoid surprises)
- [ ] `frontend/Dockerfile` -- CREATE -- FROM node:20-alpine, WORKDIR /app, copies package*.json, npm install, copies src, EXPOSE 3000, CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
- [ ] `frontend/package.json` -- CREATE -- react@18, react-dom@18, @vitejs/plugin-react, vite@5, @tanstack/react-query@5, react-router-dom@6, typescript
- [ ] `frontend/vite.config.ts` -- CREATE -- @vitejs/plugin-react, server.proxy {'/api': 'http://backend:8000'}, server.host true
- [ ] `frontend/index.html` -- CREATE -- minimal HTML shell, script type=module src=/src/main.tsx
- [ ] `frontend/src/main.tsx` -- CREATE -- ReactDOM.createRoot, QueryClientProvider, renders <App />
- [ ] `frontend/src/App.tsx` -- CREATE -- placeholder: renders <h1>Samarth</h1>
- [ ] `frontend/src/tokens.css` -- CREATE -- empty file with comment "Design tokens — implemented in Story 1.2"
- [ ] `.env.example` -- CREATE -- DATABASE_URL=postgresql://samarth:samarth@db:5432/samarth, SECRET_KEY=change-me-in-production, ALGORITHM=HS256, ACCESS_TOKEN_EXPIRE_MINUTES=60, POSTGRES_USER=samarth, POSTGRES_PASSWORD=samarth, POSTGRES_DB=samarth
- [ ] `frontend/src/{components,pages,hooks,lib}/__init__` -- CREATE -- empty placeholder directories (use .gitkeep files)
- [ ] `backend/app/{schemas,routers,services}/__init__.py` -- CREATE -- empty placeholder __init__.py files
- [ ] `backend/tests/__init__.py` -- CREATE -- empty

**Acceptance Criteria:**
- Given the repo is cloned and Docker is running, when `docker-compose up` is run, then PostgreSQL starts on port 5432, FastAPI starts on port 8000 (`GET /health` returns `{"status": "ok"}`), and the React dev server starts on port 3000.
- Given the backend starts, when FastAPI initialises, then all four tables (users, worker_profiles, bookings, booking_offers) exist in the database (verified by `docker-compose exec db psql -U samarth -d samarth -c "\dt"`).
- Given the directory structure specification in ARCHITECTURE-SPINE.md, when the repo is initialised, then `backend/` and `frontend/` are structured exactly as specified in AD-9; no extra folders at the top level.
- Given `GET http://localhost:8000/docs`, then the FastAPI OpenAPI UI loads successfully.
- Given `GET http://localhost:3000`, then the Vite React dev server returns the app page.
- Given no `.env` file exists in the repo, then `.env.example` contains all required variable names with placeholder values.

## Design Notes

Alembic `env.py` pattern — import models explicitly before autogenerate so all models are registered:
```python
from app.models import user, worker_profile, booking, booking_offer  # noqa: F401
from app.database import Base
target_metadata = Base.metadata
```

Backend Docker healthcheck pattern to avoid race with postgres:
```yaml
db:
  image: postgres:15
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U samarth"]
    interval: 5s
    timeout: 5s
    retries: 10
backend:
  depends_on:
    db:
      condition: service_healthy
```

## Verification

**Commands:**
- `docker-compose up --build -d` -- expected: all 3 containers running, exit code 0
- `docker-compose exec db psql -U samarth -d samarth -c "\dt"` -- expected: 4 rows (bookings, booking_offers, users, worker_profiles)
- `curl http://localhost:8000/health` -- expected: `{"status":"ok"}`
- `curl http://localhost:8000/docs` -- expected: HTTP 200
- `curl http://localhost:3000` -- expected: HTTP 200

**Manual checks (if no CLI):**
- Open http://localhost:8000/docs in browser — FastAPI Swagger UI renders.
- Open http://localhost:3000 in browser — Vite React app renders "Samarth" heading.
