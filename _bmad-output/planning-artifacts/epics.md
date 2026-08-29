---
stepsCompleted: [1, 2, 3, 4]
inputDocuments:
  - _bmad-output/planning-artifacts/prds/prd-Samarth-2026-08-29/prd.md
  - _bmad-output/planning-artifacts/architecture/architecture-Samarth-2026-08-29/ARCHITECTURE-SPINE.md
  - _bmad-output/planning-artifacts/ux-designs/ux-Samarth-2026-08-29/DESIGN.md
  - _bmad-output/planning-artifacts/ux-designs/ux-Samarth-2026-08-29/EXPERIENCE.md
---

# Samarth - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for Samarth, decomposing requirements from the PRD (17 FRs), Architecture (13 ADs), and UX Design into implementable stories for a 6-person team targeting a hackathon MVP.

---

## Requirements Inventory

### Functional Requirements

- FR-1: Citizen Registration — phone, name, password → JWT
- FR-2: Worker Registration — phone, name, skill, coordinates → JWT; verified defaults false
- FR-3: Login — both roles, phone + password → JWT with role
- FR-4: Worker List with Dispatch Score — ranked, filtered by skill/location/verified/available
- FR-5: Dispatch Score Formula — (5000−WeeklyEarnings)×2 + (1000×Rating) − (500×Distance) − ReliabilityPenalty
- FR-6: Reliability Penalty Flag — expose `reliability_penalty_applied` in worker response
- FR-7: Create Booking — citizen creates booking with skill, location, description; job_price snapshotted
- FR-8: Initial Offer Dispatch — top-ranked worker gets offer with expires_at = NOW() + 2 min
- FR-9: Worker Accept — row-locked accept, booking→assigned, worker→unavailable
- FR-10: Worker Decline / Cascade — decline → next worker offered; all decline → booking cancelled
- FR-11: Offer Expiry (lazy) — check expires_at on every read/action; expire + cascade if past
- FR-12: Mark Complete — worker marks complete; platform_fee = job_price × 0.05; availability reset
- FR-13: Worker Wallet View — completed bookings list, weekly_earnings (computed), lifetime total
- FR-14: Cooperative Welfare Fund Summary — sum of all platform_fee from completed bookings
- FR-15: Verification Toggle — admin toggles worker verified flag; unverified excluded from dispatch
- FR-16: Submit Rating — citizen rates 1–5 after completion; updates worker_profiles.rating average
- FR-17: Offer Audit Trail — full offer sequence per booking: worker, rank, score, outcome

### Non-Functional Requirements

- NFR-1: Auditability — dispatch_score and rank_at_offer stored immutably on every offer row
- NFR-2: Determinism — seed data produces same ranking every run (no external dependencies)
- NFR-3: Concurrency safety — row-level lock on accept path
- NFR-4: Graceful expiry — lazy offer expiry, no background scheduler
- NFR-5: Password security — bcrypt cost factor ≥ 12; no plaintext in logs/DB
- NFR-6: WCAG 2.1 AA — all text/background contrast ≥ 4.5:1

### Additional Requirements (Architecture)

- ARCH-1: FastAPI (Python 3.11) + PostgreSQL 15 + SQLAlchemy + Alembic migrations
- ARCH-2: React 18 + Vite; TanStack Query for server state; no UI framework
- ARCH-3: Docker Compose for local development (backend + frontend + database)
- ARCH-4: WeeklyEarnings MUST be computed at query time — no stored counter (AD-5)
- ARCH-5: Accept path MUST use `with_for_update()` row lock (AD-6)
- ARCH-6: dispatch_score on booking_offers is immutable after INSERT (AD-7)
- ARCH-7: No background scheduler — lazy offer expiry only (AD-8)
- ARCH-8: Canonical dispatch.py function — no deviation (AD-5, FR-5)
- ARCH-9: Milestone gate: GET /workers endpoint must produce correct seed ranking before any React component is committed

