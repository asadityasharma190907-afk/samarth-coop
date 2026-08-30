---
title: "ARCHITECTURE-SPINE: Samarth"
status: final
created: 2026-08-29
updated: 2026-08-29
project: Samarth
altitude: Initiative
sources:
  - _bmad-output/planning-artifacts/prds/prd-Samarth-2026-08-29/prd.md
  - _bmad-output/planning-artifacts/ux-designs/ux-Samarth-2026-08-29/DESIGN.md
  - _bmad-output/planning-artifacts/ux-designs/ux-Samarth-2026-08-29/EXPERIENCE.md
---

# ARCHITECTURE-SPINE: Samarth

## Paradigm

**Layered REST API + SPA (client–server separation).** The backend is a stateless FastAPI service; the frontend is a React SPA. They communicate exclusively over HTTP/JSON. No server-side rendering, no GraphQL, no WebSockets for MVP.

**Guiding principle:** boring technology, verifiable by Swagger before any UI exists. Every architectural decision is judged against: *"Can the dispatch algorithm be demonstrated to work correctly in Swagger with seed data before a single React component is built?"*

---

## Architecture Decisions

### AD-1: Backend Framework — FastAPI (Python 3.11)
**Binds:** All server-side business logic is implemented in FastAPI. No Flask, Django, or Node.js backend.  
**Prevents:** Mixed backend runtimes; two team members choosing incompatible server frameworks.  
**Rule:** Every API endpoint is defined as a FastAPI route with Pydantic request/response models. Auto-generated OpenAPI spec is the primary integration contract.  
**[ADOPTED]** — selected in the Claude tech stack conversation; matches team's Python familiarity.

---

### AD-2: Database — PostgreSQL 15 + SQLAlchemy ORM
**Binds:** All persistent data lives in a single PostgreSQL 15 database. SQLAlchemy is the ORM. No ORMs mixed (no raw psycopg2 alongside SQLAlchemy, no Prisma).  
**Prevents:** Two engineers implementing the same entity with different ORMs/query patterns.  
**Rule:** Schema is managed via Alembic migrations. No hand-rolled DDL in application startup. Seed data via a dedicated `seed.py` script, not hardcoded in routes.  
**[ADOPTED]**

---

### AD-3: Frontend — React 18 + Vite
**Binds:** The SPA is built in React 18, bundled with Vite. No Next.js (SSR not needed for an SPA with JWT auth and no SEO requirements).  
**Prevents:** Team members using different bundlers or React versions.  
**Rule:** React Router v6 for client-side routing. No framework UI library (no MUI, shadcn) — custom components from `DESIGN.md` tokens. All design tokens are CSS custom properties defined in a single `tokens.css` imported globally.  
**[ADOPTED]**

---

### AD-4: Authentication — JWT (stateless)
**Binds:** Authentication is phone + password. The server issues a signed JWT (HS256). No sessions, no cookies for auth. Refresh tokens are deferred (V2).  
**Prevents:** Team mixing session-based and token-based auth.  
**Rule:** Every protected endpoint validates the JWT in the `Authorization: Bearer <token>` header. Role (`citizen` / `worker` / `admin`) is encoded in the JWT payload. Password hashing: bcrypt, cost factor 12.  
**[ADOPTED]**

---

### AD-5: Dispatch Score is Computed at Query Time — Never Stored as a Counter
**Binds:** `WeeklyEarnings` for any worker is always computed from the `bookings` table at the moment of the query, using `date_trunc('week', NOW())`. No `weekly_earnings` column exists on `worker_profiles`.  
**Prevents:** Two engineers — one implementing the dispatch scorer, one implementing the completion endpoint — independently deciding to cache earnings in `worker_profiles` (which would reintroduce the reset bug).  
**Rule:** `GET /workers` (and any internal function that computes Dispatch Score) must run a subquery against `bookings` for weekly earnings. Any PR that adds a `weekly_earnings` column to `worker_profiles` is a spec violation.  
**[ADOPTED]** — explicitly fixed from the Claude review session; this is a load-bearing architectural decision.

---

