---
title: "Samarth Design System"
status: final
created: 2026-08-29
updated: 2026-08-29
project: Samarth
sources:
  - "_bmad-output/planning-artifacts/prds/prd-Samarth-2026-08-29/prd.md"
  - "_bmad-output/planning-artifacts/briefs/brief-Samarth-2026-08-29/brief.md"
colors:
  brand-primary: "#1A6B47"
  brand-primary-light: "#2E9E6E"
  brand-primary-dark: "#0F4A30"
  brand-accent: "#F4A623"
  brand-accent-light: "#F7BD5A"
  surface-bg: "#F8FAF9"
  surface-card: "#FFFFFF"
  surface-elevated: "#FFFFFF"
  surface-overlay: "rgba(26,107,71,0.06)"
  text-primary: "#111827"
  text-secondary: "#4B5563"
  text-muted: "#9CA3AF"
  text-on-brand: "#FFFFFF"
  text-on-accent: "#1A1A1A"
  border-default: "#E5E7EB"
  border-subtle: "#F3F4F6"
  status-success: "#16A34A"
  status-warning: "#D97706"
  status-error: "#DC2626"
  status-info: "#2563EB"
  dispatch-high: "#1A6B47"
  dispatch-mid: "#F4A623"
  dispatch-low: "#9CA3AF"
  welfare-fund: "#7C3AED"
typography:
  font-sans: "'Inter', 'Noto Sans Devanagari', sans-serif"
  font-mono: "'JetBrains Mono', 'Fira Code', monospace"
  size-display: "2.25rem/2.75rem"
  size-h1: "1.875rem/2.25rem"
  size-h2: "1.5rem/2rem"
  size-h3: "1.25rem/1.75rem"
  size-h4: "1.125rem/1.5rem"
  size-body-lg: "1.0625rem/1.625rem"
  size-body: "0.9375rem/1.5rem"
  size-body-sm: "0.875rem/1.375rem"
  size-caption: "0.75rem/1.125rem"
  size-overline: "0.6875rem/1rem"
  weight-regular: "400"
  weight-medium: "500"
  weight-semibold: "600"
  weight-bold: "700"
rounded:
  none: "0"
  sm: "4px"
  md: "8px"
  lg: "12px"
  xl: "16px"
  2xl: "24px"
  full: "9999px"
spacing:
  unit: "4px"
  xs: "4px"
  sm: "8px"
  md: "16px"
  lg: "24px"
  xl: "32px"
  2xl: "48px"
  3xl: "64px"
components:
  button-primary:
    bg: "{colors.brand-primary}"
    text: "{colors.text-on-brand}"
    hover-bg: "{colors.brand-primary-light}"
    radius: "{rounded.lg}"
    padding: "12px 24px"
    font: "{typography.weight-semibold} {typography.size-body}"
  button-secondary:
    bg: "transparent"
    border: "2px solid {colors.brand-primary}"
    text: "{colors.brand-primary}"
    hover-bg: "{colors.surface-overlay}"
    radius: "{rounded.lg}"
    padding: "10px 24px"
  button-danger:
    bg: "transparent"
    border: "2px solid {colors.status-error}"
    text: "{colors.status-error}"
    hover-bg: "rgba(220,38,38,0.06)"
    radius: "{rounded.lg}"
    padding: "10px 24px"
  card:
    bg: "{colors.surface-card}"
    border: "1px solid {colors.border-default}"
    radius: "{rounded.xl}"
    shadow: "0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.04)"
    padding: "{spacing.lg}"
  badge-verified:
    bg: "#ECFDF5"
    text: "{colors.status-success}"
    border: "1px solid #BBF7D0"
    radius: "{rounded.full}"
    font: "{typography.weight-semibold} {typography.size-caption}"
  badge-unverified:
    bg: "#FEF3C7"
    text: "{colors.status-warning}"
    radius: "{rounded.full}"
    font: "{typography.weight-semibold} {typography.size-caption}"
  badge-penalty:
    bg: "#FEF2F2"
    text: "{colors.status-error}"
    radius: "{rounded.full}"
    font: "{typography.weight-semibold} {typography.size-caption}"
  dispatch-rank-1:
    accent-color: "{colors.dispatch-high}"
    label: "Top Match"
  offer-card:
    bg: "{colors.surface-card}"
    accent-left: "4px solid {colors.brand-primary}"
    radius: "{rounded.xl}"
    shadow: "0 4px 16px rgba(26,107,71,0.12)"
  welfare-counter:
    bg: "linear-gradient(135deg, {colors.welfare-fund}, #9333EA)"
    text: "{colors.text-on-brand}"
    radius: "{rounded.2xl}"
  input:
    bg: "{colors.surface-card}"
    border: "1px solid {colors.border-default}"
    focus-border: "{colors.brand-primary}"
    radius: "{rounded.lg}"
    padding: "10px 14px"
    font: "{typography.size-body}"
