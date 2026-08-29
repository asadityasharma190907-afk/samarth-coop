---
title: "PRD: Samarth — Cooperative Gig Services Platform"
status: final
created: 2026-08-29
updated: 2026-08-29
project: Samarth
problem_statement: "SIH #26089 — Ministry of Cooperation / NCCT"
---

# PRD: Samarth — Cooperative Gig Services Platform

## 1. Vision

### 1.1 Problem

India's Labour Cooperative Federations and Societies have a verified, locally-rooted workforce of skilled tradespeople — electricians, plumbers, carpenters, domestic helpers, caregivers, drivers. The gap is not supply. The gap is structured digital access to demand.

Private gig platforms (Urban Company and equivalents) fill this demand today, but they optimize for transaction volume: route to the closest, highest-rated worker. This structurally concentrates work toward workers already doing well and leaves newer, currently-idle cooperative members systematically underutilised. Fairness is a PR statement on top of winner-takes-all routing logic.

**The SIH problem statement (PS-26089) mandates a cooperative digital platform that actually addresses this.** The question the platform must answer is not "can we build a booking app" — it is "can fairness be a routing mechanism, not a policy claim?"

### 1.2 Solution

Samarth is a cooperative-owned digital marketplace for household and community services. Its core differentiator is the **Dispatch Algorithm** — a fairness-weighted formula that routes the next job offer to the worker who has earned the least this week, not just the closest or best-rated. This is not a UI preference; it is the mathematical mechanism that makes the cooperative promise real and auditable.

### 1.3 Why Now

SIH 2026 Problem Statement #26089 is a live, evaluated mandate from the Ministry of Cooperation and NCCT. The platform must be demoable in a 36-hour hackathon window with a 4–5 day pre-build runway. The MVP's primary audience is evaluating judges, not production users — which means the correctness of the dispatch mechanism is more important than feature breadth.

---

## 2. User Journeys

### UJ-1: Citizen Books a Service
**Ravi Sharma**, Jaipur resident. His bathroom tap broke this morning. He opens Samarth, registers with name + phone + password, selects "Plumber", enters his address (or uses the map pin), and submits a booking request.

The system computes a Dispatch Score for every verified plumber within 5km, ranks them, and sends an offer (not an auto-assignment) to the top scorer. Ravi sees a "Finding a worker…" status. Within seconds (on demo seed data), a worker accepts. Ravi sees the worker's name, cooperative badge, rating, and estimated arrival time. He gets a payout summary after the job: ₹X to the worker, ₹Y to the Cooperative Welfare Fund.

**Edge case:** if every eligible worker declines, Ravi sees "No workers accepted — please retry or try a different area" rather than a silent failure.

### UJ-2: Worker Receives and Handles a Job Offer
**Suresh Kumar**, electrician, cooperative-registered, has earned ₹200 this week. He opens his Samarth worker dashboard. An offer card arrives: "Booking from Ravi Sharma — Electrical repair, 2.3km away, ₹500." He sees two buttons: Accept and Decline.

He accepts. The booking is locked — Suresh is marked unavailable. He completes the job on-site, taps "Mark Complete" in the app. His wallet updates: ₹475 (95%) credited. The Cooperative Welfare Fund counter increments by ₹25.

**Decline path:** if Suresh declines, the offer cascades to the next-ranked worker. Suresh's rating is unaffected. If his last 10 offers show < 50% acceptance (and he's had ≥ 5 offers total), a reliability penalty applies to his future dispatch scores — this closes the gaming loophole.

### UJ-3: Meena Verma Gets Ranked Last
**Meena Verma**, top-rated electrician (4.9★), 0.3km from the booking site — the closest and best-rated worker available. She ranks **4th** in the Dispatch Score for this booking because she has already earned ₹4,500 this week. The algorithm deliberately deprioritises her without penalising her rating or removing her from the pool.

This is the product's proof-of-concept moment — the one scenario a judge must witness.

### UJ-4: Federation Admin Reviews the Fund
**Ministry evaluator** (NCCT) opens the federation view. They see: total registered workers, total completed bookings this month, cumulative Cooperative Welfare Fund balance. They can see the dispatch offer trail for any booking — which worker was offered first, why (dispatch score at time of offer), what happened. The data is read-only — no admin write actions for this build.

---

## 3. Glossary

