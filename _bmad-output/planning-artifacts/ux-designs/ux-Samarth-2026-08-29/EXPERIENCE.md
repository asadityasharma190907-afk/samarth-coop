---
title: "Samarth Experience Specification"
status: final
created: 2026-08-29
updated: 2026-08-29
project: Samarth
sources:
  - "_bmad-output/planning-artifacts/prds/prd-Samarth-2026-08-29/prd.md"
  - "_bmad-output/planning-artifacts/ux-designs/ux-Samarth-2026-08-29/DESIGN.md"
---

# Samarth Experience Specification

## Foundation

**Form factor:** Mobile-first responsive web application. No native app for MVP. Targets:
- **Mobile (primary):** 375px–767px — workers primarily use smartphones in the field.
- **Tablet:** 768px–1023px — citizens and federation admins may use tablets.
- **Desktop:** 1024px+ — Swagger demo and federation view optimised for desktop.

**UI system:** Vanilla React + custom design tokens from `DESIGN.md`. No UI framework (no MUI, no shadcn) for MVP — ensures full visual control for demo fidelity.

**Visual identity:** `DESIGN.md` is the single source of truth for all visual decisions. EXPERIENCE.md owns behavioral specifications only.

**Browser targets:** Chrome 110+, Safari 16+, Firefox 110+. No IE or legacy support.

---

## Information Architecture

### Role-based Navigation

**Citizen:**
```
/ (Landing / Login gate)
  /register         → Citizen registration
  /login            → Login (shared)
  /dashboard        → Citizen home: "Book a service" + past bookings
  /book             → Booking form (category + location)
  /booking/:id      → Booking status + offer trail
  /booking/:id/rate → Post-completion rating
```

**Worker:**
```
/worker/dashboard   → Offer inbox + wallet summary
/worker/offers      → All offers (pending, past)
/worker/wallet      → Earnings ledger + weekly earnings chip
```

**Federation / Admin:**
```
/federation         → Read-only summary: workers, bookings, welfare fund
/federation/booking/:id → Full offer audit trail for any booking
```

**Shared:**
```
/login             → Phone + password
/register          → Role selection → role-specific form
```

### Surface Map

| Surface | Primary User | FR Coverage |
|---|---|---|
| Landing / Login gate | All | FR-3 |
| Citizen registration | Citizen | FR-1 |
| Worker registration | Worker | FR-2 |
| Citizen dashboard | Citizen | FR-7 |
| Booking form | Citizen | FR-7 |
| Booking status page | Citizen | FR-8, FR-17 |
| Post-completion rating | Citizen | FR-16 |
| Worker dashboard (offer inbox) | Worker | FR-8, FR-9, FR-10 |
| Worker wallet | Worker | FR-12, FR-13 |
| Federation summary | Admin/Ministry | FR-14 |
| Booking audit trail | Admin/Ministry | FR-17 |

---

## Voice and Tone

**Principles:**
1. **Name people, not roles.** "Suresh Kumar has accepted your request" not "A worker has accepted."
2. **Explain the fairness, don't hide it.** "Suresh is matched because he has lower earnings this week." Citizens deserve to understand what the algorithm does.
3. **Plain Hindi-compatible phrasing.** Short sentences, no compound clauses. Copy should translate cleanly when multilingual support arrives.
4. **Worker dignity.** Never frame decline as a failure. "This request went to the next worker" not "Worker declined."
5. **Fund identity.** Always "Cooperative Welfare Fund," never "platform fee" or "commission."

**Copy patterns:**
- Booking confirmed: *"Your request has been sent to [Worker Name]. They'll respond shortly."*
- Worker accept: *"[Worker Name] has accepted. Estimated arrival: [time]."*
- Job complete (worker view): *"₹X credited to your wallet. ₹Y added to the Cooperative Welfare Fund."*
- Decline cascade: *"Passing your request to the next available worker…"*
- All declined: *"No workers accepted this request. Please try again or check a different area."*

---

## Component Patterns

### Authentication Forms
- **Single-column, centered** on mobile and tablet. Max 480px wide.
- Role selector (Citizen / Worker) shown as two large tap-target cards, not a dropdown.
- Worker registration: skill category is a horizontal chip group (max 2 rows); static location entry uses a map embed with a draggable pin + fallback lat/lng text inputs.
- Password field: always show/hide toggle. No strength meter for MVP.
- Error states: inline, below the affected field. Never modal.

### Citizen Booking Flow
- **Step 1:** Category chips (visual icon + label for each of the 10 skill categories). Large tap targets.
- **Step 2:** Location. Map pin (Leaflet.js, free, offline-tolerant) + current-location button + text address field.
- **Step 3:** Optional description textarea. Character count shown.
- **Step 4:** Confirmation summary → Submit. No back button on step 4 (prevents double-submit confusion).
- Flow is 4-step wizard on mobile, inline form on desktop (≥ 1024px).