### UX Design Requirements

- UX-DR1: CSS custom property token system from DESIGN.md — all design tokens as CSS vars in tokens.css
- UX-DR2: Citizen 4-step booking wizard on mobile; single-page inline form on desktop (≥1024px)
- UX-DR3: Offer card component — green left-accent, expiry progress bar, Accept/Decline full-width buttons with swipe gestures
- UX-DR4: Welfare Fund counter — violet gradient card (distinct from earnings), visible on booking completion screen
- UX-DR5: Worker wallet — weekly earnings chip in monospace; reliability badge (penalty visible to worker only)
- UX-DR6: Booking status real-time states — animated pulse (finding), worker card (assigned), completion summary (completed)
- UX-DR7: Bottom tab navigation on mobile (4 tabs); sidebar on desktop (240px)
- UX-DR8: Skeleton loading screens (not spinners) for list loads; 10s timeout → error message
- UX-DR9: Federation audit trail table — dispatch scores in monospace, sortable, demonstrates cascade

### FR Coverage Map

| FR | Epic | Brief description |
|---|---|---|
| FR-1, FR-2, FR-3 | Epic 1 | Auth — registration + login for both roles |
| FR-4, FR-5, FR-6 | Epic 2 | Dispatch algorithm — score computation, ranking, penalty |
| FR-7, FR-8, FR-9, FR-10, FR-11 | Epic 3 | Booking lifecycle — create, offer, accept/decline/cascade, expiry |
| FR-12, FR-13, FR-14 | Epic 4 | Completion economics — wallet, payout split, welfare fund |
| FR-15 | Epic 5 | Worker verification badge |
| FR-16 | Epic 5 | Citizen rating |
| FR-17 | Epic 5 | Audit trail / federation view |
| UX-DR1, UX-DR7, UX-DR8 | Epic 1 | Project setup + design token system + navigation skeleton |
| UX-DR2, UX-DR6 | Epic 3 | Booking UI wizard + status states |
| UX-DR3 | Epic 3 | Offer card component |
| UX-DR4, UX-DR5 | Epic 4 | Welfare fund counter + wallet display |
| UX-DR9 | Epic 5 | Federation audit table |

---

## Epic List

### Epic 1: Project Foundation & Authentication
Users can register and log in to Samarth with the correct role-based experience. The project is fully runnable locally via Docker Compose. Design token system is in place for all subsequent UI work.
**FRs covered:** FR-1, FR-2, FR-3
**UX-DRs covered:** UX-DR1, UX-DR7

### Epic 2: Dispatch Algorithm (Milestone Gate)
The dispatch score is fully implemented and verifiable in Swagger. A citizen can retrieve a ranked list of eligible workers for a given skill and location, with scores and metadata. Seed data produces the deterministic ranking: Suresh > Priya > Anil > Meena.
**FRs covered:** FR-4, FR-5, FR-6
**Arch:** ARCH-9 (milestone gate)

### Epic 3: Booking & Offer Cascade
A citizen can create a booking that triggers a real offer cascade. Workers receive, accept, or decline offers. Cascade works. Offer expiry works. The complete loop — book → offer → decline → cascade → accept — runs end-to-end.
**FRs covered:** FR-7, FR-8, FR-9, FR-10, FR-11
**UX-DRs covered:** UX-DR2, UX-DR3, UX-DR6

### Epic 4: Completion Economics (Wallet & Welfare Fund)
A worker can mark a job complete. Payout split (95/5) is computed and displayed. Worker wallet shows earnings history and weekly total. Cooperative Welfare Fund counter is live and accurate.
**FRs covered:** FR-12, FR-13, FR-14
**UX-DRs covered:** UX-DR4, UX-DR5