- **Booking** — A citizen's service request. One booking can generate multiple Offers via cascade. Lifecycle: `pending → assigned → completed | cancelled`.
- **Offer** — An invitation to a specific worker to accept a specific Booking. Not an auto-assignment. One row per offer in `booking_offers`; the dispatch score and rank at time of offer are stored immutably.
- **Dispatch Score** — A numeric score computed per worker per booking at query time. Determines the order in which workers are offered a booking. Formula: `(5000 − WeeklyEarnings) × 2 + (1000 × Rating) − (500 × Distance_km) − ReliabilityPenalty`.
- **WeeklyEarnings** — The sum of `job_price × 0.95` for all `completed` bookings assigned to a worker since the most recent Monday 00:00 UTC. Computed at query time; never stored as a mutable counter. Resets automatically each week.
- **Cascade** — The process of offering a booking sequentially to ranked workers after a decline, until one accepts or all decline. The full sequence is logged.
- **ReliabilityPenalty** — A flat score deduction (−3,000 points) applied to a worker's Dispatch Score when their last 10 offers show an acceptance rate < 50% and they have ≥ 5 total logged offers. Waived for newer workers.
- **Cooperative Welfare Fund (CWF)** — The accumulated 5% platform fee from all completed bookings. A real, running total, not decorative. Visible in the federation view.
- **Cold-start Rating** — A worker with no completed/rated jobs defaults to a Rating of 4.0 for dispatch scoring purposes, ensuring new workers are not penalised by lack of history.
- **Worker** — A cooperative-registered tradesperson. Can receive Offers, accept or decline, mark jobs complete, and view their Wallet.
- **Citizen** — A household or institution requesting a service. Can browse, book, and rate a completed job.

---

## 4. Features

### 4.1 Authentication & Identity

**Description:** Real registration and login for Citizens and Workers. Each role sees a distinct set of screens. Passwords are hashed (bcrypt). No OTP, email verification, or password-reset flows for this build.

**Functional Requirements:**

#### FR-1: Citizen Registration
A Citizen can register with name, phone number, and password. The system creates a user record with `role: citizen` and returns a session token on success.

**Consequences (testable):**
- `POST /auth/register` with valid payload returns HTTP 201 and a JWT token.
- Duplicate phone number returns HTTP 409.
- Password is stored hashed — plain text never persists.

#### FR-2: Worker Registration
A Worker can register with name, phone, skill category (from a fixed list: electrician, plumber, carpenter, painter, domestic helper, caregiver, driver, gardener, cleaner, technician), and static latitude/longitude. The system creates a user + `worker_profiles` record. Verified flag defaults `false`.

**Consequences (testable):**
- `POST /auth/register` with `role: worker` and skill/location payload returns HTTP 201.
- Worker appears in `GET /workers` results only when `verified: true`.

#### FR-3: Login
Both roles authenticate with phone + password. System returns a JWT. Role is embedded in the token so the frontend can route to the correct dashboard.

**Consequences (testable):**
- `POST /auth/login` with valid credentials returns HTTP 200 + JWT.
- Invalid credentials return HTTP 401.

---

### 4.2 Worker Discovery & Dispatch Algorithm

**Description:** When a citizen requests a booking, the system computes a Dispatch Score for every eligible worker and ranks them. Eligibility requires: `verified: true`, same skill category as requested, within 5km of the citizen's location, `availability: true`. Realizes UJ-1, UJ-3.

**Functional Requirements:**

#### FR-4: Worker List with Dispatch Score
The system can return a ranked list of eligible workers for a given skill and location, each annotated with their computed Dispatch Score, WeeklyEarnings at time of query, and whether the cold-start default is active.

**Consequences (testable):**
- `GET /workers?skill=electrician&lat=26.9&lng=75.8` returns workers sorted by Dispatch Score descending.
- Workers with `verified: false` or `availability: false` are excluded.
- Workers > 5km from the request location are excluded.
- `weekly_earnings`, `dispatch_score`, `rating_is_default` are present in every worker row.

#### FR-5: Dispatch Score Formula
The Dispatch Score is computed as:

```
Score = (5000 − WeeklyEarnings) × 2
      + (1000 × Rating)
      − (500 × Distance_km)
      − ReliabilityPenalty
```

Where:
- `WeeklyEarnings` is computed at query time from `bookings` where `worker_id = :id AND status = 'completed' AND created_at >= date_trunc('week', NOW())`.
- `Rating` defaults to `4.0` if `worker_profiles.rating IS NULL`.
- `Distance` is the Haversine great-circle distance between the worker's registered coordinates and the booking's coordinates.
- `ReliabilityPenalty` is `3000` if the worker's last 10 offers show acceptance rate < 50% AND total offers ≥ 5; else `0`.