### AD-6: Offer Acceptance is Row-Locked
**Binds:** The accept path in `PUT /booking-offers/{id}` (action: accept) must open a database transaction and acquire a row-level lock on the `bookings` row before reading its status.  
**Prevents:** Two workers simultaneously accepting the same booking (race condition).  
**Rule:** Implementation: `db.query(Booking).filter_by(id=booking_id).with_for_update().first()`. Check `booking.status == 'pending'` inside the transaction. Return HTTP 409 if not. Any implementation that reads `booking.status` outside a transaction violates this AD.  
**[ADOPTED]**

---

### AD-7: Dispatch Score is Stored Immutably on Each Offer Row
**Binds:** When an offer row is created in `booking_offers`, the `dispatch_score` and `rank_at_offer` at that moment are written to the row and never updated.  
**Prevents:** Two engineers implementing the offer creation and the audit trail endpoint making different assumptions about whether scores are live-computed or stored.  
**Rule:** `booking_offers.dispatch_score` and `booking_offers.rank_at_offer` are written on `INSERT`. They are read-only after creation. The audit trail endpoint (`GET /booking-offers/booking/{id}`) reads these stored values — it does not recompute.  
**[ADOPTED]**

---

### AD-8: Offer Expiry is Lazy — No Background Scheduler
**Binds:** There is no Celery, no APScheduler, no cron job for offer expiry in MVP.  
**Prevents:** A teammate adding a background task runner that couples the system to a message broker (Redis, RabbitMQ) not in the stack.  
**Rule:** Every code path that reads or acts on an offer record first checks: `if now() > offer.expires_at and offer.status == 'offered': expire and cascade`. No scheduler is introduced unless explicitly approved as a V2 item.  
**[ADOPTED]**

---

### AD-9: Data Model — Four Core Tables
**Binds:** The canonical schema has exactly these four tables for MVP:
- `users` — all users (citizens + workers + admins), role-flagged
- `worker_profiles` — 1:1 with users where `role = 'worker'`; skill, location, rating, availability, verified
- `bookings` — service requests; snapshotted `job_price`, status lifecycle, `platform_fee` on completion
- `booking_offers` — cascade audit trail; FK to booking + worker; `dispatch_score`, `rank_at_offer`, `status`, `expires_at`

**Prevents:** A fifth table being added (e.g. `earnings`, `sessions`, `weekly_stats`) without a team decision logged in the memlog.  
**Rule:** Any new table requires a corresponding Alembic migration and a team decision (logged in the architecture memlog or a new AD). No implicit schema changes via ORM `create_all()`.

---

### AD-10: Local Development — Manual Setup (No Docker)
**Binds:** Local development uses a Python virtualenv for the backend and `npm run dev` for the frontend. PostgreSQL 15 is installed locally or via a free cloud provider (Neon.tech).
**Prevents:** Docker complexity causing onboarding friction for team members unfamiliar with containers.
**Rule:** Each developer runs backend and frontend as native processes. The canonical startup is: `cd backend && source venv/bin/activate && alembic upgrade head && uvicorn app.main:app --reload` and `cd frontend && npm run dev`. A `.env` file (not committed) holds `DATABASE_URL` and `SECRET_KEY`. `.env.example` is committed as the template. No Dockerfiles or docker-compose.yml.
**[UPDATED]** — Docker removed by team decision to reduce onboarding complexity for hackathon.

---

### AD-11: API Design — RESTful JSON, No Versioning for MVP
**Binds:** All endpoints follow REST conventions (nouns, HTTP verbs). JSON request/response only. No GraphQL, no gRPC.  
**Prevents:** Ad-hoc endpoint naming (e.g. `/doAccept`, `/getWorkerList`).  
**Rule:** Endpoint naming follows the patterns already defined in the PRD API surface. Any new endpoint must be proposed in the OpenAPI spec before implementation. No `/v1/` prefix for MVP — versioning is a V2 concern.

---

### AD-12: Frontend–Backend Contract — OpenAPI Spec is the Source of Truth
**Binds:** The FastAPI auto-generated OpenAPI spec (available at `/docs` and `/openapi.json`) is the integration contract between frontend and backend teams.  
**Prevents:** Frontend and backend drifting because each independently documented the API.  
**Rule:** Frontend team reads the spec, not the backend team's README. If a contract is wrong or missing, the fix is a new Pydantic model or route — not a note in Slack. The spec must be verifiable with seed data before any React component is written (this is a project milestone gate).

---

