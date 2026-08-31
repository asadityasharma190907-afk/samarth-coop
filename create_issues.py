#!/usr/bin/env python3
"""
Create all 26 GitHub issues for Samarth repo using gh CLI.
Run from the repo root: python create_issues.py
"""

import subprocess
import time

REPO = "asadityasharma190907-afk/samarth-coop"

issues = [
    # ─── EPIC 1 ───────────────────────────────────────────────────────────
    {
        "title": "[1.1] Project Bootstrap & Docker Compose Setup",
        "body": """## Story 1.1: Project Bootstrap & Docker Compose Setup

**Epic:** Epic 1 — Project Foundation & Authentication
**FRs:** ARCH-3 | **Type:** infra

**As a** developer,
**I want** a single `docker-compose up` command to start the full local dev environment (PostgreSQL, FastAPI, React),
**So that** every team member has a consistent, reproducible environment from day one.

## Acceptance Criteria

**Given** the repo is cloned and Docker is running
**When** `docker-compose up` is run
**Then** PostgreSQL starts on port 5432, FastAPI starts on port 8000 (`/docs` loads), and the React dev server starts on port 3000

**Given** the backend starts
**When** FastAPI initialises
**Then** all four tables (users, worker_profiles, bookings, booking_offers) are created via Alembic (`alembic upgrade head`)

**Given** the directory structure from ARCHITECTURE-SPINE.md AD-9
**When** the repo is initialised
**Then** `backend/` and `frontend/` are structured exactly as specified

## References
- AD-2 (Alembic), AD-9 (directory layout), AD-10 (Docker Compose only for local dev)
- Sprint key: `1-1-project-bootstrap-docker-compose`""",
        "labels": ["epic-1", "infra", "p0-must-have"],
    },
    {
        "title": "[1.2] Design Token System (CSS Custom Properties)",
        "body": """## Story 1.2: Design Token System

**Epic:** Epic 1 — Project Foundation & Authentication
**FRs:** UX-DR1 | **Type:** frontend

**As a** frontend developer,
**I want** a `tokens.css` file with all Samarth design tokens as CSS custom properties,
**So that** every UI component uses a single source of truth for colors, typography, spacing.

## Acceptance Criteria

**Given** the DESIGN.md token tables
**When** `tokens.css` is imported globally
**Then** all tokens are available as `--color-brand-primary`, `--font-sans`, `--spacing-md`, `--rounded-xl`, etc.

**Given** Inter font specified in DESIGN.md
**When** the app loads
**Then** Inter is loaded from Google Fonts and applied via `{typography.font-sans}`

**Given** the token file exists
**When** a developer adds a new component
**Then** they reference only tokens — no hardcoded hex values in component CSS

## References
- DESIGN.md: full color, typography, spacing, rounded token tables
- AD-3: No UI framework; all tokens in `frontend/src/tokens.css`
- Sprint key: `1-2-design-token-system`""",
        "labels": ["epic-1", "frontend", "p0-must-have"],
    },
    {
        "title": "[1.3] Citizen Registration API",
        "body": """## Story 1.3: Citizen Registration API

**Epic:** Epic 1 | **FR:** FR-1 | **Type:** backend

**As a** citizen,
**I want** to register with my name, phone number, and a password,
**So that** I can access the Samarth platform.

## Acceptance Criteria

**Given** a valid payload (`name`, `phone`, `password`, `role: citizen`)
**When** `POST /auth/register` is called
**Then** HTTP 201 + JWT; a `users` row with `role: citizen` is created; password stored hashed (bcrypt, cost 12)

**Given** a duplicate phone number
**When** `POST /auth/register` is called
**Then** HTTP 409 Conflict

**Given** any registration request
**When** the password is stored
**Then** plain-text password never appears in the database, logs, or API response

## References
- PRD FR-1, NFR-5 (bcrypt cost 12)
- AD-4 (JWT/bcrypt auth)
- Sprint key: `1-3-citizen-registration-api`""",
        "labels": ["epic-1", "backend", "p0-must-have"],
    },
    {
        "title": "[1.4] Worker Registration API",
        "body": """## Story 1.4: Worker Registration API

**Epic:** Epic 1 | **FR:** FR-2 | **Type:** backend

**As a** cooperative worker,
**I want** to register with my name, phone, skill category, and location,
**So that** I can receive job offers from Samarth.

## Acceptance Criteria

**Given** a valid payload (`name`, `phone`, `password`, `role: worker`, `skill`, `lat`, `lng`)
**When** `POST /auth/register` is called
**Then** HTTP 201; `users` row with `role: worker` + `worker_profiles` row created; `verified: false`, `availability: true`, `rating: null`

**Given** an invalid skill category (not in the allowed list of 10)
**When** `POST /auth/register` is called
**Then** HTTP 422 validation error

## Allowed skills: electrician, plumber, carpenter, painter, domestic helper, caregiver, driver, gardener, cleaner, technician

## References
- PRD FR-2, AD-4, AD-9 (schema)
- Sprint key: `1-4-worker-registration-api`""",
        "labels": ["epic-1", "backend", "p0-must-have"],
    },
    {
        "title": "[1.5] Login API (Both Roles)",
        "body": """## Story 1.5: Login API

**Epic:** Epic 1 | **FR:** FR-3 | **Type:** backend

**As a** citizen or worker,
**I want** to log in with my phone number and password,
**So that** I can access my role-specific dashboard.

## Acceptance Criteria

**Given** a registered user's phone and correct password
**When** `POST /auth/login` is called
**Then** HTTP 200 + signed JWT; payload includes `user_id`, `role`, and `name`

**Given** an incorrect password or unregistered phone
**When** `POST /auth/login` is called
**Then** HTTP 401 Unauthorized

## References
- PRD FR-3, AD-4 (JWT HS256, no session cookies)
- Sprint key: `1-5-login-api`""",
        "labels": ["epic-1", "backend", "p0-must-have"],
    },
    {
        "title": "[1.6] Citizen Registration & Login UI",
        "body": """## Story 1.6: Citizen Registration & Login UI

**Epic:** Epic 1 | **FRs:** FR-1, FR-3 | **UX-DRs:** UX-DR7 | **Type:** frontend

**As a** citizen,
**I want** to register and log in via the Samarth web app,
**So that** I can reach my dashboard without using Swagger.

## Acceptance Criteria

**Given** the user visits `/register` and selects "Citizen" role
**When** they fill in name, phone, password and submit
**Then** API called, JWT stored, user redirected to `/dashboard`

**Given** a registered citizen visits `/login`
**When** they enter correct credentials
**Then** redirected to `/dashboard`

**Given** a failed login (wrong credentials)
**When** the form is submitted
**Then** inline error message below the form (not a modal); no page reload

**Given** mobile viewport (375px)
**When** the registration form renders
**Then** role selector shows as two full-width tap-target cards (Citizen / Worker)

## References
- EXPERIENCE.md: Authentication Forms, Role selector pattern
- AD-13 (TanStack Query for all API calls)
- Sprint key: `1-6-citizen-registration-login-ui`""",
        "labels": ["epic-1", "frontend", "p0-must-have"],
    },
    {
        "title": "[1.7] Worker Registration & Login UI",
        "body": """## Story 1.7: Worker Registration & Login UI

**Epic:** Epic 1 | **FRs:** FR-2, FR-3 | **UX-DRs:** UX-DR7 | **Type:** frontend

**As a** cooperative worker,
**I want** to register and log in via the Samarth web app with my skill and location,
**So that** I can start receiving job offers.

## Acceptance Criteria

**Given** the user selects "Worker" during registration
**When** the form renders
**Then** a skill-category chip group (all 10 categories, horizontal) and a location input (Leaflet map pin + lat/lng fallback) are shown

**Given** the worker submits valid registration
**When** the API returns 201
**Then** JWT stored and user redirected to `/worker/dashboard`

**Given** the worker dashboard loads
**When** the worker is authenticated
**Then** the bottom tab bar (Home, Offers, Wallet, Profile) is visible on mobile

## References
- EXPERIENCE.md: Worker registration form, bottom tab bar (UX-DR7)
- AD-13 (TanStack Query)
- Sprint key: `1-7-worker-registration-login-ui`""",
        "labels": ["epic-1", "frontend", "p0-must-have"],
    },

    # ─── EPIC 2 ───────────────────────────────────────────────────────────
    {
        "title": "[2.1] Seed Data Script",
        "body": """## Story 2.1: Seed Data Script

**Epic:** Epic 2 — Dispatch Algorithm (Milestone Gate)
**FRs:** ARCH-4 | **Type:** backend

**As a** developer demonstrating the platform,
**I want** a `seed.py` script that populates deterministic test data,
**So that** the dispatch ranking can be validated in Swagger before any UI is built.

## Acceptance Criteria

**Given** the database is empty
**When** `python backend/app/seed.py` is run
**Then** 2 citizen users + 4 worker users created with specific Appendix A values

**Given** the seed script runs
**When** workers are created
**Then** each worker has: `skill: electrician`, `verified: true`, `availability: true`, correct rating and lat/lng per Appendix A of PRD

**Given** seed data is loaded
**When** `GET /workers?skill=electrician&lat=26.9124&lng=75.7873` is called
**Then** Suresh (score ~12550, rank 1) > Priya (~12000, rank 2) > Anil (~9750, rank 3) > Meena (~5750, rank 4)

## Seed Values (from PRD Appendix A)
| Worker | Weekly Earnings | Rating | Distance |
|---|---|---|---|
| Suresh Kumar | ₹200 | 4.2 | 2.5 km |
| Priya Gupta | ₹0 (new) | null → 4.0 | 4.0 km |
| Anil Yadav | ₹2,000 | 4.5 | 1.5 km |
| Meena Verma | ₹4,500 | 4.9 | 0.3 km |

## References
- PRD Appendix A, AD-5 (no weekly_earnings column)
- Sprint key: `2-1-seed-data-script`""",
        "labels": ["epic-2", "backend", "p0-must-have"],
    },
    {
        "title": "[2.2] WeeklyEarnings Subquery (Dispatch Core)",
        "body": """## Story 2.2: WeeklyEarnings Subquery

**Epic:** Epic 2 — Dispatch Algorithm | **FRs:** FR-5, AD-5 | **Type:** backend

⚠️ **CRITICAL AD-5 RULE: No `weekly_earnings` column on `worker_profiles`. This is computed at query time ONLY.**

**As a** backend developer,
**I want** a function that computes a worker's weekly earnings at query time from the `bookings` table,
**So that** the dispatch score resets automatically each Monday with no stored counter.

## Acceptance Criteria

**Given** a worker with completed bookings in the current ISO week
**When** `compute_weekly_earnings(worker_id, db)` is called
**Then** returns sum of `job_price * 0.95` for all `bookings` where `status = 'completed'` AND `created_at >= date_trunc('week', NOW())`

**Given** a new worker with no bookings this week
**When** `compute_weekly_earnings` is called
**Then** returns `Decimal('0')`

**Given** current day is Monday 00:01 UTC
**When** `compute_weekly_earnings` is called
**Then** returns 0 even if worker had ₹5000 in bookings last week

**And** no `weekly_earnings` column exists on `worker_profiles` — function queries `bookings` only

## SQL Pattern
```sql
SELECT COALESCE(SUM(job_price * 0.95), 0)
FROM bookings
WHERE worker_id = :worker_id
  AND status = 'completed'
  AND created_at >= date_trunc('week', NOW());
```

## References
- PRD FR-5, NFR-1, AD-5 (load-bearing)
- AGENTS.md pitfall: use `date_trunc('week', NOW())` not `datetime.now()`
- Sprint key: `2-2-weekly-earnings-subquery`""",
        "labels": ["epic-2", "backend", "p0-must-have"],
    },
    {
        "title": "[2.3] Reliability Penalty Computation",
        "body": """## Story 2.3: Reliability Penalty Computation

**Epic:** Epic 2 — Dispatch Algorithm | **FRs:** FR-5, FR-6 | **Type:** backend

**As a** backend developer,
**I want** a function that checks a worker's recent offer acceptance rate,
**So that** the dispatch algorithm cannot be gamed by declining all offers.

## Acceptance Criteria

**Given** a worker with ≥ 5 total offers, < 50% accepted in last 10
**When** `compute_reliability_penalty(worker_id, db)` is called
**Then** returns `True` (penalty of 3000 points applies)

**Given** a worker with < 5 total offers (grace period)
**When** `compute_reliability_penalty` is called
**Then** returns `False` regardless of acceptance rate

**Given** a worker with ≥ 5 offers and ≥ 50% acceptance rate in last 10
**When** `compute_reliability_penalty` is called
**Then** returns `False`

## SQL Pattern
```sql
SELECT COUNT(*) FILTER (WHERE status = 'accepted') AS accepted, COUNT(*) AS total
FROM (SELECT status FROM booking_offers WHERE worker_id = :worker_id ORDER BY created_at DESC LIMIT 10) recent;
-- penalty = True if total >= 5 AND accepted/total < 0.5
```

## References
- PRD FR-5 (ReliabilityPenalty), FR-6 (flag in response)
- Sprint key: `2-3-reliability-penalty-computation`""",
        "labels": ["epic-2", "backend", "p0-must-have"],
    },
    {
        "title": "[2.4] 🚦 Dispatch Score Endpoint (GET /workers) — MILESTONE GATE",
        "body": """## Story 2.4: Dispatch Score Endpoint — MILESTONE GATE

**Epic:** Epic 2 — Dispatch Algorithm | **FRs:** FR-4, FR-5, FR-6 | **Type:** backend

🚦 **MILESTONE GATE: This story must pass before ANY React component is committed (Epic 3).**

**As a** citizen or developer,
**I want** `GET /workers?skill=&lat=&lng=` to return eligible workers ranked by dispatch score,
**So that** the fairness algorithm is verifiable in Swagger before the frontend exists.

## Acceptance Criteria

**Given** seed data loaded and Appendix A request (skill=electrician, lat=26.9124, lng=75.7873)
**When** `GET /workers?skill=electrician&lat=26.9124&lng=75.7873` is called
**Then** response: 4 workers ordered Suresh (rank 1, ~12550) > Priya (rank 2, ~12000) > Anil (rank 3, ~9750) > Meena (rank 4, ~5750)
**And** each row includes: `dispatch_score`, `weekly_earnings`, `rating_is_default`, `reliability_penalty_applied`

**Given** a worker with `verified: false`
**When** `GET /workers` is called
**Then** that worker does not appear

**Given** a worker > 5km from request location
**When** `GET /workers` is called
**Then** that worker does not appear

**Given** a worker with `rating: null` (cold-start)
**When** their score is computed
**Then** `rating_is_default: true` in response; effective rating used = `4.0`

## Dispatch Formula (canonical — see dispatch.py)
```
Score = (5000 − WeeklyEarnings) × 2 + (1000 × Rating) − (500 × Distance_km) − ReliabilityPenalty
```

## Verify Gate
```bash
docker-compose up db backend
curl "http://localhost:8000/workers?skill=electrician&lat=26.9124&lng=75.7873"
# Expected: Suresh > Priya > Anil > Meena
```

## References
- PRD FR-4, FR-5, FR-6, Appendix A
- ARCHITECTURE-SPINE.md: Dispatch Score Function (canonical Python implementation)
- Sprint key: `2-4-dispatch-score-endpoint`""",
        "labels": ["epic-2", "backend", "p0-must-have", "milestone-gate"],
    },

    # ─── EPIC 3 ───────────────────────────────────────────────────────────
    {
        "title": "[3.1] Create Booking API",
        "body": """## Story 3.1: Create Booking API

**Epic:** Epic 3 — Booking & Offer Cascade | **FR:** FR-7 | **Type:** backend

**As a** citizen,
**I want** to create a booking by specifying a skill, my location, and an optional description,
**So that** the system can dispatch a cooperative worker.

## Acceptance Criteria

**Given** an authenticated citizen sends `POST /bookings` with `skill`, `lat`, `lng`, optional `description`
**When** the request is valid
**Then** HTTP 201 with `booking_id` and `status: pending`; `job_price` snapshotted from category rate at creation time

**Given** `job_price` is set on booking creation
**When** the category rate changes later
**Then** `job_price` on existing bookings does not change (immutable after creation — PRD FR-7)

**Given** an unauthenticated request
**When** `POST /bookings` is called
**Then** HTTP 401

## References
- PRD FR-7, AD-9 (bookings schema)
- Sprint key: `3-1-create-booking-api`""",
        "labels": ["epic-3", "backend", "p0-must-have"],
    },
    {
        "title": "[3.2] Initial Offer Dispatch",
        "body": """## Story 3.2: Initial Offer Dispatch

**Epic:** Epic 3 | **FRs:** FR-7, FR-8 | **Type:** backend

**As a** system,
**I want** booking creation to automatically dispatch an offer to the top-ranked eligible worker,
**So that** the cascade begins immediately.

## Acceptance Criteria

**Given** a booking is created and at least one eligible worker exists
**When** `POST /bookings` succeeds
**Then** a `booking_offers` row created with `rank_at_offer: 1`, computed `dispatch_score` stored immutably, `status: offered`, `expires_at: NOW() + 2 minutes`

**Given** the offer is created
**When** `GET /booking-offers/booking/{booking_id}` is called
**Then** offer appears with all fields including stored `dispatch_score` (AD-7 — immutable)

**Given** no eligible workers exist
**When** `POST /bookings` succeeds
**Then** `booking.status` → `cancelled` immediately

## References
- PRD FR-8, AD-7 (dispatch_score immutable on INSERT), AD-8 (expires_at = NOW() + 2 min)
- Sprint key: `3-2-initial-offer-dispatch`""",
        "labels": ["epic-3", "backend", "p0-must-have"],
    },
    {
        "title": "[3.3] Worker Accept (with Row Lock)",
        "body": """## Story 3.3: Worker Accept — Row Lock Required

**Epic:** Epic 3 | **FR:** FR-9 | **Type:** backend

⚠️ **CRITICAL AD-6 RULE: MUST use `with_for_update()` row lock. Never read `booking.status` outside a transaction.**

**As a** worker,
**I want** to accept an offer I received,
**So that** I'm confirmed as the assigned worker and the booking is locked.

## Acceptance Criteria

**Given** an authenticated worker with a pending offer (not expired)
**When** `PUT /booking-offers/{id}` is called with `{action: accept}`
**Then** HTTP 200; `booking.status` → `assigned`; `booking.worker_id` set; offer `status` → `accepted`; worker `availability` → `false`

**Given** two simultaneous accept requests for the same offer
**When** both arrive within milliseconds
**Then** exactly one returns HTTP 200 and one returns HTTP 409 (row lock prevents race)

**Given** a worker tries to accept an already-assigned booking
**When** `PUT /booking-offers/{id}` is called
**Then** HTTP 409

## Implementation Pattern
```python
booking = db.query(Booking).filter_by(id=booking_id).with_for_update().first()
if booking.status != 'pending':
    raise HTTPException(409, "Already assigned")
# proceed with accept
```

## References
- PRD FR-9, NFR-3, AD-6 (load-bearing)
- Sprint key: `3-3-worker-accept-row-lock`""",
        "labels": ["epic-3", "backend", "p0-must-have"],
    },
    {
        "title": "[3.4] Worker Decline & Cascade",
        "body": """## Story 3.4: Worker Decline & Offer Cascade

**Epic:** Epic 3 | **FR:** FR-10 | **Type:** backend

**As a** worker,
**I want** to decline an offer without it affecting my rating,
**So that** I have genuine agency over which jobs I take.

## Acceptance Criteria

**Given** an authenticated worker with a pending offer
**When** `PUT /booking-offers/{id}` is called with `{action: decline}`
**Then** HTTP 200; offer `status` → `declined`; a new offer row created for next-ranked eligible worker with `rank_at_offer: 2` and stored `dispatch_score`

**Given** all eligible workers have declined
**When** the last worker declines
**Then** `booking.status` → `cancelled`; no further offers created

**Given** a worker's last 10 offers show < 50% acceptance (with ≥ 5 total)
**When** `GET /workers` is subsequently called
**Then** `reliability_penalty_applied: true` for that worker

## References
- PRD FR-10, AD-7 (score immutable), AD-8 (lazy expiry — check on each action)
- Sprint key: `3-4-worker-decline-cascade`""",
        "labels": ["epic-3", "backend", "p0-must-have"],
    },
    {
        "title": "[3.5] Lazy Offer Expiry",
        "body": """## Story 3.5: Lazy Offer Expiry

**Epic:** Epic 3 | **FR:** FR-11 | **Type:** backend

⚠️ **AD-8 RULE: No background scheduler (no Celery, no APScheduler). Expiry is lazy-checked on every read/action.**

**As a** citizen,
**I want** unresponsive workers to be automatically skipped,
**So that** my booking doesn't stall indefinitely.

## Acceptance Criteria

**Given** an offer with `expires_at` in the past and `status: offered`
**When** any API call touches that offer (read or action)
**Then** offer marked `status: expired` and cascade triggered for next-ranked worker before request continues

**Given** an offer with `expires_at` still in the future
**When** a worker reads or acts on it
**Then** it is NOT expired

## Implementation Pattern
```python
if now() > offer.expires_at and offer.status == 'offered':
    offer.status = 'expired'
    # trigger cascade
```

## References
- PRD FR-11, NFR-4, AD-8 (no scheduler — binding)
- Sprint key: `3-5-lazy-offer-expiry`""",
        "labels": ["epic-3", "backend", "p0-must-have"],
    },
    {
        "title": "[3.6] Booking Flow UI (Citizen — 4-Step Wizard)",
        "body": """## Story 3.6: Booking Flow UI (Citizen)

**Epic:** Epic 3 | **FRs:** FR-7, FR-8 | **UX-DRs:** UX-DR2, UX-DR6 | **Type:** frontend

**As a** citizen,
**I want** to book a service through a clean 4-step wizard,
**So that** I can request help without using Swagger.

## Acceptance Criteria

**Given** an authenticated citizen on `/book`
**When** the page loads
**Then** Step 1 shows 10 skill-category chips with icons; tapping one auto-advances to Step 2 (300ms delay)

**Given** Step 2 — location
**When** the map loads
**Then** Leaflet map with draggable pin; "Use my location" button attempts device GPS; lat/lng text fallback exists

**Given** the citizen submits the booking
**When** API returns 201
**Then** redirect to `/booking/:id` showing animated "Finding a worker…" pulse (UX-DR6)

**Given** `booking.status = assigned`
**When** citizen views `/booking/:id`
**Then** worker card shows: name, "Society Verified" badge, skill, rating chip, distance

## References
- EXPERIENCE.md: Citizen Booking Flow, Flow 1 (Ravi books), UX-DR2 (wizard), UX-DR6 (status states)
- Sprint key: `3-6-booking-flow-ui-citizen`""",
        "labels": ["epic-3", "frontend", "p0-must-have"],
    },
    {
        "title": "[3.7] Worker Offer Inbox UI",
        "body": """## Story 3.7: Worker Offer Inbox UI

**Epic:** Epic 3 | **FRs:** FR-8, FR-9, FR-10 | **UX-DRs:** UX-DR3 | **Type:** frontend

**As a** worker,
**I want** to see incoming job offers with a clear Accept/Decline interface,
**So that** I can respond without confusion.

## Acceptance Criteria

**Given** an authenticated worker on `/worker/offers`
**When** an active offer exists
**Then** offer card appears with: green left-accent, citizen area, skill, distance, job price, expiry countdown bar when `expires_at < 90 seconds`

**Given** the worker taps Accept
**When** the confirmation micro-modal appears
**Then** reads: "You're taking this job. Your availability will be set to busy." with Confirm and Cancel

**Given** the worker swipes right on the offer card
**When** swipe gesture detected
**Then** accept flow triggers (shortcut — UX-DR3)

## References
- EXPERIENCE.md: Offer Card (Worker), Flow 2 (Suresh accepts), UX-DR3
- DESIGN.md: offer-card component, button-primary, button-danger
- Sprint key: `3-7-worker-offer-inbox-ui`""",
        "labels": ["epic-3", "frontend", "p0-must-have"],
    },

    # ─── EPIC 4 ───────────────────────────────────────────────────────────
    {
        "title": "[4.1] Job Completion API",
        "body": """## Story 4.1: Job Completion API

**Epic:** Epic 4 — Completion Economics | **FR:** FR-12 | **Type:** backend

**As a** worker,
**I want** to mark my assigned job as complete,
**So that** the payout split is recorded and I'm available for new offers.

## Acceptance Criteria

**Given** an authenticated worker with `booking.status: assigned` and `booking.worker_id = me`
**When** `PUT /bookings/{id}/complete` is called
**Then** HTTP 200; `booking.status` → `completed`; `platform_fee = job_price * 0.05` stored; worker `availability` → `true`

**Given** a worker tries to complete a booking not assigned to them
**When** `PUT /bookings/{id}/complete` is called
**Then** HTTP 403 Forbidden

## Business Rules (hardcoded for MVP)
- Worker payout: `job_price * 0.95`
- Platform fee (CWF contribution): `job_price * 0.05`
- These are NOT configurable

## References
- PRD FR-12, AGENTS.md invariant: platform fee always job_price * 0.05
- Sprint key: `4-1-job-completion-api`""",
        "labels": ["epic-4", "backend", "p0-must-have"],
    },
    {
        "title": "[4.2] Worker Wallet API",
        "body": """## Story 4.2: Worker Wallet API

**Epic:** Epic 4 | **FR:** FR-13 | **Type:** backend

**As a** worker,
**I want** to see my completed jobs and earnings,
**So that** I know how much I've earned this week and in total.

## Acceptance Criteria

**Given** an authenticated worker
**When** `GET /wallet/{worker_id}` is called
**Then** HTTP 200 with: list of completed bookings (date, skill, job_price, worker_payout=job_price*0.95), `weekly_earnings` (computed at query time), `lifetime_earnings`

**Given** no completed bookings
**When** `GET /wallet/{worker_id}` is called
**Then** empty list, `weekly_earnings: 0`, `lifetime_earnings: 0`

**Given** `weekly_earnings` in response
**When** current day is Monday 00:01 UTC
**Then** reflects only jobs completed since Monday 00:00 UTC (automatic reset — AD-5)

## ⚠️ weekly_earnings is NEVER read from worker_profiles — always computed from bookings (AD-5)

## References
- PRD FR-13, AD-5 (no stored counter)
- Sprint key: `4-2-worker-wallet-api`""",
        "labels": ["epic-4", "backend", "p0-must-have"],
    },
    {
        "title": "[4.3] Cooperative Welfare Fund Summary API",
        "body": """## Story 4.3: Cooperative Welfare Fund Summary API

**Epic:** Epic 4 | **FR:** FR-14 | **Type:** backend

**As a** citizen or federation admin,
**I want** to see the total Cooperative Welfare Fund balance,
**So that** I can verify the platform's economic promise is real.

## Acceptance Criteria

**Given** completed bookings exist
**When** `GET /welfare-fund/summary` is called
**Then** HTTP 200 with `{ total_fees: <sum of all platform_fee from completed bookings>, completed_bookings: <count> }`

**Given** no completed bookings
**When** `GET /welfare-fund/summary` is called
**Then** `{ total_fees: 0, completed_bookings: 0 }`

## References
- PRD FR-14
- Sprint key: `4-3-welfare-fund-summary-api`""",
        "labels": ["epic-4", "backend", "p0-must-have"],
    },
    {
        "title": "[4.4] Wallet & Completion UI",
        "body": """## Story 4.4: Wallet & Completion UI

**Epic:** Epic 4 | **FRs:** FR-12, FR-13, FR-14 | **UX-DRs:** UX-DR4, UX-DR5 | **Type:** frontend

**As a** worker,
**I want** to see my wallet update after marking a job complete,
**So that** I have immediate confidence the payout is correct.

## Acceptance Criteria

**Given** the worker taps "Mark Complete"
**When** API returns 200
**Then** wallet counter animates upward (count-up, 500ms); weekly earnings chip updates; "₹X added to the Cooperative Welfare Fund" toast appears

**Given** the worker visits `/worker/wallet`
**When** the page loads
**Then** weekly earnings chip in monospace; earnings table shows: Date, Area, Service, Job price, Your payout (95%), Welfare Fund (5%)

**Given** the citizen views `/booking/:id` after completion
**When** `status: completed`
**Then** violet welfare fund chip appears: "₹X added to the Cooperative Welfare Fund" (UX-DR4)

## References
- DESIGN.md: welfare-counter (violet gradient), typography.font-mono for earnings numbers
- EXPERIENCE.md: Worker Wallet, Flow 2 (wallet counter animates), UX-DR4, UX-DR5
- Sprint key: `4-4-wallet-completion-ui`""",
        "labels": ["epic-4", "frontend", "p0-must-have"],
    },

    # ─── EPIC 5 ───────────────────────────────────────────────────────────
    {
        "title": "[5.1] Worker Verification Toggle API",
        "body": """## Story 5.1: Worker Verification Toggle API

**Epic:** Epic 5 — Polish, Rating & Federation | **FR:** FR-15 | **Type:** backend

**As an** admin,
**I want** to toggle a worker's verified status,
**So that** cooperative-registered workers get the "Society Verified" badge.

## Acceptance Criteria

**Given** an admin-authenticated request to `PATCH /admin/workers/{id}/verify` with `{ verified: true }`
**When** the request is valid
**Then** HTTP 200; `worker_profiles.verified` → `true`; worker now appears in `GET /workers` results

**Given** a worker with `verified: false`
**When** `GET /workers` is called
**Then** the worker does NOT appear in dispatch results

## References
- PRD FR-15
- Sprint key: `5-1-worker-verification-toggle-api`""",
        "labels": ["epic-5", "backend", "p1-should-have"],
    },
    {
        "title": "[5.2] Citizen Rating API",
        "body": """## Story 5.2: Citizen Rating API

**Epic:** Epic 5 | **FR:** FR-16 | **Type:** backend

**As a** citizen,
**I want** to rate a worker after a completed job (1–5 stars),
**So that** the dispatch algorithm reflects real quality signals over time.

## Acceptance Criteria

**Given** an authenticated citizen with a `completed` booking
**When** `POST /bookings/{id}/rating` is called with `{ rating: 4 }`
**Then** HTTP 200; `worker_profiles.rating` updates to the running average of all ratings received

**Given** a citizen tries to rate the same booking twice
**When** the second rating request is made
**Then** HTTP 409 Conflict

**Given** a rating outside 1–5
**When** the request is made
**Then** HTTP 422 Validation Error

## References
- PRD FR-16
- Sprint key: `5-2-citizen-rating-api`""",
        "labels": ["epic-5", "backend", "p1-should-have"],
    },
    {
        "title": "[5.3] Offer Audit Trail API",
        "body": """## Story 5.3: Offer Audit Trail API

**Epic:** Epic 5 | **FR:** FR-17 | **Type:** backend

**As a** federation admin or evaluator,
**I want** to view the full offer cascade history for any booking,
**So that** I can verify the dispatch algorithm made the correct decisions.

## Acceptance Criteria

**Given** a booking with multiple offers (e.g., 3 declines + 1 accept)
**When** `GET /booking-offers/booking/{booking_id}` is called
**Then** HTTP 200 with ordered list: `worker_name`, `rank_at_offer`, `dispatch_score` (stored value — NOT recomputed), `status`, `created_at`

**Given** a fresh booking with one offer
**When** the endpoint is called
**Then** one record returned

## ⚠️ dispatch_score in the audit trail is READ from the stored value (AD-7). It is NEVER recomputed.

## References
- PRD FR-17, NFR-1 (auditability), AD-7 (immutable dispatch_score)
- Sprint key: `5-3-offer-audit-trail-api`""",
        "labels": ["epic-5", "backend", "p1-should-have"],
    },
    {
        "title": "[5.4] Rating UI & Verified Badge",
        "body": """## Story 5.4: Rating UI & Verified Badge

**Epic:** Epic 5 | **FRs:** FR-15, FR-16 | **Type:** frontend

**As a** citizen,
**I want** to rate my worker and see the "Society Verified" badge,
**So that** the platform's trust signals are visible.

## Acceptance Criteria

**Given** `booking.status: completed` and no existing rating
**When** citizen views `/booking/:id`
**Then** 1–5 star rating input and "Rate [Worker Name]" button shown

**Given** the citizen submits a rating
**When** API returns 200
**Then** rating input replaced with "Rating submitted. Thank you."

**Given** a verified worker appears in a list
**When** their card renders
**Then** green "Society Verified" badge (`badge-verified` from DESIGN.md) shown next to name

## References
- DESIGN.md: badge-verified, badge-unverified components
- Sprint key: `5-4-rating-ui-verified-badge`""",
        "labels": ["epic-5", "frontend", "p1-should-have"],
    },
    {
        "title": "[5.5] Federation Dashboard UI",
        "body": """## Story 5.5: Federation Dashboard UI

**Epic:** Epic 5 | **FR:** FR-17 | **UX-DRs:** UX-DR9 | **Type:** frontend

**As a** Ministry/NCCT evaluator,
**I want** a read-only federation dashboard showing aggregate data and the full booking audit trail,
**So that** I can verify the cooperative economics and dispatch fairness without Swagger.

## Acceptance Criteria

**Given** any authenticated user visits `/federation`
**When** the page loads
**Then** three counters: "X registered workers", "Y completed bookings", and the Cooperative Welfare Fund total in a violet gradient card (UX-DR4)

**Given** completed bookings exist
**When** the user clicks on a booking
**Then** full offer audit trail shown: worker name, rank, dispatch score (monospace), status — in offer order

**Given** the cascade demo booking (3 declines + 1 accept)
**When** the federation view shows it
**Then** each row shows stored `dispatch_score`, making it clear why lower-earning workers ranked higher

## References
- EXPERIENCE.md: Federation View, Flow 4 (ministry evaluator), UX-DR9
- DESIGN.md: welfare-counter (violet), dispatch-score in font-mono
- Sprint key: `5-5-federation-dashboard-ui`""",
        "labels": ["epic-5", "frontend", "p1-should-have"],
    },
    {
        "title": "[5.6] Demo Reliability — End-to-End Validation",
        "body": """## Story 5.6: Demo Reliability — E2E Validation

**Epic:** Epic 5 | **Type:** fullstack

**As a** team preparing the hackathon demo,
**I want** a validated end-to-end run of the complete cascade demo beat,
**So that** the demo fails safely if anything is wrong before we present.

## Acceptance Criteria

**Given** the app is running with seed data
**When** the full demo flow runs: Ravi books → Suresh (rank 1) declines → Priya (rank 2) declines → Anil (rank 3) declines → Meena (rank 4) accepts → Meena marks complete → Ravi rates 4 stars
**Then** every step completes without a hardcoded response

**Given** the above flow is complete
**When** `GET /booking-offers/booking/{id}` is called
**Then** 4 offer rows with correct ranks and stored dispatch scores

**Given** Meena accepts and completes the booking
**When** wallet view is checked
**Then** Meena's `weekly_earnings` reflects job_price × 0.95

**Given** the booking is complete
**When** `GET /welfare-fund/summary` is called
**Then** `total_fees` increased by `job_price * 0.05`

**And** WCAG 2.1 AA contrast is met for all key screens (NFR-6) — verified via browser accessibility audit

## References
- PRD Section 10 (Success Metrics SM-1, SM-2, SM-3)
- EXPERIENCE.md: Flow 3 (Meena cascade — the demo beat)
- Sprint key: `5-6-demo-reliability-e2e-validation`""",
        "labels": ["epic-5", "fullstack", "p0-must-have"],
    },
]

def run_issue(issue, index):
    labels = ",".join(issue["labels"])
    cmd = [
        "gh", "issue", "create",
        "--title", issue["title"],
        "--body", issue["body"],
        "--label", labels,
        "--repo", REPO,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        url = result.stdout.strip()
        print(f"  ✅ [{index+1}/26] {issue['title'][:60]} → {url}")
    else:
        print(f"  ❌ [{index+1}/26] FAILED: {issue['title'][:60]}")
        print(f"     {result.stderr.strip()[:200]}")
    time.sleep(1.2)  # rate limit buffer

print(f"Creating 26 issues on {REPO}...")
for i, issue in enumerate(issues):
    run_issue(issue, i)

print("\nDone!")
