# Product Requirements Document — Samarth

**Cooperative Gig Services Platform for Household & Community Services**
Problem Statement #26089 — Ministry of Cooperation / National Council for Cooperative Training (NCCT)

---

## 1. Overview

**Product name:** Samarth
**One-line description:** A cooperative-owned digital marketplace that dispatches household service jobs (electricians, plumbers, domestic help) using a fairness-weighted algorithm that prioritizes workers who have earned the least in the current week — not just the closest or highest-rated.

**Why "Samarth":** the word means capable/empowered — the product's premise is that cooperative workers already have the skill and local presence; what they lack is structured, fair access to demand. Samarth is the access layer, not a skills program.

**Timeline:** 4–5 days of pre-hackathon build, then a 36-hour hackathon window for should-have features, polish, and rehearsal.

---

## 2. Problem Statement

Labour Cooperative Federations and Societies possess a large pool of verified, skilled workers, but lack a structured digital platform to connect them with households and institutions. Private gig platforms dominate the market and optimize purely for transaction volume — closest worker, highest rating — which structurally favors workers who are already doing well and leaves newer or currently-idle cooperative workers underutilized.

**Core insight driving the product:** fairness has to be a routing mechanism, not a policy statement. If the dispatch algorithm doesn't mathematically account for who hasn't been paid yet this week, "fair" is just marketing copy on top of the same winner-takes-all logic every other platform uses.

---

## 3. Goals & Non-Goals