**Consequences (testable):**
- Appendix A seed data must produce ranking Suresh (1) > Priya (2) > Anil (3) > Meena (4) deterministically.
- A worker with `weekly_earnings = 0` and `rating = 4.0` and `distance = 0` has a score of 14,000 (before penalty).

#### FR-6: Reliability Penalty Flag
The system exposes `reliability_penalty_applied: bool` in the worker response so the UI can display it transparently (same pattern as `rating_is_default`).

---

### 4.3 Booking & Offer Cascade

**Description:** A booking is never auto-assigned. The system offers it sequentially to ranked workers. Every offer is logged immutably — the dispatch score and rank at the time of offer are preserved. Realizes UJ-1, UJ-2.

**Functional Requirements:**

#### FR-7: Create Booking
An authenticated Citizen can create a booking with: skill category, location (lat/lng), optional description. The system stores the booking with `status: pending` and snapshots the `job_price` from the category rate table at creation time (not a live pricing engine).

**Consequences (testable):**
- `POST /bookings` returns HTTP 201 with booking ID and `status: pending`.
- `job_price` is snapshotted from the category table at creation time and does not change after booking is created.

#### FR-8: Initial Offer Dispatch
On booking creation, the system computes the ranked worker list, creates an offer record for the top-ranked worker in `booking_offers` (storing `worker_id`, `rank_at_offer`, `dispatch_score`), and sets its `status: offered` and `expires_at: NOW() + 2 minutes`.

**Consequences (testable):**
- A new row in `booking_offers` with the correct `dispatch_score` and `rank_at_offer = 1` is created.

#### FR-9: Worker Accept
An authenticated Worker can accept an offered booking. The system:
1. Acquires a row-level lock on the booking record.
2. Confirms `booking.status = 'pending'`; returns HTTP 409 if not.
3. Updates `booking.status = 'assigned'`, `booking.worker_id`.
4. Marks the offer record `status: accepted`.
5. Sets the worker's `availability: false`.

**Consequences (testable):**
- Two simultaneous accepts for the same booking result in one HTTP 200 and one HTTP 409.
- Worker is no longer returned in `GET /workers` results after accepting.

#### FR-10: Worker Decline / Offer Cascade
An authenticated Worker can decline an offer. The system:
1. Marks the current offer `status: declined`.
2. Identifies the next-ranked eligible worker.
3. Creates a new offer record for that worker.
4. If no eligible workers remain, sets `booking.status = 'cancelled'`.

**Consequences (testable):**
- After decline, a new offer row with `rank_at_offer = N+1` is created within one API call.
- If all workers decline, `booking.status = 'cancelled'`.

#### FR-11: Offer Expiry (lazy)
When an offer is read or acted on, the system checks if `now() > expires_at` and `status = 'offered'`. If so, it marks the offer `expired` and triggers the cascade before processing any further action. No background scheduler is needed.

**Consequences (testable):**
- An offer with `expires_at` in the past is automatically expired and cascaded on the next API call touching it.

---

### 4.4 Job Completion & Worker Wallet

**Description:** The Worker marks a job complete. The system computes the payout split and updates the Cooperative Welfare Fund. The Worker's wallet shows all completed jobs and running totals. Realizes UJ-2.

**Functional Requirements:**

#### FR-12: Mark Complete
An authenticated Worker assigned to a booking can mark it complete. The system sets `booking.status = 'completed'`, computes `platform_fee = job_price × 0.05`, and stores it.

**Consequences (testable):**
- `PUT /bookings/{id}/complete` returns HTTP 200.
- `booking.platform_fee = job_price × 0.05` is stored.
- Worker's `availability` is reset to `true`.

#### FR-13: Worker Wallet View
An authenticated Worker can view their completed bookings and running payout total. `WeeklyEarnings` and lifetime earnings are both derived at query time from `bookings`.

**Consequences (testable):**
- `GET /wallet/{worker_id}` returns a list of completed bookings with job prices, and `weekly_earnings` (current week only).

#### FR-14: Cooperative Welfare Fund Summary
Any authenticated user can view the cumulative Cooperative Welfare Fund balance (sum of all `platform_fee` from `completed` bookings) and the total number of completed bookings.

**Consequences (testable):**
- `GET /welfare-fund/summary` returns `{ total_fees: number, completed_bookings: number }`.

---

### 4.5 Worker Verification Badge

**Description:** Workers have a `verified` boolean field, togglable via an admin endpoint (standing in for real cooperative registration review). Citizens see a "Society Verified" badge on verified workers. Realizes UJ-4. P1 priority.

**Functional Requirements:**