### Epic 5: Polish, Verification, Rating & Federation View
Workers can be verified (badge shows to citizens). Citizens can rate completed jobs (feeds dispatch). Federation view shows real aggregate data and the full offer audit trail with dispatch scores.
**FRs covered:** FR-15, FR-16, FR-17
**UX-DRs covered:** UX-DR9, NFR-6

---

## Epic 1: Project Foundation & Authentication

Users can register and log in to Samarth. The dev environment runs locally in Docker Compose. Design token system is initialised for all subsequent UI work.

### Story 1.1: Project Bootstrap & Docker Compose Setup

As a **developer**,
I want a single `docker-compose up` command to start the full local development environment (PostgreSQL, FastAPI backend, React frontend),
So that every team member has a consistent, reproducible environment from day one.

**Acceptance Criteria:**

**Given** the repo is cloned and Docker is running
**When** `docker-compose up` is run
**Then** PostgreSQL starts on port 5432, FastAPI starts on port 8000 (`/docs` loads), and the React dev server starts on port 3000

**Given** the backend starts
**When** FastAPI initialises
**Then** all four tables (users, worker_profiles, bookings, booking_offers) are created via Alembic initial migration (`alembic upgrade head`)

**Given** the directory structure specification in ARCHITECTURE-SPINE.md
**When** the repo is initialised
**Then** `backend/` and `frontend/` are structured exactly as specified in AD-9 directory layout; no extra folders at the top level

---

### Story 1.2: Design Token System (CSS Custom Properties)

As a **frontend developer**,
I want a `tokens.css` file that defines all Samarth design tokens as CSS custom properties,
So that every UI component uses a single, consistent source of truth for colors, typography, spacing, and radii.

**Acceptance Criteria:**

**Given** the DESIGN.md color, typography, spacing, and rounded token tables
**When** `tokens.css` is imported globally
**Then** all tokens from DESIGN.md are available as `--color-brand-primary`, `--font-sans`, `--spacing-md`, `--rounded-xl`, etc.

**Given** Inter font is specified in DESIGN.md
**When** the app loads
**Then** Inter is loaded from Google Fonts and applied as the default font-family via `{typography.font-sans}`

**Given** the token file exists
**When** a developer adds a new component
**Then** they reference only tokens from tokens.css — no hardcoded hex values in component CSS

---

### Story 1.3: Citizen Registration API

As a **citizen**,
I want to register with my name, phone number, and a password,
So that I can access the Samarth platform and request services.

**Acceptance Criteria:**

**Given** a valid payload (`name`, `phone`, `password`, `role: citizen`)
**When** `POST /auth/register` is called
**Then** HTTP 201 is returned with a JWT token; a `users` row with `role: citizen` is created; password is stored hashed (bcrypt, cost 12)

**Given** a phone number that already exists in the `users` table
**When** `POST /auth/register` is called
**Then** HTTP 409 Conflict is returned

**Given** any registration request
**When** the password is stored
**Then** the plain-text password never appears in the database, logs, or API response

---

### Story 1.4: Worker Registration API

As a **cooperative worker**,
I want to register with my name, phone, skill category, and location,
So that I can receive job offers from Samarth.

**Acceptance Criteria:**

**Given** a valid payload (`name`, `phone`, `password`, `role: worker`, `skill`, `lat`, `lng`)
**When** `POST /auth/register` is called
**Then** HTTP 201 is returned; a `users` row with `role: worker` and a `worker_profiles` row are created; `verified: false`, `availability: true`, `rating: null`

**Given** an invalid skill category (not in the allowed list of 10)
**When** `POST /auth/register` is called
**Then** HTTP 422 is returned with a validation error

---

### Story 1.5: Login API (Both Roles)

As a **citizen or worker**,
I want to log in with my phone number and password,
So that I can access my role-specific dashboard.

**Acceptance Criteria:**

**Given** a registered user's phone and correct password
**When** `POST /auth/login` is called
**Then** HTTP 200 is returned with a signed JWT; the JWT payload includes `user_id`, `role`, and `name`