### Goals (this build)
- Prove that a dispatch algorithm can measurably redistribute job opportunities toward lower-earning workers without abandoning quality (rating) or convenience (distance) as factors
- Give workers real agency — a worker can decline a job; declining cascades the offer, it does not remove them from the pool
- Keep the platform fee radically lower than private competitors (5% vs. private platforms' 20–30%) and route it to a visible, auditable Cooperative Welfare Fund
- Ship a complete, demoable transaction loop: registration → booking → offer → accept/decline → completion → payout — not a collection of disconnected screens

### Non-goals (explicitly out of scope for this build)
- Multilingual UI
- Native mobile app (React web app, mobile-responsive, is sufficient)
- Live GPS tracking (static coordinates only)
- AI-based demand forecasting
- Insurance integration
- OTP/2FA, email verification, password reset flows
- Real Aadhar-based worker verification (document upload/manual review)
- A full federation administration dashboard with write/admin actions (read-only summary only)

These are real features named in the original problem statement. They are not being ignored — they're consciously deferred so the fairness mechanism, which is the actual thesis of the product, gets built well rather than everything getting built shallowly.

---

## 4. Target Users & Personas

**Citizen / Customer** — a household needing a verified worker (e.g. an electrician) on short notice. Wants: fast matching, transparent pricing, trust that the worker is legitimate.
*Persona: Ravi Sharma, Jaipur resident, books a same-day electrician repair.*

**Cooperative Worker** — a skilled tradesperson registered with a Labour Cooperative Society. Wants: fair access to jobs regardless of tenure, the right to decline a job without penalty to their standing, visible and fast payout.
*Persona: Suresh Kumar, electrician, newer to the platform, has earned little this week — the system is designed to notice this and act on it.*
*Contrast persona: Meena Verma, top-rated, closest to most jobs, already earning well — the system deliberately deprioritizes her for this booking without penalizing her rating.*

**Federation Administrator** — oversees the cooperative's welfare fund and worker roster. Wants: visibility into fund growth and dispatch fairness, not necessarily manual control for this MVP.
*Persona: Ministry/NCCT evaluator, wants to see the welfare fund is real and auditable, not decorative.*

---

## 5. Core Product Loop

```
Citizen registers/logs in
  → browses service categories
  → requests a booking (skill + location)
  → Samarth computes a Dispatch Score for every available, verified worker in radius
  → job is OFFERED to the top-ranked worker (not auto-assigned)
  → worker can ACCEPT or DECLINE
      → decline: offer cascades to the next-ranked worker
      → accept: booking is locked, worker marked unavailable
  → worker marks job COMPLETE
  → payout (95%) credited to worker, platform fee (5%) credited to Cooperative Welfare Fund
  → citizen can rate the worker (should-have)
```

This loop — not any single screen — is the product. Every feature in this document exists to make this loop real, auditable, and honest under judging scrutiny.

---

## 6. Functional Requirements

### 6.1 The Dispatch Algorithm (P0 — the product's core differentiator)

```
Dispatch Score = (5000 − Weekly Earnings) × 2
               + (1000 × Rating)
               − (500 × Distance_km)
               − Reliability Penalty
```

- **Weekly Earnings** is computed at query time from completed bookings in the current calendar week (`date_trunc('week', NOW())`) — not a stored counter. This means the fairness mechanic resets itself every week automatically, with no scheduled job required.
- **Rating** defaults to `4.0` for workers with no rating history (cold start), so new workers aren't penalized for lacking a track record.
- **Distance** is Haversine-calculated against static registered coordinates; only workers within a 5km radius are scored.
- **Reliability Penalty**: a flat penalty applied when a worker's last 10 logged offers show an acceptance rate below 50% (waived for workers with fewer than 5 logged offers). This exists specifically to close the loophole where a worker could decline every job to permanently stay at ₹0 earned and dominate the queue — the fairness mechanism cannot be allowed to reward bad-faith non-participation.

**Verified independently at design time** against realistic seed values (see Appendix A) — the formula holds the "low earner wins" property across the full ₹0–5000 range, not just at the extremes.

### 6.2 Booking & Offer Cascade (P0)

A booking never auto-assigns. It is offered to the top-ranked worker, who has the right to decline. On decline, the system cascades to the next-ranked worker and logs the full history — which worker was offered, in what order, and why (via the stored `dispatch_score` and `rank_at_offer` on every offer record). If every in-radius worker declines, the booking is marked cancelled rather than silently failing.

This is the feature that actually earns the word "cooperative" — a platform that only ever auto-assigns is a routing engine wearing cooperative branding.

### 6.3 Identity & Access (P0)

Real registration and login for both citizens and workers — hashed passwords (bcrypt/argon2), no OTP or email verification for this build. Each role sees a distinct set of screens (citizen: booking flow; worker: offer inbox, wallet).

### 6.4 Worker Wallet & Economic Ledger (P0)

Each worker can see completed jobs and their running payout total. The 95/5 split is computed from `job_price`, which is a flat, category-based rate snapshotted onto the booking at creation time (not a live pricing engine — that's out of scope). The platform fee accumulates into a Cooperative Welfare Fund total, visible to the citizen and to the federation view.

### 6.5 Worker Verification (P1 — should-have)

A `verified` boolean per worker, controllable via a simple toggle screen (standing in for real Aadhar-linked cooperative registration review). Displayed to citizens as a "Society Verified" badge. Not a document upload/approval workflow.

### 6.6 Ratings & Feedback (P1 — should-have)

After a job is marked complete, the citizen can submit a 1–5 rating, which updates the worker's `rating` field — this is what makes the dispatch algorithm's rating term reflect real data over time rather than only ever showing seed values.

### 6.7 Federation / Ministry View (P2 — could-have)

A read-only summary screen: total workers, total bookings, cumulative welfare fund. No admin write actions for this build.

### 6.8 In-app Notifications (P2 — could-have)

Simple in-app state changes ("your offer was accepted/declined") — no push or SMS infrastructure.

---

## 7. Non-Functional Requirements

- **Auditability:** every dispatch decision must be traceable — the `dispatch_score` a worker had at the moment of an offer is stored, not recomputed after the fact. This is a judging-defensibility requirement as much as an engineering one.
- **Determinism for demo:** the seed dataset and dispatch math must produce the same ranking every time (Suresh > Priya > Anil > Meena) — no reliance on live external data (GPS, payment gateways) that could fail during a live presentation.
- **Data integrity under concurrency:** accepting an offer is guarded by a row lock, preventing two simultaneous accepts on the same booking.
- **Graceful degradation:** an unresponsive worker's offer expires (lazily checked, no background scheduler needed) rather than stalling the booking indefinitely.

---

## 8. Data Model (summary — full DDL in `architecture.md`)

| Table | Purpose |
|---|---|
| `users` | Citizens and workers, role-flagged, real hashed passwords |
| `worker_profiles` | Skill, static location, rating (nullable = cold start), availability, verification flag — no stored earnings column |
| `bookings` | One row per service request; snapshotted job price, platform fee set on completion, status lifecycle `pending → assigned → completed / cancelled` |
| `booking_offers` | Full cascade audit trail — every worker offered, their rank and score at offer time, and the outcome |

---

## 9. API Surface (summary — full contract in `architecture.md`)

```
POST /auth/register, POST /auth/login
GET  /workers?skill=&lat=&lng=
POST /bookings
PUT  /booking-offers/{id}          {action: accept | reject}
GET  /booking-offers/booking/{id}
PUT  /bookings/{id}/complete
GET  /wallet/{worker_id}
GET  /welfare-fund/summary
```

---

## 10. Success Metrics (for this build)

Since this is a hackathon MVP, not a production launch, success is measured by demo integrity, not usage numbers:

- The dispatch ranking is provably correct against seed data, on demand, in Swagger — before any UI exists
- A judge can watch a live decline-and-cascade happen (Meena declines → Suresh receives the offer) and see the audit trail explaining why
- The full loop — register → book → offer → decline → cascade → accept → complete → wallet updates → fund updates — runs without a single hardcoded/faked step
- Feasibility questions (scaling, gaming the algorithm) have real, stated answers — either built (reliability penalty, row locking, offer expiry) or explicitly named as a documented v2 path (PostGIS, empty-cascade fallback)

---

## 11. Known Limitations (stated deliberately, not hidden)

- Flat per-category pricing, not a negotiated or dynamic rate
- No PostGIS spatial indexing — fine at demo scale (4 workers), a named bottleneck at city scale
- No push/SMS notifications, in-app only
- Worker verification is a manual toggle, not a document-review workflow
- If every in-radius worker declines a booking, it cancels rather than auto-widening the search radius — mitigated for demo via seed-data discipline, named as a production gap

---

## 12. Appendix A — Dispatch Score Verification (seed data)

Customer location: Jaipur city center. All four workers: `electrician`, within 5km.

| Worker | Weekly Earnings | Rating | Distance | Dispatch Score | Rank |
|---|---|---|---|---|---|
| Suresh Kumar | ₹200 | 4.2 | 2.5 km | **12,550** | 1 |
| Priya Gupta | ₹0 (new, cold-start rating 4.0) | 4.0 | 4.0 km | **12,000** | 2 |
| Anil Yadav | ₹2,000 | 4.5 | 1.5 km | **9,750** | 3 |
| Meena Verma | ₹4,500 | 4.9 (best) | 0.3 km (closest) | **5,750** | 4 |

Meena — best-rated, closest — ranks last, because she has already earned the most this week. This is the exact proof point the product exists to demonstrate.

---

## 13. Roadmap Reference

Full epic breakdown (EPIC-1 through EPIC-8), phased build plan, and cut order are maintained separately in `roadmap.md` to keep this PRD focused on *what* and *why* rather than *when* and *who*.
