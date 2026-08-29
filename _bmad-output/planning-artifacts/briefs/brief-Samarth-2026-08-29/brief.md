---
title: "Product Brief: Samarth"
status: final
created: 2026-08-29
updated: 2026-08-29
---

# Product Brief: Samarth

> *"Samarth" means capable / empowered. The product's premise is that cooperative workers already have the skill and local presence — what they lack is structured, fair access to demand. Samarth is the access layer, not a skills program.*

---

## Executive Summary

Samarth is a cooperative-owned digital marketplace for household and community services — electricians, plumbers, domestic helpers, carpenters, caregivers, and more — built on a foundational insight that competing gig platforms have deliberately ignored: **fairness has to be a routing mechanism, not a policy statement.**

India's Labour Cooperative Federations and Societies already have the workforce. Tens of thousands of verified, skilled tradespeople are registered with these bodies. The gap is not supply — it is structured digital access to demand. Private gig platforms (Urban Company, TaskRabbit clones) serve this market today, but they optimize purely for the platform's transaction volume: closest worker, highest rated. The structural outcome is winner-takes-all: the already-busy worker gets busier, the newer or recently-idle cooperative member gets nothing.

Samarth solves this by embedding fairness into the dispatch algorithm itself. A worker who has earned ₹200 this week mathematically outranks a worker who has earned ₹4,500 — even if the ₹4,500 worker is closer and better rated. The algorithm is not a PR claim; it is an auditable formula whose output is stored on every booking offer so any evaluator can verify the decision after the fact.

The platform is being built for **SIH Problem Statement #26089**, sponsored by the Ministry of Cooperation / National Council for Cooperative Training (NCCT). The MVP targets a 36-hour hackathon window with a 4–5 day pre-build runway, with a 6-person team.

---

## The Problem

**Structural exclusion by algorithm.** Cooperative workers — who are formally registered, often more trustworthy than gig-economy anonymous contractors, and explicitly the target of a national cooperative development mandate — are underserved by every existing digital platform. The platforms that could serve them are not designed for fairness; they are designed for speed and volume, which reinforces seniority bias.

**No cooperative-specific digital infrastructure exists.** Labour Cooperative Federations have rosters, but no dispatch system. They manage job assignments manually or informally. This means:
- A household in Jaipur needing a certified plumber today cannot find one from their local cooperative digitally — they call Urban Company instead.
- A cooperative plumber sitting idle this week has no visibility and no channel to receive demand, even though they are formally verified and locally present.

**The fairness gap is a mechanism problem, not a policy problem.** Every cooperative platform that has tried to address this with "our values are fair" messaging fails because the underlying algorithm still routes to the top earner. Goodwill does not override a sorted list.

**Specific pain Samarth addresses:**
- Worker: *"I'm verified, available, and local — but I never get the call because Meena has more reviews."*
- Citizen: *"I want to hire from the cooperative, but there's no platform to do that — I have to use an app that doesn't care where my money goes."*
- Federation admin: *"We have a welfare fund on paper. We have no digital proof it's real or growing."*

---

## The Solution

Samarth is a full-transaction-loop web platform (mobile-responsive, no native app needed) that connects citizens requesting household services to cooperative-verified workers, dispatched by a fairness-weighted algorithm.

**The core loop:**
```
Citizen requests a service
  → Samarth scores every eligible worker by: fairness (weekly earnings) + quality (rating) + convenience (distance)
  → Job is OFFERED to the top scorer — not auto-assigned
  → Worker can ACCEPT or DECLINE (decline cascades to the next worker, not a penalty)
  → Accepted → worker completes job → 95% payout to worker, 5% to Cooperative Welfare Fund
  → Citizen rates worker → feeds back into future dispatch scores
```

**The dispatch formula:**
```
Score = (5000 − WeeklyEarnings) × 2 + (1000 × Rating) − (500 × Distance_km) − ReliabilityPenalty
```

Weekly earnings reset automatically every Monday (computed from completed bookings, not stored as a counter). Rating defaults to 4.0 for new workers (cold-start fairness). The reliability penalty closes the gaming loophole: a worker cannot idle at ₹0 forever to dominate the queue — if they decline more than half of the last 10 offered jobs, they take a score hit.

**What makes the offer-cascade differentiating:** A platform that auto-assigns is a routing engine with cooperative branding. Samarth preserves worker agency — the right to decline — while making that right auditable. Every offer, its rank, its score at time of offer, and its outcome is logged. A judge (or federation administrator) can trace exactly why worker A was offered the job before worker B.

---

## What Makes This Different