**Given** an incorrect password or unregistered phone
**When** `POST /auth/login` is called
**Then** HTTP 401 Unauthorized is returned

---

### Story 1.6: Citizen Registration & Login UI

As a **citizen**,
I want to register and log in via the Samarth web app,
So that I can reach my dashboard without needing to use Swagger.

**Acceptance Criteria:**

**Given** the user visits `/register` and selects the "Citizen" role
**When** they fill in name, phone, and password and submit
**Then** the API is called, a JWT is stored in memory/localStorage, and the user is redirected to `/dashboard`

**Given** a registered citizen visits `/login`
**When** they enter correct credentials
**Then** they are redirected to `/dashboard`

**Given** a failed login (wrong credentials)
**When** the form is submitted
**Then** an inline error message appears below the form (not a modal); no page reload

**Given** mobile viewport (375px)
**When** the registration form renders
**Then** the role selector shows as two full-width tap-target cards (Citizen / Worker)

---

### Story 1.7: Worker Registration & Login UI

As a **cooperative worker**,
I want to register and log in via the Samarth web app with my skill and location,
So that I can start receiving job offers.

**Acceptance Criteria:**

**Given** the user selects "Worker" during registration
**When** the form renders
**Then** a skill-category chip group (all 10 categories, horizontal layout) and a location input (map pin + lat/lng fallback) are shown

**Given** the worker submits valid registration
**When** the API returns 201
**Then** the JWT is stored and the user is redirected to `/worker/dashboard`

**Given** the worker dashboard loads
**When** the worker is authenticated
**Then** the bottom tab bar (Home, Offers, Wallet, Profile) is visible on mobile

---

## Epic 2: Dispatch Algorithm (Milestone Gate)

The dispatch score is fully implemented and verifiable in Swagger before any booking UI exists.

### Story 2.1: Seed Data Script

As a **developer demonstrating the platform**,
I want a `seed.py` script that populates 2 citizens and 4 workers with deterministic, verifiable data,
So that the dispatch ranking can be validated in Swagger before any UI is built.

**Acceptance Criteria:**

**Given** the database is empty
**When** `python backend/app/seed.py` is run
**Then** 2 citizen users and 4 worker users are created (Ravi Sharma, Priya customer; Suresh Kumar, Priya Gupta, Anil Yadav, Meena Verma as workers)

**Given** the seed script runs
**When** workers are created
**Then** each worker has: `skill: electrician`, `verified: true`, `availability: true`, `lat/lng` within 5km of Jaipur city center, and the specific `rating` and `lat/lng` values from Appendix A of the PRD

**Given** seed data is loaded
**When** `GET /workers?skill=electrician&lat=26.9124&lng=75.7873` is called
**Then** Suresh Kumar appears first (score ~12,550), then Priya Gupta (~12,000), then Anil Yadav (~9,750), then Meena Verma (~5,750)

---

### Story 2.2: WeeklyEarnings Subquery (Dispatch Core)

As a **backend developer**,
I want a function that computes a worker's weekly earnings at query time from the `bookings` table,
So that the dispatch score always reflects live data and resets automatically each Monday.

**Acceptance Criteria:**

**Given** a worker with completed bookings in the current ISO week
**When** `compute_weekly_earnings(worker_id, db)` is called
**Then** it returns the sum of `job_price * 0.95` for all `bookings` where `status = 'completed'` and `created_at >= date_trunc('week', NOW())`

**Given** a new worker with no completed bookings this week
**When** `compute_weekly_earnings` is called
**Then** it returns `Decimal('0')`

**Given** the current day is Monday at 00:01 UTC
**When** `compute_weekly_earnings` is called
**Then** it returns 0 even if the worker had ₹5000 of bookings last week (reset is automatic)

**And** no `weekly_earnings` column exists on `worker_profiles` — the function queries `bookings` only

---