### AD-13: State Management — React Query (TanStack Query)
**Binds:** All async server state (API calls, loading states, caching) is managed via TanStack Query v5. No Redux, no Zustand, no Context API for server state.  
**Prevents:** Two frontend developers implementing data fetching with different patterns (one using `useEffect` + `useState`, another using a custom hook, another using Redux Thunk).  
**Rule:** Local UI state (modal open/closed, form values) uses `useState`. Server state uses TanStack Query. No mixing.

---

## Data Schema (Seed — owned by migrations)

```sql
-- users
CREATE TABLE users (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    phone       VARCHAR(15) UNIQUE NOT NULL,
    name        VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role        VARCHAR(20) NOT NULL CHECK (role IN ('citizen', 'worker', 'admin')),
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- worker_profiles
CREATE TABLE worker_profiles (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id       UUID UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    skill         VARCHAR(50) NOT NULL,
    lat           DECIMAL(9,6) NOT NULL,
    lng           DECIMAL(9,6) NOT NULL,
    rating        DECIMAL(2,1),           -- NULL = cold-start (treated as 4.0 in dispatch)
    availability  BOOLEAN DEFAULT TRUE,
    verified      BOOLEAN DEFAULT FALSE,
    created_at    TIMESTAMPTZ DEFAULT NOW()
);

-- bookings
CREATE TABLE bookings (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    citizen_id    UUID REFERENCES users(id),
    worker_id     UUID REFERENCES users(id),
    skill         VARCHAR(50) NOT NULL,
    lat           DECIMAL(9,6) NOT NULL,
    lng           DECIMAL(9,6) NOT NULL,
    description   TEXT,
    job_price     DECIMAL(10,2) NOT NULL,  -- snapshotted at creation
    platform_fee  DECIMAL(10,2),           -- set on completion (job_price * 0.05)
    status        VARCHAR(20) NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending','assigned','completed','cancelled')),
    created_at    TIMESTAMPTZ DEFAULT NOW()
);

-- booking_offers
CREATE TABLE booking_offers (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    booking_id      UUID REFERENCES bookings(id),
    worker_id       UUID REFERENCES users(id),
    rank_at_offer   INTEGER NOT NULL,
    dispatch_score  DECIMAL(12,2) NOT NULL,  -- immutable after INSERT (AD-7)
    status          VARCHAR(20) NOT NULL DEFAULT 'offered'
                      CHECK (status IN ('offered','accepted','declined','expired')),
    expires_at      TIMESTAMPTZ NOT NULL,    -- created_at + 2 minutes
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
```

---

## API Surface (Seed — owned by routes)

```
POST   /auth/register                      Register citizen or worker
POST   /auth/login                         Returns JWT

GET    /workers?skill=&lat=&lng=           Ranked worker list with dispatch scores (FR-4, FR-5)
POST   /bookings                           Create booking (FR-7)
PUT    /booking-offers/{id}               Accept or decline offer (FR-9, FR-10)
GET    /booking-offers/booking/{id}       Offer audit trail for a booking (FR-17)
PUT    /bookings/{id}/complete            Mark job complete (FR-12)
POST   /bookings/{id}/rating              Citizen submits rating (FR-16)
GET    /wallet/{worker_id}               Worker wallet view (FR-13)
GET    /welfare-fund/summary              CWF total (FR-14)

PATCH  /admin/workers/{id}/verify        Toggle verified flag (FR-15)
```

---

## Dependency Rules

```
┌────────────────────────────────────┐
│         React SPA (Frontend)       │  ← reads OpenAPI spec (AD-12)
│  components / pages / hooks        │  ← TanStack Query for server state (AD-13)
└───────────────┬────────────────────┘
                │ HTTP/JSON
┌───────────────▼────────────────────┐
│        FastAPI (Backend)            │  ← Python 3.11, async routes
│  routers / services / models        │  ← Pydantic for request/response
└───────────────┬────────────────────┘
                │ SQLAlchemy ORM
┌───────────────▼────────────────────┐
│        PostgreSQL 15                │  ← 4 tables (AD-9)
│        (local install or Neon.tech)  │  ← Alembic migrations (AD-2)
└────────────────────────────────────┘
```

**Dependency rules:**
- Frontend → Backend: HTTP only. No direct DB access from the frontend.
- Backend routes → Services: business logic lives in service modules, not in route handlers. Route handlers validate input (Pydantic) and call services.
- Services → DB: SQLAlchemy sessions. No raw SQL except for the dispatch score subquery (read-only, performance-critical — documented exception).
- No circular dependencies between routers.

