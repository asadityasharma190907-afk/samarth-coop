# Samarth — Agent Instructions (AGENTS.md)

<!-- AGENTS-BLOCK-START: bmad-project-context | generated: 2026-08-29 -->

## Project: Samarth — Cooperative Gig Services Platform

**SIH Problem #26089** | Ministry of Cooperation / NCCT  
**Team:** 6 members | **Phase:** Planning complete → Implementation ready

---

## Where Things Are

| Artifact | Path |
|---|---|
| Product Brief | `_bmad-output/planning-artifacts/briefs/brief-Samarth-2026-08-29/brief.md` |
| PRD (17 FRs) | `_bmad-output/planning-artifacts/prds/prd-Samarth-2026-08-29/prd.md` |
| Architecture Spine (13 ADs) | `_bmad-output/planning-artifacts/architecture/architecture-Samarth-2026-08-29/ARCHITECTURE-SPINE.md` |
| Design System | `_bmad-output/planning-artifacts/ux-designs/ux-Samarth-2026-08-29/DESIGN.md` |
| Experience Spec | `_bmad-output/planning-artifacts/ux-designs/ux-Samarth-2026-08-29/EXPERIENCE.md` |
| Epics & Stories (5 epics, 26 stories) | `_bmad-output/planning-artifacts/epics.md` |
| Sprint Status | `_bmad-output/implementation-artifacts/sprint-status.yaml` |
| Backend source | `backend/` (not yet created — follow AD-9 directory layout) |
| Frontend source | `frontend/` (not yet created — follow AD-9 directory layout) |

---

## Stack (Architecture Decisions — binding, not suggestions)

- **Backend:** FastAPI (Python 3.11) + SQLAlchemy + Alembic + PostgreSQL 15
- **Frontend:** React 18 + Vite + TanStack Query v5 + vanilla CSS (no UI framework)
- **Auth:** JWT (HS256) + bcrypt (cost 12). No session cookies.
- **Dev environment:** Docker Compose only. `docker-compose up` is the one-and-only local dev command.
- **Migrations:** Alembic only. Never use `Base.metadata.create_all()` in production paths.
- **Design tokens:** All in `frontend/src/tokens.css` as CSS custom properties. No hardcoded hex values in component CSS.

---

## Non-Negotiable Architecture Rules

These are Architecture Decision records — violating them without a team decision is a spec violation:

1. **No `weekly_earnings` column on `worker_profiles`.** WeeklyEarnings is ALWAYS computed at query time from `bookings`. (AD-5)
2. **The accept path MUST use `with_for_update()` row lock.** Never read `booking.status` outside a transaction on the accept path. (AD-6)
3. **`booking_offers.dispatch_score` is immutable after INSERT.** Never update it. Never recompute it in the audit trail endpoint. (AD-7)
4. **No background task runner (Celery, APScheduler, cron).** Offer expiry is lazy-checked on every read/action. (AD-8)
5. **Exactly 4 tables for MVP:** `users`, `worker_profiles`, `bookings`, `booking_offers`. A 5th table requires a team decision and a new Alembic migration. (AD-9)
6. **No UI framework (no MUI, shadcn, Ant Design).** Custom components from DESIGN.md tokens only. (AD-3)

---

## Dispatch Algorithm — Canonical Implementation

The source of truth is `backend/app/services/dispatch.py`. Any deviation from the formula below is a bug:

```python
Score = (5000 − WeeklyEarnings) × 2
      + (1000 × Rating)           # Rating defaults to 4.0 if null
      − (500 × Distance_km)       # Haversine, 5km max radius
      − ReliabilityPenalty        # 3000 if acceptance_rate < 0.5 AND offers >= 5; else 0
```

WeeklyEarnings SQL pattern:
```sql
SELECT COALESCE(SUM(job_price * 0.95), 0)
FROM bookings
WHERE worker_id = :worker_id
  AND status = 'completed'
  AND created_at >= date_trunc('week', NOW());
```

---

## Milestone Gate (Epic 2 → Epic 3 boundary)

**Before ANY React component is committed:**

```bash
# Start the backend + DB
docker-compose up db backend

# Verify the dispatch ranking in Swagger
curl "http://localhost:8000/workers?skill=electrician&lat=26.9124&lng=75.7873"
# Expected order: Suresh Kumar (score ~12550) > Priya Gupta (~12000) > Anil Yadav (~9750) > Meena Verma (~5750)
```

This gate must pass before Epic 3 begins.

---

## Running the Project

```bash
# Full local dev environment
docker-compose up

# Seed the database (first run)
docker-compose exec backend python app/seed.py

# Run backend tests
docker-compose exec backend pytest

# Alembic migrations
docker-compose exec backend alembic upgrade head

# Frontend (if running outside Docker)
cd frontend && npm install && npm run dev
```

---

## Seed Data (Deterministic — do not change)

| Worker | Skill | Weekly Earnings | Rating | Distance from Jaipur center | Expected Rank |
|---|---|---|---|---|---|
| Suresh Kumar | electrician | ₹200 | 4.2 | 2.5 km | 1 |
| Priya Gupta | electrician | ₹0 (new) | null (cold-start → 4.0) | 4.0 km | 2 |
| Anil Yadav | electrician | ₹2,000 | 4.5 | 1.5 km | 3 |
| Meena Verma | electrician | ₹4,500 | 4.9 | 0.3 km | 4 |

Meena is closest and best-rated — she ranks last. This is intentional and is the core demo proof point.

---

## Key Invariants for AI Agents

- When implementing the accept endpoint, always check the story AC: two simultaneous accepts must produce one 200 and one 409. Never implement accept without the row lock.
- When implementing `GET /workers`, always join against `bookings` to compute weekly earnings. Never read a `weekly_earnings` column from `worker_profiles`.
- When creating a `booking_offers` row, always store `dispatch_score` and `rank_at_offer` at INSERT time. The audit trail reads these stored values — it does not recompute.
- When implementing offer expiry, check `expires_at` lazily on every read or action. Do not add a scheduler.
- The platform fee is always `job_price * 0.05`. Worker payout is always `job_price * 0.95`. These are hardcoded business rules for MVP — not configurable.

---

## Known Pitfalls (from architecture review)

- **Pitfall:** Using `datetime.now()` instead of `NOW()` in SQL for weekly earnings boundary. Use `date_trunc('week', NOW())` in the SQL query to ensure PostgreSQL's timezone-aware week boundary is used.
- **Pitfall:** Auto-importing SQLAlchemy models in `main.py` before Alembic runs. Always use `alembic upgrade head` before app startup in Docker entrypoint.
- **Pitfall:** React `useEffect` + `useState` for server state. Use TanStack Query hooks in `frontend/src/hooks/` — not raw `useEffect`.
- **Pitfall:** Hardcoding `job_price` as a local variable in a test rather than using the snapshotted value from the `bookings` table. Always read `booking.job_price`, never recompute it.

---

## GitHub Issues Mapping (planned — to be created after repo setup)

Each story in `epics.md` becomes one GitHub issue. Story IDs map to issue labels:
- Epic labels: `epic-1`, `epic-2`, `epic-3`, `epic-4`, `epic-5`
- Type labels: `backend`, `frontend`, `fullstack`, `infra`
- Priority labels: `p0-must-have`, `p1-should-have`, `p2-nice-to-have`
- Milestone: `Hackathon MVP` (due date = hackathon day)

<!-- AGENTS-BLOCK-END -->
