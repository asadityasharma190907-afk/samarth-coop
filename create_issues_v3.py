#!/usr/bin/env python3
"""
Create GitHub issues for Milestone 10: Worker KYC Upgrade & Experience Release
"""

import subprocess
import time

REPO = "asadityasharma190907-afk/samarth-coop"
MILESTONE = "Milestone 10: Worker KYC Upgrade & Experience Release"

# Ensure labels exist
labels_to_create = [
    ("epic-9", "0075ca", "Epic 9: Worker KYC & Verification Infrastructure"),
    ("epic-10", "e4e669", "Epic 10: Multi-Step Worker Onboarding & Verification UI"),
    ("epic-11", "d93f0b", "Epic 11: Worker Dashboard Layout & Citizen Experience"),
    ("epic-12", "0e8a16", "Epic 12: Design System & E2E Verification"),
]

for name, color, desc in labels_to_create:
    cmd = ["gh", "label", "create", name, "--color", color, "--description", desc, "--force", "-R", REPO]
    subprocess.run(cmd, capture_output=True, text=True)

issues = [
    {
        "title": "[Story 9.1] Database Schema Expansion for Worker KYC",
        "body": """## Story 9.1: Database Schema Expansion for Worker KYC

**Epic:** Epic 9 — Worker KYC & Verification Infrastructure
**FRs:** FR-2 | **Type:** backend / database

**As a** cooperative platform administrator,
**I want** the database schema to store comprehensive worker KYC verification attributes,
**So that** worker identity, verification status, and regulatory background can be tracked securely.

## Acceptance Criteria

**Given** the `WorkerProfile` SQLAlchemy model
**When** the schema migration is created and applied via Alembic (`alembic revision --autogenerate` and `alembic upgrade head`)
**Then** the `worker_profiles` table contains new columns: `father_name` (String 100), `date_of_birth` (String 20), `domicile` (String 100), `local_address` (String 255), `marital_status` (String 20), `experience_years` (Integer), `languages_spoken` (String 100), `aadhaar_number` (String 12), `police_verification_status` (String 20, default 'pending'), and `kyc_payment_status` (String 20, default 'pending').

**Given** existing database records
**When** the Alembic migration runs
**Then** existing rows receive default null or 'pending' values without breaking data integrity or failing constraints.

## References
- AD-9 (Database schema)
- PRD FR-2 (Worker Profile)""",
        "labels": ["epic-9", "backend", "p0-must-have"],
    },
    {
        "title": "[Story 9.2] Auth API & Registration Schema Updates for KYC",
        "body": """## Story 9.2: Auth API & Registration Schema Updates for KYC

**Epic:** Epic 9 — Worker KYC & Verification Infrastructure
**FRs:** FR-2 | **Type:** backend

**As a** worker registering on Samarth,
**I want** the registration API to validate and save extended KYC profile fields,
**So that** my personal, geographic, and verification details are recorded upon signup.

## ⚠️ Do this first: [Story 9.1]

## Acceptance Criteria

**Given** a registration request payload containing full KYC fields (`father_name`, `date_of_birth`, `domicile`, `local_address`, `marital_status`, `experience_years`, `languages_spoken`, `aadhaar_number`)
**When** `POST /auth/register` is called with `role: worker`
**Then** HTTP 201 Created is returned and all KYC fields are correctly persisted in `worker_profiles`.

**Given** `seed.py` / `seed_demo.py` is executed
**When** test workers are seeded into the database
**Then** all 4 test workers (Suresh, Priya, Anil, Meena) are populated with realistic KYC attributes for demonstration.

## References
- PRD FR-2, AD-4 (JWT Auth)""",
        "labels": ["epic-9", "backend", "p0-must-have"],
    },
    {
        "title": "[Story 9.3] KYC Router with Aadhaar OTP & Razorpay Test Payment Endpoints",
        "body": """## Story 9.3: KYC Router with Aadhaar OTP & Razorpay Test Payment Endpoints

**Epic:** Epic 9 — Worker KYC & Verification Infrastructure
**FRs:** FR-2 | **Type:** backend

**As a** worker undergoing KYC,
**I want** backend API endpoints to simulate Aadhaar OTP verification and Razorpay fee payment,
**So that** my verification and onboarding workflows can be processed and stored.

## ⚠️ Do this first: [Story 9.1]

## Acceptance Criteria

**Given** a valid 12-digit Aadhaar number
**When** `POST /kyc/aadhaar/send-otp` is invoked
**Then** HTTP 200 OK is returned with a simulated transaction ID and success status.

**Given** an OTP payload (`aadhaar_number`, `otp: "123456"`)
**When** `POST /kyc/aadhaar/verify-otp` is invoked
**Then** HTTP 200 OK is returned, updating the worker's profile to marked Aadhaar verified.

**Given** a payment order request
**When** `POST /kyc/payment/create-order` and `POST /kyc/payment/verify` are invoked
**Then** HTTP 200 OK is returned and `kyc_payment_status` is updated to 'completed'.

## References
- PRD FR-2""",
        "labels": ["epic-9", "backend", "p0-must-have"],
    },
    {
        "title": "[Story 10.1] Multi-Step Worker Registration Wizard",
        "body": """## Story 10.1: Multi-Step Worker Registration Wizard

**Epic:** Epic 10 — Multi-Step Worker Onboarding & Verification UI
**FRs:** FR-2 | **Type:** frontend

**As a** new worker signing up,
**I want** a clear, multi-step onboarding wizard covering Basic Info, Profile Details, Aadhaar Simulation, and Payment,
**So that** I am guided smoothly through complete KYC registration.

## ⚠️ Do this first: [Story 9.2], [Story 9.3]

## Acceptance Criteria

**Given** a worker navigating to `/register`
**When** selecting Worker role
**Then** a 4-step wizard renders: Step 1 (Basic Info), Step 2 (Profile Details), Step 3 (Aadhaar Verification Simulation), Step 4 (Razorpay Payment Simulation).

**Given** each step of the onboarding wizard
**When** required fields are completed and "Next" is clicked
**Then** progress advances, input validation executes, and the final step submits the complete payload to `POST /auth/register` and KYC endpoints.

## References
- DESIGN.md, UX-DR7""",
        "labels": ["epic-10", "frontend", "p0-must-have"],
    },
    {
        "title": "[Story 10.2] Police Verified Visual Badge Component & Card Integration",
        "body": """## Story 10.2: Police Verified Visual Badge Component & Card Integration

**Epic:** Epic 10 — Multi-Step Worker Onboarding & Verification UI
**FRs:** FR-15 | **Type:** frontend

**As a** citizen viewing worker cards,
**I want** to see a prominent "Police Verified" visual badge on worker profiles,
**So that** I have immediate trust in the worker's background check status.

## ⚠️ Do this first: [Story 9.1]

## Acceptance Criteria

**Given** a worker profile with `police_verification_status = 'verified'`
**When** worker profile cards are rendered across search lists, offer details, or booking summary
**Then** a custom styled "Police Verified" badge with checkmark icon is displayed.

**Given** a worker profile with pending or unverified status
**When** worker profile cards are rendered
**Then** an appropriate pending/unverified badge indicator is shown.

## References
- PRD FR-15, DESIGN.md""",
        "labels": ["epic-10", "frontend", "p0-must-have"],
    },
    {
        "title": "[Story 11.1] Worker Dashboard React Router Outlet Refactoring & Nested Routing",
        "body": """## Story 11.1: Worker Dashboard React Router Outlet Refactoring & Nested Routing

**Epic:** Epic 11 — Worker Dashboard Layout & Citizen Experience
**FRs:** UX-DR7 | **Type:** frontend

**As a** worker navigating my dashboard,
**I want** seamless tab switching between Offers and Wallet using React Router `<Outlet />`,
**So that** navigation state is reflected in the URL without jarring page reloads.

## Acceptance Criteria

**Given** `WorkerDashboard.tsx`
**When** refactored into a layout component with navigation tabs and React Router `<Outlet />`
**Then** `/worker/offers` and `/worker/wallet` render cleanly as nested child routes within `App.tsx`.

**Given** a user navigating directly to `/worker/offers` or `/worker/wallet`
**When** the page loads
**Then** the corresponding tab is active and content renders correctly.

## References
- UX-DR7, AD-3""",
        "labels": ["epic-11", "frontend", "p0-must-have"],
    },
    {
        "title": "[Story 11.2] Citizen Dashboard Recent Bookings & Quick Login Enhancement",
        "body": """## Story 11.2: Citizen Dashboard Recent Bookings & Quick Login Enhancement

**Epic:** Epic 11 — Worker Dashboard Layout & Citizen Experience
**FRs:** FR-7 | **Type:** frontend

**As a** citizen viewing my dashboard,
**I want** to see my recent booking history and access quick-login shortcuts,
**So that** I can track current bookings and easily log in during testing.

## Acceptance Criteria

**Given** `Dashboard.tsx` (Citizen Dashboard)
**When** rendered
**Then** the placeholder is replaced with a live list of recent bookings fetched from `GET /bookings`.

**Given** the login interface (`Login.tsx`)
**When** rendered
**Then** "Quick Login" buttons for demo Citizen and Worker accounts fill credentials instantly for fast testing.

## References
- PRD FR-7""",
        "labels": ["epic-11", "frontend", "p0-must-have"],
    },
    {
        "title": "[Story 12.1] Design Token Refactoring (Eliminate Hardcoded Hex Values)",
        "body": """## Story 12.1: Design Token Refactoring (Eliminate Hardcoded Hex Values)

**Epic:** Epic 12 — Design System & E2E Verification
**FRs:** UX-DR1 | **Type:** frontend / design-system

**As a** frontend developer,
**I want** all hardcoded CSS hex values replaced with variables from `tokens.css`,
**So that** the design token architecture is strictly enforced across the application.

## Acceptance Criteria

**Given** all `.css` and `.tsx` styling in `frontend/src`
**When** scanned for color values
**Then** zero hardcoded hex values (e.g. `#1e293b`) remain in component CSS, and all properties reference `var(--color-*)` tokens defined in `tokens.css`.

## References
- DESIGN.md, UX-DR1, AD-3""",
        "labels": ["epic-12", "frontend", "p0-must-have"],
    },
    {
        "title": "[Story 12.2] End-to-End Demo Verification & Suite Health Check",
        "body": """## Story 12.2: End-to-End Demo Verification & Suite Health Check

**Epic:** Epic 12 — Design System & E2E Verification
**FRs:** NFR-2 | **Type:** fullstack / testing

**As a** QA engineer,
**I want** to execute automated tests and manual walkthrough validation across the upgraded KYC and dashboard flows,
**So that** 100% backend health and demo reliability are confirmed.

## ⚠️ Do this first: [Story 10.1], [Story 11.1], [Story 12.1]

## Acceptance Criteria

**Given** the backend and frontend dev servers running
**When** `pytest` is executed
**Then** all test suites pass with 0 failures.

**Given** manual walkthrough execution
**When** Worker multi-step onboarding, dashboard tab navigation, and citizen booking views are exercised
**Then** `GET /health` returns `{"status": "ok"}` and no console errors or exceptions occur.

## References
- AGENTS.md milestone gate""",
        "labels": ["epic-12", "fullstack", "p0-must-have"],
    },
]

created_issues = []
for issue in issues:
    cmd = [
        "gh", "issue", "create",
        "--title", issue["title"],
        "--body", issue["body"],
        "--milestone", MILESTONE,
        "-R", REPO,
    ]
    for label in issue["labels"]:
        cmd.extend(["--label", label])

    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0:
        url = res.stdout.strip()
        created_issues.append((issue["title"], url))
        print(f"Created: {issue['title']} -> {url}")
    else:
        print(f"Failed to create {issue['title']}: {res.stderr}")

print(f"Total created: {len(created_issues)}")
