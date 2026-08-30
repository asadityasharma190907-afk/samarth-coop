# Epic 1 Context: Project Foundation & Authentication

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Bootstrap a fully runnable local development environment and implement authentication for both user roles (citizen and worker). When this epic is done, any team member can clone the repo, activate the backend venv, run Alembic migrations, start uvicorn + npm dev server, and be ready for Epic 2 backend work. The design token system must also be in place so frontend work in later epics starts from a consistent visual foundation.

## Stories

- Story 1.1: Project Bootstrap & Manual Dev Setup
- Story 1.2: Design Token System (CSS Custom Properties)
- Story 1.3: Citizen Registration API
- Story 1.4: Worker Registration API
- Story 1.5: Login API (Both Roles)
- Story 1.6: Citizen Registration & Login UI
- Story 1.7: Worker Registration & Login UI

## Requirements & Constraints

- Running `alembic upgrade head` then `uvicorn app.main:app --reload` starts the backend on port 8000. `npm run dev` starts the frontend on port 3000. PostgreSQL runs locally or via Neon.tech.
- Backend startup runs `alembic upgrade head` — never `Base.metadata.create_all()` in any production code path.
- Schema has exactly 4 tables: `users`, `worker_profiles`, `bookings`, `booking_offers`. No extras.
- Passwords stored with bcrypt cost factor 12. Never logged or returned in any response.
- All auth uses JWT (HS256) in `Authorization: Bearer` header. No session cookies.
- JWT payload must contain `user_id`, `role`, and `name`.
- Allowed roles: `citizen`, `worker`, `admin`.
- Worker skill must be from a fixed list of 10 categories (validation -> HTTP 422 on unknown).
- Directory structure must exactly match AD-9 layout; no extra top-level folders.
- All design tokens in `frontend/src/tokens.css` as CSS custom properties. No hardcoded hex in any component CSS file. Inter font loaded from Google Fonts.
- WCAG 2.1 AA contrast >= 4.5:1 for all text/background combinations.

## Technical Decisions

- Backend: FastAPI (Python 3.11) + SQLAlchemy ORM + Alembic migrations + PostgreSQL 15.
- Frontend: React 18 + Vite. TanStack Query v5 for server state. No UI framework (no MUI, shadcn).
- Auth: JWT HS256 issued by backend. passlib[bcrypt] for hashing.
- Each service runs natively: PostgreSQL locally or Neon.tech, backend in a Python venv, frontend via npm.
- `alembic upgrade head` must be run manually whenever schema changes are made (before starting uvicorn).
- Environment variables: DATABASE_URL, SECRET_KEY, ALGORITHM=HS256, ACCESS_TOKEN_EXPIRE_MINUTES.
- CORS: Backend must allow http://localhost:3000 origin.
- Backend layout: backend/app/{main.py, config.py, database.py, models/, schemas/, routers/, services/, seed.py}, backend/alembic/, backend/tests/, backend/requirements.txt, backend/.env.example.
- Frontend layout: frontend/src/{main.tsx, App.tsx, tokens.css, components/, pages/, hooks/, lib/}, frontend/index.html, frontend/vite.config.ts, frontend/package.json.

## UX & Interaction Patterns

- Color palette: brand-primary #1A6B47, brand-accent #F4A623, surface-bg #F8FAF9.
- Typography: Inter (Google Fonts) primary, JetBrains Mono for numeric data.
- Mobile role selector: two full-width tap-target cards (Citizen / Worker).
- Worker registration: skill-category chip group (10 chips) + location input.
- Navigation: bottom tab bar on mobile; 240px sidebar on desktop (>=1024px).
- Failed login: inline error below form, no modal, no page reload.

## Cross-Story Dependencies

- Story 1.1 (Manual Setup) must complete before any other story can be tested locally.
- Stories 1.3-1.5 (backend APIs) must complete before Stories 1.6-1.7 (UI) can be integrated.
- Story 1.2 (tokens.css) should complete alongside 1.1 for frontend developers.
- Epic 2 cannot begin until this entire epic is done and the environment is stable.