### Booking Status Card (Citizen)
Three states:
1. **Pending / Finding worker** — animated pulse on a single green dot + "Finding a cooperative worker…" copy.
2. **Assigned** — worker card: name, cooperative badge, skill, rating chip, estimated arrival. No phone number shown.
3. **Completed** — shows: job total, worker payout (₹X), welfare fund contribution (₹Y, purple). Rate button if not yet rated.

### Offer Card (Worker)
- Full-bleed green left-accent card.
- Shows: citizen first name + area (not full address), skill, distance, job price.
- Two prominent buttons: **Accept** (primary, full width) and **Decline** (danger outline, full width).
- Expiry countdown shown as a thin progress bar at the card top when `expires_at < 90 seconds`.
- Accept triggers a confirmation micro-modal: "You're taking this job. Your availability will be set to busy." → Confirm.

### Worker Wallet
- **Top chip:** Weekly earnings (current week) in large monospace. Resets display each Monday automatically (the underlying data resets inherently).
- **Reliability badge:** Only shown if penalty is active. "Acceptance rate below 50% — your ranking is temporarily adjusted." Dismissable for 24h but not permanently.
- **Earnings list:** Table with columns: Date, Citizen area, Service, Job price, Your payout (95%), Welfare fund (5%). Sorted newest-first.

### Federation View
- **Three counters at top:** Total registered workers, Total completed bookings, Welfare Fund total (violet background).
- **Booking list:** Sortable table. Click a booking → full offer audit trail.
- **Audit trail:** Ordered list of every worker offered, with columns: Worker name, Rank at offer, Dispatch score at time of offer, Status (accepted/declined/expired). Dispatch scores in monospace.

---

## State Patterns

### Loading States
- Skeleton screens (not spinners) for list loads. Spinner only for action-result waits (accepting, submitting booking).
- Max skeleton duration before error: 10 seconds. Show "Taking longer than expected — check your connection" after 5s.

### Empty States
| Surface | Empty state copy |
|---|---|
| Worker offer inbox (no active offers) | "No open requests right now. You'll be notified when a booking matches your skill and area." |
| Citizen past bookings (no history) | "You haven't booked a service yet. [Book your first service →]" |
| Federation booking list (no completed bookings) | "No completed bookings yet. Seed data loads automatically on first run." |

### Error States
- **API error:** Toast notification (bottom of screen, 4s auto-dismiss) + retry button where applicable.
- **409 conflict (already accepted):** "This booking was just accepted by another worker. Refreshing…" auto-reload.
- **Form validation:** Inline, red border + error text below field. Never block submit with a modal.
- **No workers in radius:** "No cooperative workers found within 5km for this service. Try a nearby area." (Not surfaced as a technical error.)

### Transition Patterns
- Page transitions: fade (150ms). No slide — mobile webview performance.
- Offer card arrival: slide-in from right (200ms ease-out).
- Accept confirmation micro-modal: scale-in (120ms).
- Wallet counter update (after complete): number count-up animation (500ms).

---

## Interaction Primitives

### Tap Targets
- Minimum 44×44px on mobile for all interactive elements.
- Accept/Decline buttons: full-width, 56px height on mobile.

### Gestures
- Offer list: swipe-right to accept shortcut (shows green overlay). Swipe-left to decline (red overlay). Not the only path — buttons always visible.
- Pull-to-refresh on offer inbox.

### Form Interactions
- Auto-advance: after selecting a skill category chip, page scrolls to step 2 after 300ms.
- Map pin: drag to adjust; tapping "Use my location" snaps pin to device location (if permission granted).

### Keyboard / Accessibility
- All interactive elements keyboard-reachable with Tab.
- Accept/Decline buttons: distinct aria-labels ("Accept booking from [Citizen area]", "Decline booking from [Citizen area]").
- Color is never the only indicator of state (icons + labels accompany all colored status badges).

---

## Accessibility Floor

- **Color contrast:** All text/background combinations meet WCAG 2.1 AA (4.5:1 for normal text, 3:1 for large text). `{colors.brand-primary}` on white: 5.2:1 — compliant.
- **Focus rings:** Visible 2px ring in `{colors.brand-primary}` on all focusable elements.
- **Screen reader:** Dispatch score chip has `aria-label="Dispatch score: 12550, ranked 1 of 4"`.
- **Motion:** All animations respect `prefers-reduced-motion`. Substitute fade for slide/count-up animations.
- **Text resize:** Layout holds at 200% text zoom. No horizontal scroll at default viewport width.

---

## Key Flows (Named-Protagonist Journeys)

### Flow 1: Ravi Books an Electrician — The Citizen Loop

**Actor:** Ravi Sharma (citizen, Jaipur, first-time user)  
**Goal:** Book a same-day electrician