#### FR-15: Verification Toggle
An admin user (or simplified: any worker-manager endpoint) can toggle a worker's `verified` flag. Unverified workers do not appear in dispatch results.

**Consequences (testable):**
- Worker with `verified: false` does not appear in `GET /workers` results.
- After toggle to `verified: true`, worker appears in results.

---

### 4.6 Citizen Rating

**Description:** After a job is marked complete, the Citizen can submit a 1–5 star rating for the Worker. This updates `worker_profiles.rating` and feeds back into future Dispatch Score calculations. P1 priority.

**Functional Requirements:**

#### FR-16: Submit Rating
An authenticated Citizen who had a booking completed can submit a 1–5 integer rating for that booking's worker. The system updates the worker's `rating` field (average of all ratings received).

**Consequences (testable):**
- `POST /bookings/{id}/rating` with `{ rating: 4 }` returns HTTP 200.
- `worker_profiles.rating` updates to the new average.
- A citizen cannot rate the same booking twice (HTTP 409 on duplicate).

---

### 4.7 Offer Audit Trail / Federation View

**Description:** The federation/admin view exposes booking offer history — who was offered, in what order, at what score. Read-only. Realizes UJ-4.

**Functional Requirements:**

#### FR-17: Offer History
Any authenticated user can retrieve the full offer trail for a given booking: list of workers offered, rank at time of offer, dispatch score at time of offer, outcome (accepted/declined/expired).

**Consequences (testable):**
- `GET /booking-offers/booking/{booking_id}` returns the ordered list of offer records.
- `dispatch_score` on each record matches the score that was computed at time of offer (immutable).

---

## 5. Non-Goals (Explicit)

- **No native mobile app.** Mobile-responsive web is sufficient.
- **No multilingual UI.** English only for this build.
- **No OTP / 2FA / email verification.** Phone + password only.
- **No real Aadhaar-based verification.** The `verified` toggle is the stub.
- **No live GPS tracking.** Static registered coordinates only.
- **No AI demand forecasting.** Dispatch is algorithmic, not predictive.
- **No insurance integration.** Named as a future subsystem.
- **No dynamic / negotiated pricing.** Flat per-category rates.
- **No federation admin write actions.** Read-only summary only.
- **No push / SMS notifications.** In-app state changes only.
- **No PostGIS spatial indexing.** Haversine at demo scale is sufficient; PostGIS is a named v2 path.

---

## 6. MVP Scope

### 6.1 In Scope (P0 — pre-hackathon build)
- Registration and login for both roles
- Booking creation with category and location
- Dispatch Score computation and worker ranking
- Offer dispatch to top-ranked worker
- Accept / Decline with cascade
- Offer expiry (lazy) and row-lock on accept
- Job completion with 95/5 payout split
- Worker wallet view
- Cooperative Welfare Fund running total
- Seed data: 4 workers, deterministic ranking, verifiable in Swagger
- Complete offer audit trail per booking

### 6.2 In Scope (P1 — hackathon window)
- Citizen rating (1–5 stars) feeding back into dispatch
- Worker verification toggle + badge
- Reliability penalty (anti-gaming, built not just documented)
- Federation read-only summary view

### 6.3 Out of Scope for MVP
- Multilingual UI `[NOTE FOR PM: high impact post-hackathon, cooperative's base is non-English]`
- Native mobile app `[NOTE FOR PM: most workers will use smartphones — PWA or React Native in v2]`
- PostGIS spatial indexing `[named scaling bottleneck at city scale, addendum has migration path]`
- Dynamic pricing engine `[new subsystem, not a column addition]`
- Insurance integration `[new subsystem]`
- Real Aadhaar verification workflow

---

## 7. Success Metrics

**Primary**
- **SM-1:** Full transaction loop completes without any hardcoded/faked step — register → book → offer → cascade → accept → complete → wallet → fund. Validates FR-7 through FR-14.
- **SM-2:** Dispatch ranking for Appendix A seed data is correct on demand in Swagger: Suresh (1) > Priya (2) > Anil (3) > Meena (4). Validates FR-4, FR-5.
- **SM-3:** Offer cascade happens live in demo: one decline triggers the next offer in the same API call, visible in the audit trail. Validates FR-10, FR-17.

**Secondary**
- **SM-4:** Judge can verify the Cooperative Welfare Fund balance is real (computed from actual completed bookings, not hardcoded). Validates FR-14.
- **SM-5:** Reliability penalty is demonstrable — a worker with > 50% decline rate on their last 10 offers receives a lower dispatch score. Validates FR-5, FR-6.