| Factor | Private Platforms | Samarth |
|---|---|---|
| Dispatch logic | Closest + highest rated | Fairness-weighted (earnings reset weekly) |
| Worker agency | Auto-assign or reject (penalty) | Offer cascade — decline without score penalty |
| Platform fee | 20–30% | 5% → Cooperative Welfare Fund |
| Auditability | Black box | Full offer trail stored on every booking |
| Who it serves | Workers already doing well | Workers who need the work most |

**The honest moat:** This is not a technical moat. The algorithm is simple enough to reproduce. The moat is institutional: this platform is specifically designed to serve cooperative registration structures, welfare fund accounting, and the ministry's cooperative development mandate — things Urban Company has no reason to care about and no data model to support.

---

## Who This Serves

**Citizen / Customer** — A household needing a verified worker on short notice. Wants: fast matching, transparent pricing, confidence the worker is legitimate. Does not care about the cooperative structure; cares that it works.
> *Persona: Ravi Sharma, Jaipur. Needs an electrician today. Books on Samarth because cooperative workers are verified and the platform fee is lower.*

**Cooperative Worker** — A skilled tradesperson registered with a Labour Cooperative Society. Wants: fair access to jobs regardless of how long they've been on the platform, the right to say no without losing standing, fast payout visibility.
> *Persona: Suresh Kumar — electrician, newer to the platform, earned ₹200 this week. The algorithm routes the next booking to him first. This is the product's proof of concept.*
> *Contrast: Meena Verma — best-rated, closest. Ranks last on this booking because she's already earned ₹4,500 this week. She does not lose rating; she simply waits for next week's reset.*

**Federation Administrator / Ministry Evaluator** — Wants: proof the welfare fund is real and auditable, visibility into dispatch fairness, worker roster. Does not need write/admin actions for this build.

---

## Success Criteria

**For the hackathon MVP:**
- The dispatch ranking is provably correct against seed data — verifiable in Swagger before any UI exists
- A live judge can watch the offer cascade happen (Meena declines → Suresh receives the offer) and see the audit trail
- The full loop runs without a single hardcoded or faked step: register → book → offer → decline → cascade → accept → complete → wallet updates → welfare fund updates
- Feasibility questions have real, stated answers — not "we'll look at it later"

**For V1 post-hackathon:**
- 100 cooperative workers onboarded in one city
- Booking-to-completion rate > 80%
- Worker Gini coefficient on weekly earnings demonstrably lower than control (private platform equivalent)

---

## Scope

**In for MVP (P0 — must have):**
- Registration and login (citizens + workers), real hashed passwords
- Booking flow: service category, location, job request
- Dispatch algorithm with full offer cascade and audit trail
- Worker offer inbox: accept / decline
- Worker wallet: completed jobs, payout total, 95/5 split display
- Cooperative Welfare Fund total (visible to citizen and federation view)
- Seed data proving the dispatch math: 4 workers, deterministic ranking every time

**In for hackathon window (P1 — should have):**
- Worker verification badge (manual toggle, not a document workflow)
- Post-completion rating by citizen (feeds back into future dispatch)
- Reliability penalty (anti-gaming mechanism, built not just documented)
- Offer expiry with lazy timeout (no background scheduler needed)
- Row lock on accept (race condition protection)

**Explicitly out of scope:**
- Native mobile app (responsive web sufficient)
- Multilingual UI
- OTP / 2FA / email verification
- Real Aadhaar-based document verification workflow
- Live GPS tracking
- AI demand forecasting
- Insurance integration
- Dynamic / negotiated pricing
- Federation admin write actions

**Deferred (explicitly named, not forgotten):**
- PostGIS spatial indexing (named scaling bottleneck at city scale)
- Dynamic pricing engine (new subsystem, not a column addition)
- Insurance integration (new subsystem, not an addon)

---

## Vision

In three years: Samarth is the operating system for India's 300,000+ registered cooperative workers — the platform that converted the government's cooperative mandate from a policy paper into a transaction network. Federation administrators use it to manage rosters, track welfare fund disbursements, and run verification workflows. Workers use it as their primary income channel. Citizens use it because it is trustworthy, fairly priced, and worker-verified in a way no private platform can credibly claim.

The fairness algorithm scales from 4 workers in a Jaipur demo to city-scale dispatch with PostGIS spatial indexing and dynamic radius widening. The 5% welfare fund becomes a real financial instrument — cooperative members receive year-end distributions backed by verifiable transaction data.

The long-term differentiator is not the algorithm. It is institutional trust: the cooperative registration structure, the government mandate, and the welfare fund accountability that no VC-backed gig platform will build because it is architecturally incompatible with their margin model.