---

# Samarth Design System

## Brand & Style

**Brand personality:** Trustworthy, grounded, empowering. Samarth serves cooperative workers and households — not a flashy consumer app. The aesthetic is professional warmth: confident greens that signal growth and fairness, amber accents for energy and optimism. Nothing feels corporate or cold; nothing feels frivolous.

**Cooperative identity:** The green palette is intentionally aligned with India's cooperative movement branding. The Welfare Fund element uses violet — distinct, memorable, signals something different from the rest of the UI.

**Anti-references:** Avoid the bold-red/orange of Zomato-style gig apps (implies urgency over fairness). Avoid pure white/minimalist fintech (too cold for a community platform). Avoid heavy gradients everywhere (reserve for fund/welfare moments only).

**Voice in UI copy:** Direct, warm, plain language. No jargon. Never "optimised for" — say "chosen because." Never "gig worker" — say "cooperative worker." Worker names are used throughout (Suresh, Meena, Priya) — the platform knows and names people, it doesn't abstract them.

---

## Colors

### Primary Palette
- **Brand Primary** `#1A6B47` — cooperative green. Buttons, active states, verification badges, dispatch rank-1 accents.
- **Brand Primary Light** `#2E9E6E` — hover states, lighter fills.
- **Brand Primary Dark** `#0F4A30` — pressed states, high-contrast text on light green backgrounds.
- **Brand Accent** `#F4A623` — amber. Used sparingly: CTAs on dark backgrounds, warnings that aren't errors, "offer received" notification accents.

### Surface Palette
- **Surface BG** `#F8FAF9` — very light green-tinted white. Page background.
- **Surface Card** `#FFFFFF` — pure white. Card and panel backgrounds.
- **Surface Overlay** `rgba(26,107,71,0.06)` — hover tint on interactive surfaces.

### Status Colors
- **Success** `#16A34A` — job completed, accepted, verified.
- **Warning** `#D97706` — offer expiring, reliability penalty notice.
- **Error** `#DC2626` — offer declined, error states.
- **Info** `#2563EB` — informational notices.

### Special
- **Welfare Fund** `#7C3AED` — the Cooperative Welfare Fund counter uses violet throughout to signal it's categorically different from worker earnings. Only used for CWF-related UI.

---

## Typography

**Primary font:** Inter (Google Fonts). Fallback: Noto Sans Devanagari (for future multilingual support). Mono: JetBrains Mono (dispatch score numbers, IDs).