### Story 2.3: Reliability Penalty Computation

As a **backend developer**,
I want a function that checks a worker's recent offer acceptance rate and returns whether the reliability penalty applies,
So that the dispatch algorithm cannot be gamed by declining all offers.

**Acceptance Criteria:**

**Given** a worker with ≥ 5 total offers, fewer than 50% accepted in the last 10
**When** `compute_reliability_penalty(worker_id, db)` is called
**Then** it returns `True` (penalty applies)

**Given** a worker with fewer than 5 total offers (grace period)
**When** `compute_reliability_penalty` is called
**Then** it returns `False` regardless of acceptance rate

**Given** a worker with ≥ 5 offers and ≥ 50% acceptance rate in the last 10
**When** `compute_reliability_penalty` is called
**Then** it returns `False`

---

### Story 2.4: Dispatch Score Endpoint (GET /workers)

As a **citizen or developer**,
I want `GET /workers?skill=&lat=&lng=` to return eligible workers ranked by dispatch score,
So that I can verify the fairness algorithm is working correctly.

**Acceptance Criteria:**

**Given** seed data is loaded and the Appendix A request (skill=electrician, lat=26.9124, lng=75.7873)
**When** `GET /workers?skill=electrician&lat=26.9124&lng=75.7873` is called
**Then** the response is an array of 4 workers in the order: Suresh (rank 1), Priya (rank 2), Anil (rank 3), Meena (rank 4); each row includes `dispatch_score`, `weekly_earnings`, `rating_is_default`, `reliability_penalty_applied`

**Given** a worker with `verified: false`
**When** `GET /workers` is called
**Then** that worker does not appear in the results

**Given** a worker with `availability: false`
**When** `GET /workers` is called
**Then** that worker does not appear in the results

**Given** a worker more than 5km from the request location
**When** `GET /workers` is called
**Then** that worker does not appear in the results

**Given** a worker with `rating: null` (cold-start)
**When** their score is computed
**Then** `rating_is_default: true` appears in the response and the effective rating used is `4.0`

---

## Epic 3: Booking & Offer Cascade

A citizen can book a service. The cascade runs end-to-end. The demo beat — book → offer → decline → cascade → accept — works deterministically.

### Story 3.1: Create Booking API

As a **citizen**,
I want to create a booking by specifying a skill, my location, and an optional description,
So that the system can find and dispatch a cooperative worker to help me.

**Acceptance Criteria:**

**Given** an authenticated citizen sends `POST /bookings` with `skill`, `lat`, `lng`, optional `description`
**When** the request is valid
**Then** HTTP 201 is returned with `booking_id` and `status: pending`; `job_price` is snapshotted from the category rate at creation time

