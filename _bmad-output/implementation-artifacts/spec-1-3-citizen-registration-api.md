---
title: 'Story 1.3: Citizen Registration API'
type: 'feature'
created: '2026-08-31'
status: 'done'
review_loop_iteration: 0
context:
  - _bmad-output/implementation-artifacts/epic-1-context.md
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Anonymous visitors cannot register as citizen users on the platform.

**Approach:** Implement the `POST /auth/register` API endpoint in FastAPI that accepts user details, validates inputs, verifies phone uniqueness, hashes passwords with bcrypt (cost factor 12), persists the user to the `users` table with `role = 'citizen'`, and returns a signed JWT access token.

## Boundaries & Constraints

**Always:**
- Password hashed with bcrypt cost factor 12 (`passlib.context.CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)`). Plaintext passwords must NEVER be stored or logged.
- Duplicate phone number checks return `HTTP 409 Conflict` with clear detail string.
- JWT signed using `python-jose` with `settings.SECRET_KEY` and `settings.ALGORITHM` ("HS256").
- JWT payload contains `user_id`, `name`, `role`.
- Successful registration returns `HTTP 201 Created` with `TokenResponse` schema (`access_token`, `token_type`, `user_id`, `role`).

**Never:**
- Storing or logging plaintext passwords.
- Session cookies (auth strictly `Authorization: Bearer <token>`).
- Allowing duplicate phone numbers.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Successful Registration | Valid `RegisterRequest` (`role="citizen"`) | HTTP 201 + `TokenResponse` with JWT | N/A |
| Duplicate Phone Number | `phone` already exists in `users` | HTTP 409 Conflict | `{"detail": "Phone number already registered"}` |
| Missing Fields | Invalid JSON missing required fields | HTTP 422 Unprocessable Entity | Pydantic validation error details |

</frozen-after-approval>

## Code Map

- `backend/app/schemas/auth.py` -- Pydantic schemas for `RegisterRequest` and `TokenResponse`
- `backend/app/services/auth.py` -- Password hashing (bcrypt 12) & JWT generation service
- `backend/app/routers/auth.py` -- FastAPI router with `POST /auth/register` endpoint
- `backend/app/main.py` -- Router registration (`prefix="/auth"`)
- `backend/tests/test_auth.py` -- pytest test suite covering registration logic and error states

## Tasks & Acceptance

**Execution:**
- [x] `backend/app/schemas/auth.py` -- CREATE -- Pydantic request/response models
- [x] `backend/app/services/auth.py` -- CREATE -- Password hashing and JWT generation helpers
- [x] `backend/app/routers/auth.py` -- CREATE -- `POST /auth/register` route handler
- [x] `backend/app/main.py` -- UPDATE -- Include auth router under `/auth` prefix
- [x] `backend/tests/test_auth.py` -- CREATE -- Unit & integration tests for citizen registration
- [x] Verification -- Run `pytest` from `backend/` directory

**Acceptance Criteria:**
- Given valid registration payload (`name`, `phone`, `password`, `role="citizen"`), when `POST /auth/register` is called, then HTTP 201 + valid JWT `TokenResponse` is returned, and user row is in DB.
- Given a phone number that already exists, when `POST /auth/register` is called with that phone, then HTTP 409 Conflict is returned.
- Given invalid payload missing required fields, when `POST /auth/register` is called, then HTTP 422 is returned.
- Given `pytest` command, then all tests in `backend/tests/test_auth.py` pass.

## Verification

**Commands:**
- `pytest backend/tests/test_auth.py` -- expected: all tests pass
