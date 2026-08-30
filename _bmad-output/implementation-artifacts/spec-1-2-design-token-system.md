---
title: 'Story 1.2: Design Token System (tokens.css)'
type: 'feature'
created: '2026-08-31'
status: 'done'
review_loop_iteration: 0
context:
  - _bmad-output/implementation-artifacts/epic-1-context.md
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Hardcoded hex values, font family names, border radii, and spacing values across components lead to visual inconsistency and make global design updates impossible.

**Approach:** Implement a comprehensive CSS custom properties system in `frontend/src/tokens.css` based on `DESIGN.md` and import it in `frontend/src/main.tsx`.

## Boundaries & Constraints

**Always:**
- All design tokens defined as CSS custom properties in `:root` inside `frontend/src/tokens.css`.
- Google Fonts (`Inter` and `JetBrains Mono`) imported via `@import url(...)` at the top of `tokens.css`.
- `frontend/src/main.tsx` must import `./tokens.css`.
- All component styles in later stories MUST reference CSS custom properties (`var(--color-...)`), no raw hex codes.

**Never:**
- Hardcoding hex values in component CSS files.
- Adding UI library frameworks (MUI, Tailwind, shadcn).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Global styling import | `main.tsx` loads | All `:root` tokens available across DOM | CSS parse errors if invalid syntax |
| Font rendering | Any element using `var(--font-sans)` or `var(--font-mono)` | Renders in Inter or JetBrains Mono | Browser default fallback |

</frozen-after-approval>

## Code Map

- `frontend/src/tokens.css` -- Complete CSS custom properties dictionary & base CSS rules
- `frontend/src/main.tsx` -- Imports tokens.css globally

## Tasks & Acceptance

**Execution:**
- [x] `frontend/src/tokens.css` -- UPDATE -- Add `@import` for Inter & JetBrains Mono, `:root` design tokens for colors, typography, spacing, border-radius, shadows, and component presets
- [x] `frontend/src/main.tsx` -- VERIFY/UPDATE -- Ensure `import './tokens.css';` is present
- [x] Verification -- `npm run build` from `frontend/` directory

**Acceptance Criteria:**
- Given `frontend/src/tokens.css`, when imported in `main.tsx`, then all color, typography, radius, spacing, and shadow tokens from `DESIGN.md` are defined in `:root`.
- Given `npm run build`, then Vite builds the frontend bundle cleanly with 0 TypeScript or CSS errors.

## Verification

**Commands:**
- `npm run build` (from frontend directory) -- expected: build completes successfully