**Given** `job_price` is set on booking creation
**When** the category rate changes later
**Then** `job_price` on existing bookings does not change (it's immutable after creation)

**Given** an unauthenticated request
**When** `POST /bookings` is called
**Then** HTTP 401 is returned

---

### Story 3.2: Initial Offer Dispatch

As a **system**,
I want booking creation to automatically dispatch an offer to the top-ranked eligible worker,
So that the offer cascade begins immediately without manual intervention.

**Acceptance Criteria:**

**Given** a booking is created and at least one eligible worker exists
**When** `POST /bookings` succeeds
**Then** a `booking_offers` row is created with `rank_at_offer: 1`, the computed `dispatch_score` stored immutably, `status: offered`, and `expires_at: NOW() + 2 minutes`

**Given** the offer is created
**When** `GET /booking-offers/booking/{booking_id}` is called
**Then** the offer appears with all fields populated including the stored `dispatch_score`

**Given** no eligible workers exist for the request
**When** `POST /bookings` succeeds
**Then** `booking.status` is set to `cancelled` immediately with a message

---

### Story 3.3: Worker Accept (with Row Lock)

As a **worker**,
I want to accept an offer I received,
So that I'm confirmed as the assigned worker and the booking is locked.

**Acceptance Criteria:**

**Given** an authenticated worker with a pending offer (`status: offered`, not expired)
**When** `PUT /booking-offers/{id}` is called with `{action: accept}`
**Then** HTTP 200 is returned; `booking.status` → `assigned`; `booking.worker_id` set; `booking_offers.status` → `accepted`; worker's `availability` → `false`

**Given** two simultaneous accept requests for the same offer
**When** both arrive within milliseconds
**Then** exactly one returns HTTP 200 and one returns HTTP 409 (row lock prevents double-accept — AD-6)

**Given** a worker tries to accept an already-assigned booking
**When** `PUT /booking-offers/{id}` is called
**Then** HTTP 409 is returned

---

### Story 3.4: Worker Decline & Cascade

As a **worker**,
I want to decline an offer without it affecting my rating,
So that I have genuine agency over which jobs I take.

**Acceptance Criteria:**

**Given** an authenticated worker with a pending offer
**When** `PUT /booking-offers/{id}` is called with `{action: decline}`
**Then** HTTP 200 is returned; `booking_offers.status` → `declined`; a new offer row is created for the next-ranked eligible worker with `rank_at_offer: 2` and the stored `dispatch_score`

**Given** all eligible workers have declined
**When** the last worker declines
**Then** `booking.status` → `cancelled`; no further offers are created

**Given** a worker's last 10 offers after the decline show < 50% acceptance (with ≥ 5 total)
**When** `GET /workers` is subsequently called
**Then** `reliability_penalty_applied: true` appears for that worker (AD-5)

---

### Story 3.5: Lazy Offer Expiry

As a **citizen**,
I want unresponsive workers to be automatically skipped,
So that my booking doesn't stall indefinitely if a worker ignores the offer.

**Acceptance Criteria:**

**Given** an offer with `expires_at` in the past and `status: offered`
**When** any API call touches that offer (read or action)
**Then** the offer is marked `status: expired` and a new offer is created for the next-ranked worker before the request continues (AD-8 — no scheduler)

**Given** an offer with `expires_at` still in the future
**When** a worker reads or acts on it
**Then** it is not expired

---

### Story 3.6: Booking Flow UI (Citizen)

As a **citizen**,
I want to book a service through the app using a clean 4-step wizard,
So that I can request help without needing to use Swagger.

**Acceptance Criteria:**

**Given** an authenticated citizen on `/book`
**When** the page loads
**Then** Step 1 shows 10 skill-category chips with icons; tapping one auto-advances to Step 2

**Given** Step 2 — location
**When** the map loads
**Then** a Leaflet map with a draggable pin is shown; a "Use my location" button attempts device GPS; a lat/lng text fallback exists

**Given** the citizen submits the booking
**When** the API returns 201
**Then** they are redirected to `/booking/:id` which shows the animated "Finding a worker…" pulse (UX-DR6)

**Given** the booking status is `assigned`
**When** the citizen views `/booking/:id`
**Then** the worker card shows: name, "Society Verified" badge, skill, rating chip, estimated distance

---

### Story 3.7: Worker Offer Inbox UI

As a **worker**,
I want to see incoming job offers with a clear Accept/Decline interface,
So that I can respond without confusion.

**Acceptance Criteria:**

**Given** an authenticated worker on `/worker/offers`
**When** an active offer exists
**Then** the offer card appears with: green left-accent, citizen area, skill, distance, job price, expiry countdown bar when `expires_at < 90 seconds`

**Given** the worker taps Accept
**When** the confirmation micro-modal appears
**Then** it reads: "You're taking this job. Your availability will be set to busy." with Confirm and Cancel buttons

**Given** the worker swipes right on the offer card
**When** the swipe gesture is detected
**Then** the same accept flow triggers (shortcut — UX-DR3)

---

## Epic 4: Completion Economics (Wallet & Welfare Fund)

Workers complete jobs and see real payout data. The Cooperative Welfare Fund counter is live and visible.

### Story 4.1: Job Completion API

As a **worker**,
I want to mark my assigned job as complete,
So that the payout split is recorded and I'm available for new offers.

**Acceptance Criteria:**

**Given** an authenticated worker with `booking.status: assigned` and `booking.worker_id = me`
**When** `PUT /bookings/{id}/complete` is called
**Then** HTTP 200; `booking.status` → `completed`; `platform_fee = job_price * 0.05` stored; worker `availability` → `true`

**Given** a worker tries to complete a booking not assigned to them
**When** `PUT /bookings/{id}/complete` is called
**Then** HTTP 403 Forbidden

---

### Story 4.2: Worker Wallet API

As a **worker**,
I want to see my completed jobs and earnings,
So that I know how much I've earned this week and in total.

**Acceptance Criteria:**

**Given** an authenticated worker
**When** `GET /wallet/{worker_id}` is called
**Then** HTTP 200 with: list of completed bookings (date, skill, job_price, worker_payout=job_price*0.95), `weekly_earnings` (computed at query time from current ISO week), `lifetime_earnings`

**Given** no completed bookings
**When** `GET /wallet/{worker_id}` is called
**Then** an empty list is returned and `weekly_earnings: 0`, `lifetime_earnings: 0`

**Given** `weekly_earnings` is in the response
**When** the current day is Monday at 00:01
**Then** it reflects only jobs completed since Monday 00:00 UTC (automatic reset — AD-5)

---

### Story 4.3: Cooperative Welfare Fund Summary API

As a **citizen or federation admin**,
I want to see the total Cooperative Welfare Fund balance,
So that I can verify the platform's economic promise is real.

**Acceptance Criteria:**

**Given** completed bookings exist
**When** `GET /welfare-fund/summary` is called
**Then** HTTP 200 with `{ total_fees: <sum of all platform_fee>, completed_bookings: <count> }`

**Given** no completed bookings
**When** `GET /welfare-fund/summary` is called
**Then** `{ total_fees: 0, completed_bookings: 0 }`

---

### Story 4.4: Wallet & Completion UI

As a **worker**,
I want to see my wallet update in real-time after marking a job complete,
So that I have immediate confidence the payout is correct.

**Acceptance Criteria:**

**Given** the worker taps "Mark Complete" on `/worker/dashboard`
**When** the API returns 200
**Then** the wallet counter animates upward (count-up, 500ms); the weekly earnings chip updates; "₹X added to the Cooperative Welfare Fund" appears as a toast

**Given** the worker visits `/worker/wallet`
**When** the page loads
**Then** the weekly earnings chip shows in monospace font; the earnings table shows columns: Date, Area, Service, Job price, Your payout (95%), Welfare Fund (5%)

**Given** the citizen completes booking flow on `/booking/:id`
**When** `status: completed`
**Then** the violet welfare fund chip appears: "₹X added to the Cooperative Welfare Fund" (UX-DR4)

---

## Epic 5: Polish, Verification, Rating & Federation View

The hackathon demo is bulletproof. Workers can be verified with a badge. Citizens can rate. Federation view shows live data with the audit trail.

### Story 5.1: Worker Verification Toggle API

As an **admin**,
I want to toggle a worker's verified status,
So that cooperative-registered workers get the "Society Verified" badge visible to citizens.

**Acceptance Criteria:**

**Given** an admin-authenticated request to `PATCH /admin/workers/{id}/verify` with `{ verified: true }`
**When** the request is valid
**Then** HTTP 200; `worker_profiles.verified` → `true`; the worker now appears in `GET /workers` results

**Given** a worker with `verified: false`
**When** `GET /workers` is called
**Then** the worker does not appear in dispatch results

---

### Story 5.2: Citizen Rating API

As a **citizen**,
I want to rate a worker after a completed job (1–5 stars),
So that the dispatch algorithm reflects real quality signals over time.

**Acceptance Criteria:**

**Given** an authenticated citizen with a `completed` booking
**When** `POST /bookings/{id}/rating` is called with `{ rating: 4 }`
**Then** HTTP 200; `worker_profiles.rating` updates to the running average of all ratings received

**Given** a citizen tries to rate the same booking twice
**When** the second rating request is made
**Then** HTTP 409 Conflict

**Given** a rating outside 1–5
**When** the request is made
**Then** HTTP 422 Validation Error

---

### Story 5.3: Offer Audit Trail API

As a **federation admin or evaluator**,
I want to view the full offer cascade history for any booking,
So that I can verify the dispatch algorithm made the correct decisions.

**Acceptance Criteria:**

**Given** a booking that went through multiple offers (e.g., 3 declines + 1 accept)
**When** `GET /booking-offers/booking/{booking_id}` is called
**Then** HTTP 200 with an ordered list of offer records: `worker_name`, `rank_at_offer`, `dispatch_score` (stored value — not recomputed), `status`, `created_at`

**Given** a fresh booking with one offer
**When** the endpoint is called
**Then** one record is returned

---

### Story 5.4: Rating UI & Verified Badge

As a **citizen**,
I want to rate my worker and see the "Society Verified" badge on worker cards,
So that the platform's trust signals are visible and actionable.

**Acceptance Criteria:**

**Given** `booking.status: completed` and no existing rating
**When** the citizen views `/booking/:id`
**Then** a 1–5 star rating input and "Rate [Worker Name]" button are shown

**Given** the citizen submits a rating
**When** the API returns 200
**Then** the rating input is replaced with "Rating submitted. Thank you."

**Given** a verified worker appears in a list
**When** their card renders
**Then** a green "Society Verified" badge (`badge-verified` component from DESIGN.md) is shown next to their name

---

### Story 5.5: Federation Dashboard UI

As a **Ministry/NCCT evaluator**,
I want a read-only federation dashboard showing aggregate data and the full booking audit trail,
So that I can verify the cooperative economics and dispatch fairness without needing Swagger.

**Acceptance Criteria:**

**Given** any authenticated user visits `/federation`
**When** the page loads
**Then** three counters appear: "X registered workers", "Y completed bookings", and the Cooperative Welfare Fund total in a violet gradient card (UX-DR4)

**Given** completed bookings exist
**When** the user clicks on a booking in the federation list
**Then** the full offer audit trail is shown: worker name, rank, dispatch score (monospace), status — in offer order (UX-DR9)

**Given** the audit trail for the cascade demo booking (3 declines + 1 accept)
**When** the federation view shows it
**Then** each row shows the stored `dispatch_score`, making it clear why lower-earning workers ranked higher

---

### Story 5.6: Demo Reliability — End-to-End Validation

As a **team preparing the hackathon demo**,
I want a single manual test run that validates the entire cascade demo beat without any hardcoded data,
So that the demo fails safely if anything is wrong and we can fix it before presenting.

**Acceptance Criteria:**

**Given** the app is running with seed data
**When** the demo flow runs: Ravi (citizen) books → Suresh (rank 1) declines → Priya (rank 2) declines → Anil (rank 3) declines → Meena (rank 4) accepts → Meena marks complete → Ravi rates 4 stars
**Then** every step completes without a hardcoded response; `GET /booking-offers/booking/{id}` shows 4 offer rows with correct ranks and scores

**Given** Meena accepts the booking
**When** the wallet view is checked
**Then** Meena's `weekly_earnings` reflects the completed job price × 0.95

**Given** the booking is complete
**When** `GET /welfare-fund/summary` is called
**Then** `total_fees` increased by `job_price * 0.05`

**And** the WCAG 2.1 AA contrast requirement is met for all key screens (NFR-6) — manually verified using a browser accessibility audit