1. Lands on `/` — sees: "Book trusted cooperative workers near you." Two CTAs: Login / Register.
2. Taps Register → selects **Citizen** → fills: name, phone, password → Submit.
3. Redirected to `/dashboard`. Sees empty state with prominent **"Book a service"** button.
4. Taps "Book" → Step 1: category chips. Taps **Electrician** chip. Auto-advances.
5. Step 2: map loads, pin at approximate city center. Drags pin to his address. Step 3: types "Bathroom fan not working." Step 4: confirms — service, location, estimate ₹350. Submits.
6. **Climax beat:** Booking status page shows the animated pulse — "Finding a cooperative worker…". After ≤ 2 seconds (on seed data), transitions to **Suresh Kumar accepted** — name, badge ("Society Verified"), rating chip (4.2★), distance (2.5 km). No phone number.
7. After job: Status card shows completed. ₹332.50 to Suresh. **₹17.50 to Cooperative Welfare Fund** (violet chip, stands out). Rate button visible.
8. Ravi taps Rate → gives 4 stars → done.

**Climax beat rationale:** the moment the offer-cascade resolves into a named worker is the emotional payoff — Samarth is not an algorithm, it is a person who will help you.

---

### Flow 2: Suresh Receives and Accepts an Offer — The Worker Loop

**Actor:** Suresh Kumar (worker, electrician, ₹200 earned this week)  
**Goal:** Accept a job, complete it, see the wallet update

1. Suresh has the worker app open on his phone. Offer card slides in from right: "Booking from North Jaipur — Electrical, 2.5 km, ₹350."
2. Sees expiry progress bar (thin green → amber as time passes).
3. Taps **Accept** → micro-modal: "You're taking this job. Your availability will be set to busy." Confirms.
4. Booking status updates in his view: Ravi's area shown, job description, status: **In Progress**. Availability badge: "Busy."
5. Completes the job on-site. Taps **Mark Complete**.
6. **Climax beat:** Wallet counter animates: +₹332.50. "₹17.50 added to the Cooperative Welfare Fund." Weekly earnings chip updates: ₹532.50 (from ₹200). Availability resets: "Available."

**Climax beat rationale:** seeing the wallet number go up, and the welfare fund go up simultaneously, is the payoff that makes the economics of the platform visible — this is not a typical gig app.

---

### Flow 3: Meena Declines — The Cascade Demo Beat

**Actor:** Meena Verma (worker, best-rated, highest weekly earner)  
**Goal:** Demonstrate the cascade — Meena deprioritised, offer passed to Suresh

*This is the judge-facing demo flow. It must work on the first try.*

1. For the demo booking: Meena Verma is Rank 4 (lowest score despite being closest and best-rated — ₹4,500 weekly earnings).
2. The system offers first to Suresh (Rank 1). For demo purposes, Suresh declines → offer moves to Priya (Rank 2) → Priya declines → offer moves to Anil (Rank 3) → Anil declines → **offer reaches Meena (Rank 4)**.
3. In the demo: Meena receives the offer card. She accepts.
4. **Climax beat:** Switch to federation view — show the full audit trail. Four rows: Suresh (rank 1, score 12,550, declined), Priya (rank 2, score 12,000, declined), Anil (rank 3, score 9,750, declined), Meena (rank 4, score 5,750, accepted). The math is visible.
5. Evaluator can see: Meena was closest and best-rated. She got the job only after everyone else declined. The algorithm did exactly what it claimed to do.

**Climax beat rationale:** the audit trail with stored dispatch scores is the only thing that makes the fairness claim verifiable, not just asserted. This is the design decision that earns trust from evaluators.

---

### Flow 4: Federation Admin Reviews the Fund

**Actor:** Ministry/NCCT evaluator (read-only access)  
**Goal:** Verify the Cooperative Welfare Fund is real and auditable

1. Navigates to `/federation`. Sees three counters: 6 registered workers, 3 completed bookings, **₹52.50 in Cooperative Welfare Fund** (violet, stands out).
2. Clicks a booking in the list. Opens audit trail: full offer sequence with dispatch scores.
3. Satisfied: the fund is derived from real transactions, the algorithm is transparent, no numbers are hardcoded.

---

## Responsive & Platform Considerations

**Mobile (375–767px):**
- Single-column layouts. Wizard flow for booking (multi-step).
- Offer card is full-screen (bottom sheet on very small screens).
- Navigation: bottom tab bar (4 items: Home, Book, Offers, Wallet).
- Wallet: stacked table rows (not horizontal table).

**Tablet (768–1023px):**
- 2-column layout for booking form + map preview.
- Navigation: left sidebar (collapsed, icon-only).
- Offer list: cards in 2-column grid.

**Desktop (1024px+):**
- Full sidebar navigation (240px).
- Federation view: full data table with sortable columns.
- Booking form: single-page (not wizard), map and form side by side.

**Offline / poor connectivity:**
- Registration and login forms: queue submission and show "Submitting when connection restores."
- Offer inbox: cached for 60 seconds; refresh indicator shown when stale.
- Map: graceful fallback to text-only location entry if tiles fail to load.