---

## Directory Structure (Seed)

```
samarth/
├── backend/
│   ├── app/
│   │   ├── main.py                # FastAPI app init, CORS, router registration
│   │   ├── config.py              # Settings (env vars via pydantic-settings)
│   │   ├── database.py            # SQLAlchemy engine, session factory
│   │   ├── models/                # SQLAlchemy ORM models (users, worker_profiles, bookings, booking_offers)
│   │   ├── schemas/               # Pydantic request/response models
│   │   ├── routers/               # FastAPI routers (auth, workers, bookings, offers, wallet, admin)
│   │   ├── services/              # Business logic (dispatch.py, auth.py, booking.py, wallet.py)
│   │   └── seed.py                # Seed data script
│   ├── alembic/                   # Database migrations
│   ├── tests/                     # Pytest tests
│   ├── requirements.txt
│   └── .env.example               # Template: DATABASE_URL, SECRET_KEY, ALGORITHM, etc.
├── frontend/
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx                # Router, auth context
│   │   ├── tokens.css             # Design tokens (CSS custom properties from DESIGN.md)
│   │   ├── components/            # Shared components (Button, Card, Badge, OfferCard, WelfareFund)
│   │   ├── pages/                 # Route-level components (Login, Register, Dashboard, Book, Wallet...)
│   │   ├── hooks/                 # TanStack Query hooks (useWorkers, useBooking, useWallet...)
│   │   └── lib/                   # API client (api.ts — typed fetch wrappers over OpenAPI contract)
│   ├── index.html
│   ├── vite.config.ts
│   └── package.json
└── docs/                          # Planning artifacts (briefs, PRD, architecture, UX)
```

---

## Dispatch Score Function (Canonical Implementation)

This is the canonical Python implementation. Any deviation is a spec violation (AD-5, FR-5).

```python
# backend/app/services/dispatch.py

from decimal import Decimal
from math import radians, sin, cos, sqrt, atan2

def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlng = radians(lng2 - lng1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng/2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1-a))

def compute_dispatch_score(
    weekly_earnings: Decimal,
    rating: float | None,
    distance_km: float,
    reliability_penalty: bool
) -> Decimal:
    effective_rating = Decimal(str(rating)) if rating is not None else Decimal("4.0")
    penalty = Decimal("3000") if reliability_penalty else Decimal("0")
    return (
        (Decimal("5000") - weekly_earnings) * 2
        + Decimal("1000") * effective_rating
        - Decimal("500") * Decimal(str(distance_km))
        - penalty
    )
```

---

## Deferred (Will Not Decide Here)

| Concern | Why Deferred | When to Revisit |
|---|---|---|
| Production deployment target | Hackathon focus; Render/Railway/VPS all viable | Post-hackathon V1 launch |
| PostGIS spatial indexing | Haversine sufficient for ≤ 50 workers; PostGIS is a new infrastructure dependency | When city-scale rollout begins (> 1,000 workers) |
| JWT refresh tokens | Overkill for a 36h hackathon session | V2: add `refresh_tokens` table + `/auth/refresh` endpoint |
| WebSockets for real-time offer push | Nice-to-have; polling is sufficient for demo | V2: Socket.IO or SSE if worker app is production-grade |
| Dynamic pricing engine | New subsystem, not a column addition | Post-V1: separate `pricing_rules` service |
| Insurance integration | New subsystem | Post-V1 |
| Background task runner (Celery) | AD-8 rules it out; lazy expiry is sufficient | When offer volume makes lazy expiry a measurable bottleneck |
| Multilingual i18n | React-intl or i18next are trivial adds | V2: add when non-English cooperative base is onboarded |
| Native mobile app | PWA or React Native after V1 web is stable | V2 |

---

## Open Questions

None blocking. All load-bearing decisions are resolved.

---

## Milestone Gate

> **Before any React component is committed:** `GET /workers?skill=electrician&lat=26.9124&lng=75.7873` must return the four seed workers in the order Suresh (1) > Priya (2) > Anil (3) > Meena (4), verifiable in Swagger at `http://localhost:8000/docs`. This is the integration test that validates the entire architecture before the frontend exists.