**Scale:**
| Token | Size / Line-height | Use |
|---|---|---|
| display | 2.25rem / 2.75rem | Hero section, onboarding headline |
| h1 | 1.875rem / 2.25rem | Page titles |
| h2 | 1.5rem / 2rem | Section headers |
| h3 | 1.25rem / 1.75rem | Card titles, sub-sections |
| h4 | 1.125rem / 1.5rem | Feature labels |
| body-lg | 1.0625rem / 1.625rem | Primary body text |
| body | 0.9375rem / 1.5rem | Secondary body, form labels |
| body-sm | 0.875rem / 1.375rem | Helper text, secondary metadata |
| caption | 0.75rem / 1.125rem | Badges, timestamps, footnotes |
| overline | 0.6875rem / 1rem | Section labels (ALL CAPS, letter-spaced) |

**Dispatch score numbers** use `{typography.font-mono}` — they're data, not prose.

---

## Layout & Spacing

**Base unit:** 4px. All spacing is a multiple of the base unit.

**Max content width:** 1140px (desktop). 640px (single-column forms, dashboards).

**Page shell:** 24px side padding on mobile, 48px on tablet, 80px on desktop.

**Grid:** 12-column fluid grid. Cards: 4-col on desktop, 6-col on tablet, 12-col on mobile.

**Dashboard split:** Sidebar (240px fixed, collapsed to icon-only on mobile) + main content area.

---

## Elevation & Depth

| Level | Shadow | Use |
|---|---|---|
| 0 | none | Flat surface (page BG sections) |
| 1 | `0 1px 3px rgba(0,0,0,0.08)` | Cards, form inputs |
| 2 | `0 4px 16px rgba(26,107,71,0.12)` | Offer cards (active state), modals |
| 3 | `0 8px 32px rgba(0,0,0,0.12)` | Dropdown menus, toasts |

---

## Shapes

- **Cards:** `{rounded.xl}` (16px) — main content cards.
- **Buttons:** `{rounded.lg}` (12px) — not pill-shaped; feels professional not playful.
- **Badges:** `{rounded.full}` — status badges and labels.
- **Inputs:** `{rounded.lg}` (12px).
- **Welfare Fund display:** `{rounded.2xl}` (24px) — stands out as a special element.

---

## Components

### Buttons
Three variants: Primary (filled green), Secondary (outlined green), Danger (outlined red). Used exclusively — no ghost buttons on green backgrounds. Button text is sentence case (not ALL CAPS).

### Cards
Standard card: white background, 1px border, xl radius, elevation-1 shadow. Offer cards get elevation-2 + a 4px left accent in brand-primary to draw the eye.

### Badges
- **Society Verified** (green) — shown on every verified worker card.
- **Unverified** (amber) — internal admin view only, not citizen-facing.
- **Reliability Penalty** (red/light) — shown on worker's own dashboard only; not visible to citizens.
- **Cold-start Rating** (muted) — "New worker" label where rating shows 4.0 default.

### Dispatch Score Display
The dispatch score is shown in monospace, right-aligned, in a subtle chip. Rank 1 gets a green accent. The formula is never shown in the citizen-facing UI — only in the audit trail (federation view and Swagger).

### Welfare Fund Counter
A standout purple-gradient card, visible on the citizen post-booking summary screen and in the federation view. Shows: ₹X accumulated, N completed jobs. Not on the worker dashboard.

### Offer Card (Worker)
Incoming job offers appear as elevated cards with green left-accent, worker's wallet balance shown inline for context, two large buttons: Accept (primary) and Decline (danger outline). Auto-expires visually with a countdown if `expires_at` is near.

---

## Do's and Don'ts

| Do | Don't |
|---|---|
| Use workers' real names (Suresh Kumar, Meena Verma) | Say "Worker #4" or "gig worker" |
| Show dispatch score in Swagger and audit trail | Show the formula math in citizen-facing UI |
| Use cooperative green as the anchor color | Add red as a primary color (reserve for errors only) |
| Label the welfare fund with its full name | Call it "platform fee" or "commission" |
| Show the cascade happening in real-time | Auto-assign or hide the offer-cascade from the demo |
| Monospace for scores and numeric data | Mix font styles casually |
| Sentence case for all UI copy | ALL CAPS for button labels |