**Counter-metrics (do not optimise)**
- **SM-C1:** Do not optimise for feature count at the expense of loop correctness. A broken cascade is worse than a missing rating feature.
- **SM-C2:** Do not optimise dispatch toward speed by auto-assigning — the offer/cascade structure must be preserved.

---

## 8. Cross-Cutting Non-Functional Requirements

- **Auditability:** Every dispatch decision stores `dispatch_score` and `rank_at_offer` at the time of offer — immutable. A judge reviewing a booking 3 days after the demo sees the same scores that drove the decision.
- **Determinism:** The seed dataset and dispatch math must produce the same ranking every time. No reliance on live external data (GPS, payment gateways, real-time APIs) that could fail during a live presentation.
- **Data integrity under concurrency:** `PUT /booking-offers/{id}` (accept path) uses a row-level lock (`SELECT ... FOR UPDATE`) to prevent two simultaneous accepts on the same booking.
- **Graceful offer expiry:** An offer with a past `expires_at` is lazily expired and cascaded on the next API call — no background scheduler required.
- **Password security:** Passwords stored with bcrypt (cost factor ≥ 12). Plain text never written to logs or database.

---

## 9. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Gaming the algorithm (decline everything, stay at ₹0) | Medium | High | ReliabilityPenalty (FR-5, FR-6) — built, not just documented |
| weekly_earnings counter drift | — | — | Eliminated: computed at query time from completed bookings, no stored counter |
| Accept race condition | Low (demo) / High (prod) | High | Row lock on accept (FR-9) — built |
| Offer stall (no response) | Low (manual demo) | Medium | Lazy expiry + cascade (FR-11) — built |
| PostGIS bottleneck at scale | N/A for demo | — | Named limitation; Haversine sufficient for 4-worker demo |
| Empty cascade (all workers decline) | Low (seed data controlled) | Medium | Booking status → `cancelled` with explicit message (FR-10); seed data guarantees one acceptor |

---

## 10. Open Questions

1. **Rating aggregation method:** Current spec uses simple average. Should there be recency weighting (recent ratings count more) in v2? `[Deferred to v2]`
2. **Category pricing table:** Where does the flat per-category rate come from — hardcoded seed, admin-editable table, or configurable config? `[Assumption: hardcoded seed for MVP; admin-editable in v2]`
3. **Worker availability flag:** Currently a manual boolean on `worker_profiles`. In v2, should it auto-set based on active booking status? `[Assumption: auto-set in v2 based on `booking.status = 'assigned'`]`

---

## 11. Assumptions Index

- **A-1:** Category pricing is flat and hardcoded for MVP (not user-negotiated, not admin-editable).
- **A-2:** Worker coordinates are static (registered address), not live GPS.
- **A-3:** The demo will use 4 seed workers and 2 seed citizens — enough to demonstrate the cascade (one decline, one accept).
- **A-4:** "Weekly" means the current ISO calendar week (Monday 00:00 UTC to Sunday 23:59 UTC), as computed by `date_trunc('week', NOW())` in PostgreSQL.
- **A-5:** Authentication is phone + password only. No session management beyond JWT.
- **A-6:** The reliability penalty threshold (< 50% acceptance in last 10 offers, with ≥ 5 offers as grace) is a reasonable anti-gaming bound for MVP; recalibration is a named v2 item.

---

## Appendix A — Dispatch Score Verification

Citizen location: Jaipur city center (26.9124° N, 75.7873° E). All four workers: `electrician`, `verified: true`, `availability: true`.

| Worker | WeeklyEarnings | Rating | Distance | ReliabilityPenalty | Dispatch Score | Rank |
|---|---|---|---|---|---|---|
| Suresh Kumar | ₹200 | 4.2 | 2.5 km | 0 | `(5000−200)×2 + 1000×4.2 − 500×2.5` = **12,550** | **1** |
| Priya Gupta | ₹0 (new) | 4.0 (cold-start) | 4.0 km | 0 | `(5000−0)×2 + 1000×4.0 − 500×4.0` = **12,000** | **2** |
| Anil Yadav | ₹2,000 | 4.5 | 1.5 km | 0 | `(5000−2000)×2 + 1000×4.5 − 500×1.5` = **9,750** | **3** |
| Meena Verma | ₹4,500 | 4.9 (best) | 0.3 km (closest) | 0 | `(5000−4500)×2 + 1000×4.9 − 500×0.3` = **5,750** | **4** |

Meena — best-rated and closest — ranks **last** because she has already earned the most this week. This is the exact proof point the product exists to demonstrate and is verifiable in Swagger before any UI exists.
