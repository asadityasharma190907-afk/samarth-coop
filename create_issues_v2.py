#!/usr/bin/env python3
"""
Create all Samarth GitHub issues — granular, beginner-friendly, with dependencies.

Each issue is ~1-2 hours of work.
Format: [EPIC.STORY.TASK] Title
Dependencies always listed as "⚠️ Do this first: #N"

Run: python create_issues_v2.py
"""

import subprocess
import time

REPO = "asadityasharma190907-afk/samarth-coop"

# ─────────────────────────────────────────────────────────────────────────────
# ISSUE DEFINITIONS
# Each dict: title, body, labels
# Body uses plain language — beginner friendly
# ─────────────────────────────────────────────────────────────────────────────

issues = [

# ════════════════════════════════════════════════════════════════════════════
# EPIC 0 — INFRASTRUCTURE & CI/CD
# ════════════════════════════════════════════════════════════════════════════

{
"title": "[INFRA-1] Create backend folder structure and FastAPI app skeleton",
"body": """## 📁 What this issue is about

Set up the `backend/` folder with a working FastAPI app that starts without errors.
When done, running `uvicorn app.main:app --reload` should show the Swagger docs at http://localhost:8000/docs.

## 📋 Exactly what to do

1. Create `backend/app/main.py` with a basic FastAPI app (just a health check route `/health`)
2. Create `backend/app/config.py` — reads settings from `.env` file using `pydantic-settings`
3. Create `backend/app/database.py` — SQLAlchemy engine connecting to SQLite (local) or PostgreSQL (production)
4. Create `backend/.env` by copying `.env.example`
5. Run `pip install -r requirements.txt` then `uvicorn app.main:app --reload`
6. Verify: open http://localhost:8000/health — should return `{"status": "ok"}`

## ✅ How to know it's done

- [ ] `GET /health` returns `{"status": "ok"}`
- [ ] `GET /docs` shows Swagger UI without errors
- [ ] `.env` file exists (copy of `.env.example`) — **never commit `.env` to git**

## 📚 Helpful reading
- FastAPI first steps: https://fastapi.tiangolo.com/tutorial/first-steps/
- pydantic-settings: https://docs.pydantic.dev/latest/concepts/pydantic_settings/

---
**No dependencies — start here!**""",
"labels": ["epic-infra", "backend", "p0-must-have"],
},

{
"title": "[INFRA-2] Initialize Alembic and create the first database migration",
"body": """## 📁 What this issue is about

Set up Alembic so we can create and manage database tables properly.
Alembic is like version control for your database schema.

## ⚠️ Do this first: #29 (INFRA-1 must be done)

## 📋 Exactly what to do

1. In the `backend/` folder, run `alembic init alembic`
2. Edit `alembic/env.py`:
   - Import your SQLAlchemy `Base` from `app.database`
   - Set `target_metadata = Base.metadata`
   - Read the `DATABASE_URL` from your config
3. Create an empty first migration: `alembic revision --autogenerate -m "initial"`
4. Apply it: `alembic upgrade head`
5. Verify the `alembic_version` table exists in the SQLite file

## ✅ How to know it's done

- [ ] `alembic upgrade head` runs without errors
- [ ] `alembic history` shows one revision

## 📚 Helpful reading
- Alembic tutorial: https://alembic.sqlalchemy.org/en/latest/tutorial.html

---
**Depends on:** #29 (backend skeleton)""",
"labels": ["epic-infra", "backend", "p0-must-have"],
},

{
"title": "[INFRA-3] Set up Vite + React frontend project",
"body": """## 📁 What this issue is about

Create the `frontend/` folder with a React + TypeScript + Vite project.

## 📋 Exactly what to do

1. In the `frontend/` folder, run: `npm create vite@latest . -- --template react-ts`
2. Run `npm install`
3. Install TanStack Query: `npm install @tanstack/react-query`
4. Install React Router: `npm install react-router-dom`
5. Run `npm run dev` — should open http://localhost:5173
6. Replace the default Vite boilerplate in `src/App.tsx` with: `<h1>Samarth</h1>`
7. Delete `src/App.css` and `src/index.css` (we'll replace with our own tokens)

## ✅ How to know it's done

- [ ] `npm run dev` starts without errors
- [ ] `npm run build` succeeds (this is what CI checks)
- [ ] `npm run lint` passes

---
**No dependencies — can be done in parallel with INFRA-1**""",
"labels": ["epic-infra", "frontend", "p0-must-have"],
},

{
"title": "[INFRA-4] Set up GitHub Actions: backend CI (tests + lint)",
"body": """## 📁 What this issue is about

The CI workflow file `.github/workflows/backend-ci.yml` already exists in the repo.
This issue is about making sure it actually passes — add `ruff` config and a first passing test.

## ⚠️ Do this first: #29 (INFRA-1)

## 📋 Exactly what to do

1. Create `backend/pyproject.toml` with ruff config:
```toml
[tool.ruff]
line-length = 88
select = ["E", "F", "I"]

[tool.ruff.format]
quote-style = "double"
```

2. Create `backend/tests/__init__.py` (empty file)
3. Create `backend/tests/test_health.py`:
```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

4. Run locally: `pytest tests/` — should pass
5. Push to a branch and open a PR — GitHub Actions should show ✅

## ✅ How to know it's done

- [ ] `pytest tests/` passes locally
- [ ] GitHub Actions shows green on a PR
- [ ] `ruff check .` passes (no lint errors)

---
**Depends on:** #29 (backend skeleton)""",
"labels": ["epic-infra", "infra", "p0-must-have"],
},

{
"title": "[INFRA-5] Set up GitHub Actions: frontend CI (lint + build)",
"body": """## 📁 What this issue is about

The CI workflow `.github/workflows/frontend-ci.yml` already exists.
Make sure it passes — add ESLint config and ensure the build succeeds.

## ⚠️ Do this first: #31 (INFRA-3)

## 📋 Exactly what to do

1. Check `frontend/package.json` has these scripts:
   - `"lint": "eslint src --ext ts,tsx"`
   - `"build": "tsc && vite build"`
2. Fix any TypeScript or ESLint errors that appear
3. Push to a branch and open a PR

## ✅ How to know it's done

- [ ] `npm run lint` passes with no errors
- [ ] `npm run build` completes without errors
- [ ] GitHub Actions frontend CI shows ✅ on a PR

---
**Depends on:** #31 (frontend setup)""",
"labels": ["epic-infra", "infra", "p0-must-have"],
},

{
"title": "[INFRA-6] Create deployment guide (Render.com setup)",
"body": """## 📁 What this issue is about

Write `docs/deployment.md` — a step-by-step guide for deploying to Render.com.
This is a documentation task, not a code task.

## 📋 Exactly what to do

Write clear instructions covering:
1. **Backend on Render** — "New Web Service" → connect GitHub repo → set Build Command, Start Command, Environment Variables
2. **PostgreSQL on Render** — "New PostgreSQL" free tier → copy the `DATABASE_URL` to the web service
3. **Frontend on Render** — "New Static Site" → Build Command: `npm run build` → Publish Directory: `dist`
4. **Environment variables** to set: `DATABASE_URL`, `SECRET_KEY`, `ALGORITHM`
5. How to run migrations on Render: add it to the start command

## ✅ How to know it's done

- [ ] `docs/deployment.md` exists and is clear enough for a beginner to follow
- [ ] A team member who hasn't done it before can deploy using only this guide

---
**No code dependencies — can be done anytime**""",
"labels": ["epic-infra", "infra", "p1-should-have"],
},


# ════════════════════════════════════════════════════════════════════════════
# EPIC 1 — AUTH & DESIGN SYSTEM
# ════════════════════════════════════════════════════════════════════════════

{
"title": "[1.1] Create the 4 database tables (users, worker_profiles, bookings, booking_offers)",
"body": """## 📁 What this issue is about

Create the SQLAlchemy models (Python classes) for all 4 database tables.
These are the only 4 tables we'll ever need for this project.

## ⚠️ Do this first: #30 (Alembic setup, INFRA-2)

## 📋 Exactly what to do

Create these files:
- `backend/app/models/user.py` — `User` model
- `backend/app/models/worker_profile.py` — `WorkerProfile` model  
- `backend/app/models/booking.py` — `Booking` model
- `backend/app/models/booking_offer.py` — `BookingOffer` model

**Table schemas (copy these exactly):**

```python
# users table
class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    phone = Column(String(15), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)  # 'citizen', 'worker', 'admin'
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# worker_profiles table
class WorkerProfile(Base):
    __tablename__ = "worker_profiles"
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String, ForeignKey("users.id"), unique=True)
    skill = Column(String(50), nullable=False)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    rating = Column(Float, nullable=True)  # None = cold start (use 4.0 in dispatch)
    availability = Column(Boolean, default=True)
    verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

After creating all 4 models:
1. Import them in `app/database.py`
2. Run: `alembic revision --autogenerate -m "add four tables"`
3. Run: `alembic upgrade head`
4. Verify the tables exist in the SQLite file

## ✅ How to know it's done

- [ ] 4 model files exist in `app/models/`
- [ ] `alembic upgrade head` runs without errors
- [ ] Tables are visible in the SQLite database

## ⚠️ Important rules
- **NO `weekly_earnings` column** on `worker_profiles` — this is computed at query time
- There should be exactly **4 tables** — no more

---
**Depends on:** #30 (Alembic setup)""",
"labels": ["epic-1", "backend", "p0-must-have"],
},

{
"title": "[1.2] Create Pydantic schemas for request/response validation",
"body": """## 📁 What this issue is about

Create Pydantic schemas — these define what data the API accepts and returns.
Think of them as form templates that automatically check if the data is valid.

## ⚠️ Do this first: #35 (database tables)

## 📋 Exactly what to do

Create `backend/app/schemas/`:
- `auth.py` — `RegisterRequest`, `LoginRequest`, `TokenResponse`
- `worker.py` — `WorkerResponse` (includes dispatch_score field)
- `booking.py` — `BookingCreateRequest`, `BookingResponse`
- `offer.py` — `OfferActionRequest` (action: accept/decline), `OfferAuditRow`

Example for auth:
```python
from pydantic import BaseModel

class RegisterRequest(BaseModel):
    name: str
    phone: str
    password: str
    role: str  # 'citizen' or 'worker'
    skill: str | None = None  # workers only
    lat: float | None = None  # workers only
    lng: float | None = None  # workers only

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    name: str
```

## ✅ How to know it's done

- [ ] All schema files exist
- [ ] `from app.schemas.auth import RegisterRequest` works without errors

---
**Depends on:** #35 (database tables, so you know what data exists)""",
"labels": ["epic-1", "backend", "p0-must-have"],
},

{
"title": "[1.3] Build the auth service: password hashing and JWT token creation",
"body": """## 📁 What this issue is about

Create the security utilities: hash passwords with bcrypt, create and verify JWT tokens.
This is the heart of authentication — no actual API routes yet.

## ⚠️ Do this first: #35 (tables), #36 (schemas)

## 📋 Exactly what to do

Create `backend/app/services/auth.py`:

```python
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict, secret_key: str, expire_minutes: int = 10080) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(minutes=expire_minutes)
    return jwt.encode(payload, secret_key, algorithm="HS256")

def decode_token(token: str, secret_key: str) -> dict:
    return jwt.decode(token, secret_key, algorithms=["HS256"])
```

Write a test in `tests/test_auth_service.py`:
```python
from app.services.auth import hash_password, verify_password

def test_password_hashing():
    hashed = hash_password("mypassword")
    assert verify_password("mypassword", hashed)
    assert not verify_password("wrongpassword", hashed)
```

## ✅ How to know it's done

- [ ] `tests/test_auth_service.py` passes with `pytest`
- [ ] The password is NOT stored as plain text anywhere

---
**Depends on:** #35, #36""",
"labels": ["epic-1", "backend", "p0-must-have"],
},

{
"title": "[1.4] Build POST /auth/register API endpoint",
"body": """## 📁 What this issue is about

Create the registration endpoint. Citizens and workers use this to create accounts.

## ⚠️ Do this first: #35, #36, #37

## 📋 Exactly what to do

Create `backend/app/routers/auth.py`:

```python
@router.post("/auth/register", status_code=201)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    # 1. Check if phone already exists → 409 if yes
    # 2. Hash the password
    # 3. Create User row
    # 4. If role == 'worker': also create WorkerProfile row
    # 5. Return a JWT token
```

Register the router in `app/main.py`.

Write tests in `tests/test_auth_api.py`:
```python
def test_citizen_registration_success():
    res = client.post("/auth/register", json={
        "name": "Ravi Sharma", "phone": "9876543210",
        "password": "secret123", "role": "citizen"
    })
    assert res.status_code == 201
    assert "access_token" in res.json()

def test_duplicate_phone_returns_409():
    # register same phone twice
    ...
```

## ✅ How to know it's done

- [ ] `POST /auth/register` with valid citizen data → 201 + JWT
- [ ] `POST /auth/register` with duplicate phone → 409
- [ ] Tests pass
- [ ] Swagger docs show the endpoint

---
**Depends on:** #35 (tables), #36 (schemas), #37 (auth service)""",
"labels": ["epic-1", "backend", "p0-must-have"],
},

{
"title": "[1.5] Build POST /auth/login API endpoint",
"body": """## 📁 What this issue is about

Create the login endpoint. Returns a JWT token when phone + password are correct.

## ⚠️ Do this first: #38 (register endpoint)

## 📋 Exactly what to do

Add to `backend/app/routers/auth.py`:

```python
@router.post("/auth/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    # 1. Find user by phone
    # 2. If not found → 401
    # 3. Verify password → 401 if wrong
    # 4. Return JWT with {user_id, role, name} in payload
```

Tests:
```python
def test_login_success():
    # First register, then login
    ...
    assert res.status_code == 200
    assert res.json()["role"] in ["citizen", "worker"]

def test_login_wrong_password():
    res = client.post("/auth/login", json={"phone": "...", "password": "wrong"})
    assert res.status_code == 401
```

## ✅ How to know it's done

- [ ] Correct credentials → 200 + JWT with role in payload
- [ ] Wrong password → 401
- [ ] Tests pass

---
**Depends on:** #38 (register — so you can create a user to log in with)""",
"labels": ["epic-1", "backend", "p0-must-have"],
},

{
"title": "[1.6] Create auth middleware: protect routes with JWT",
"body": """## 📁 What this issue is about

Create a dependency function that checks the JWT token on protected routes.
Without this, anyone can call any endpoint without logging in.

## ⚠️ Do this first: #39 (login endpoint)

## 📋 Exactly what to do

Add to `backend/app/services/auth.py` or create `backend/app/dependencies.py`:

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    token = credentials.credentials
    try:
        payload = decode_token(token, settings.SECRET_KEY)
        user = db.query(User).filter(User.id == payload["user_id"]).first()
        if not user:
            raise HTTPException(status_code=401)
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

Write a test showing that calling a protected endpoint without a token returns 401.

## ✅ How to know it's done

- [ ] Protected endpoint without token → 401
- [ ] Protected endpoint with valid token → 200
- [ ] Test passes

---
**Depends on:** #39 (login, to get a token to test with)""",
"labels": ["epic-1", "backend", "p0-must-have"],
},

{
"title": "[1.7] Create design token CSS file (all colors, fonts, spacing)",
"body": """## 📁 What this issue is about

Create `frontend/src/tokens.css` — all colors, fonts, and spacing as CSS variables.
**Rule: No hardcoded colors anywhere in the app. Everything references a token.**

## ⚠️ Do this first: #31 (frontend setup, INFRA-3)

## 📋 Exactly what to do

Create `frontend/src/tokens.css` with these exact tokens:

```css
:root {
  /* Colors — Notion-inspired clean palette */
  --color-bg: #ffffff;
  --color-bg-secondary: #f7f6f3;
  --color-bg-hover: #f0efec;
  --color-border: #e9e9e7;
  --color-border-subtle: #f0efec;

  --color-text-primary: #1a1a1a;
  --color-text-secondary: #6b6b6b;
  --color-text-muted: #9b9b9b;

  /* Brand — cooperative green */
  --color-brand: #1a6b47;
  --color-brand-light: #e8f5ee;
  --color-brand-dark: #0f4a30;
  --color-brand-text: #ffffff;

  /* Accent — amber for secondary actions */
  --color-accent: #f4a623;
  --color-accent-light: #fef3e0;

  /* Status */
  --color-success: #16a34a;
  --color-warning: #d97706;
  --color-error: #dc2626;
  --color-info: #2563eb;

  /* Special — violet for Cooperative Welfare Fund only */
  --color-welfare: #7c3aed;
  --color-welfare-light: #f3f0ff;

  /* Typography */
  --font-sans: 'Inter', -apple-system, sans-serif;
  --font-mono: 'JetBrains Mono', monospace;

  --text-xs: 0.75rem;
  --text-sm: 0.875rem;
  --text-base: 0.9375rem;
  --text-lg: 1.0625rem;
  --text-xl: 1.25rem;
  --text-2xl: 1.5rem;
  --text-3xl: 1.875rem;

  /* Spacing */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-8: 32px;
  --space-10: 40px;
  --space-12: 48px;

  /* Radius */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-xl: 16px;
  --radius-full: 9999px;

  /* Shadows — very subtle, Notion-style */
  --shadow-sm: 0 1px 2px rgba(0,0,0,0.06);
  --shadow-md: 0 2px 8px rgba(0,0,0,0.08);
  --shadow-lg: 0 4px 16px rgba(0,0,0,0.10);
}
```

Import it in `src/main.tsx`: `import './tokens.css'`

## ✅ How to know it's done

- [ ] `tokens.css` exists with all tokens
- [ ] It's imported in `main.tsx`
- [ ] `npm run build` still passes

---
**Depends on:** #31 (frontend setup)""",
"labels": ["epic-1", "frontend", "p0-must-have"],
},

{
"title": "[1.8] Build the page shell: navigation, routing, layout",
"body": """## 📁 What this issue is about

Set up React Router with the page structure and a navigation shell.
After this, each team member can work on a page independently.

## ⚠️ Do this first: #41 (tokens.css), #31 (frontend setup)

## 📋 Exactly what to do

1. Set up routes in `src/App.tsx`:
   - `/login` → `LoginPage`
   - `/register` → `RegisterPage`
   - `/dashboard` → `CitizenDashboard` (protected)
   - `/book` → `BookingPage` (protected, citizen only)
   - `/booking/:id` → `BookingStatusPage` (protected)
   - `/worker/dashboard` → `WorkerDashboard` (protected)
   - `/worker/offers` → `WorkerOffersPage` (protected)
   - `/worker/wallet` → `WorkerWalletPage` (protected)
   - `/federation` → `FederationPage` (protected)

2. Create placeholder page components (just an `<h1>` for now) in `src/pages/`

3. Create `src/lib/auth.ts`:
   - `saveToken(token)` → saves JWT to localStorage
   - `getToken()` → reads from localStorage
   - `clearToken()` → logout

4. Create an `AuthGuard` component that redirects to `/login` if no token

## ✅ How to know it's done

- [ ] Visiting `/login` shows the Login placeholder page
- [ ] Visiting `/dashboard` without a token redirects to `/login`
- [ ] All routes render without crashing

---
**Depends on:** #31 (frontend setup), #41 (tokens)""",
"labels": ["epic-1", "frontend", "p0-must-have"],
},

{
"title": "[1.9] Build Login and Register pages (UI)",
"body": """## 📁 What this issue is about

Build the actual Login and Register pages with forms.
Uses Notion-style design: clean, minimal, lots of whitespace.

## ⚠️ Do this first: #42 (page shell/routing), #41 (tokens)

## 📋 Exactly what to do

**Register page (`src/pages/RegisterPage.tsx`):**
- Two large role-selector cards: "I'm a Citizen" and "I'm a Worker"
- Form fields: Name, Phone, Password
- If Worker: show Skill dropdown + Location (lat, lng text inputs for now)
- On submit: call `POST /auth/register`
- On success: save token → redirect to dashboard

**Login page (`src/pages/LoginPage.tsx`):**
- Phone + Password inputs
- "Log in" button
- Error message inline below form (not a popup)

**Notion-style design tips:**
- Max width 480px, centered
- `background: var(--color-bg-secondary)` page background
- Clean white card with `var(--shadow-sm)`
- `font-family: var(--font-sans)`
- Inputs: `border: 1px solid var(--color-border)`, rounded `var(--radius-md)`

**Create a reusable `Button` component in `src/components/Button.tsx`:**
- Props: `variant` (primary | secondary), `isLoading`, `children`
- Primary: `background: var(--color-brand)`, white text
- Disabled/loading: reduced opacity

## ✅ How to know it's done

- [ ] Can register as a citizen and get redirected to dashboard
- [ ] Can register as a worker (with skill and location)
- [ ] Can log in with correct credentials
- [ ] Wrong credentials shows an error message without page reload
- [ ] Design uses only tokens from tokens.css (no hardcoded colors)

---
**Depends on:** #38 (register API), #39 (login API), #42 (routing)""",
"labels": ["epic-1", "frontend", "p0-must-have"],
},


# ════════════════════════════════════════════════════════════════════════════
# EPIC 2 — DISPATCH ALGORITHM
# ════════════════════════════════════════════════════════════════════════════

{
"title": "[2.1] Build the Haversine distance function and write unit tests",
"body": """## 📁 What this issue is about

Write the function that calculates the straight-line distance between two GPS coordinates.
This is used to check if a worker is within 5km of the citizen's location.

## ⚠️ Do this first: #35 (tables, just to have the project structure ready)

## 📋 Exactly what to do

Create `backend/app/services/dispatch.py`:

```python
from math import radians, sin, cos, sqrt, atan2

def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    \"\"\"Calculate distance in km between two GPS coordinates.\"\"\"
    R = 6371.0  # Earth radius in km
    dlat = radians(lat2 - lat1)
    dlng = radians(lng2 - lng1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng/2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1-a))
```

Write tests in `tests/test_dispatch.py`:
```python
def test_same_point_distance_is_zero():
    assert haversine_km(26.9124, 75.7873, 26.9124, 75.7873) == 0.0

def test_jaipur_distance():
    # Two known points in Jaipur ~2.5km apart
    d = haversine_km(26.9124, 75.7873, 26.8954, 75.8069)
    assert 2.0 < d < 3.0
```

## ✅ How to know it's done

- [ ] `haversine_km` function exists in `dispatch.py`
- [ ] Tests pass with `pytest`

---
**No prior issues needed** — this is pure math, self-contained""",
"labels": ["epic-2", "backend", "p0-must-have"],
},

{
"title": "[2.2] Build the weekly earnings subquery function",
"body": """## 📁 What this issue is about

Build the function that calculates how much a worker has earned this week by querying the database.

**⚠️ CRITICAL RULE: We NEVER store weekly earnings in the database. Always compute from bookings.**

## ⚠️ Do this first: #35 (database tables), #44 (haversine)

## 📋 Exactly what to do

Add to `backend/app/services/dispatch.py`:

```python
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func, text

def get_weekly_earnings(worker_id: str, db: Session) -> Decimal:
    \"\"\"
    Compute worker's earnings for the current ISO week.
    Returns worker_payout = job_price * 0.95 for all completed bookings this week.

    Uses date_trunc('week', NOW()) in PostgreSQL or equivalent in SQLite.
    \"\"\"
    result = db.execute(
        text(\"\"\"
            SELECT COALESCE(SUM(job_price * 0.95), 0) as earnings
            FROM bookings
            WHERE worker_id = :worker_id
              AND status = 'completed'
              AND created_at >= date('now', 'weekday 0', '-7 days')
        \"\"\"),
        {"worker_id": worker_id}
    ).fetchone()
    return Decimal(str(result.earnings))
```

Write a test that creates a booking in the DB and checks the result.

## ✅ How to know it's done

- [ ] Function exists and is importable
- [ ] Test passes: worker with 1 completed booking of ₹1000 → `get_weekly_earnings` returns `Decimal('950')`
- [ ] Test passes: new worker with no bookings → returns `Decimal('0')`

---
**Depends on:** #35 (tables — need Booking model), #44 (for context in same file)""",
"labels": ["epic-2", "backend", "p0-must-have"],
},

{
"title": "[2.3] Build the reliability penalty check",
"body": """## 📁 What this issue is about

Build the function that checks if a worker declines too many offers.
Workers who decline more than 50% of their last 10 offers (after getting 5+) get a score penalty.

## ⚠️ Do this first: #35 (tables), #45 (dispatch.py file started)

## 📋 Exactly what to do

Add to `backend/app/services/dispatch.py`:

```python
def has_reliability_penalty(worker_id: str, db: Session) -> bool:
    \"\"\"
    Returns True if worker should have a reliability penalty applied.
    Conditions: must have >= 5 total offers AND acceptance rate < 50%.
    \"\"\"
    from app.models.booking_offer import BookingOffer
    recent = (
        db.query(BookingOffer)
        .filter(BookingOffer.worker_id == worker_id)
        .order_by(BookingOffer.created_at.desc())
        .limit(10)
        .all()
    )
    if len(recent) < 5:
        return False
    accepted = sum(1 for o in recent if o.status == "accepted")
    return accepted / len(recent) < 0.5
```

Write tests:
- Worker with 3 offers total → no penalty (grace period)
- Worker with 6 offers, 2 accepted (33%) → penalty applies
- Worker with 6 offers, 4 accepted (67%) → no penalty

## ✅ How to know it's done

- [ ] Function exists
- [ ] 3 tests pass

---
**Depends on:** #35 (need BookingOffer model), #45 (adding to same file)""",
"labels": ["epic-2", "backend", "p0-must-have"],
},

{
"title": "[2.4] Build the dispatch score calculator",
"body": """## 📁 What this issue is about

Build the main scoring function that combines weekly earnings, rating, distance, and reliability.
This is the core of the entire platform.

## ⚠️ Do this first: #44, #45, #46

## The formula (do NOT change this):
```
Score = (5000 − WeeklyEarnings) × 2
      + (1000 × Rating)      ← use 4.0 if rating is null
      − (500 × Distance_km)
      − ReliabilityPenalty   ← 3000 if penalty applies, else 0
```

## 📋 Exactly what to do

Add to `backend/app/services/dispatch.py`:

```python
from decimal import Decimal

def compute_dispatch_score(
    weekly_earnings: Decimal,
    rating: float | None,
    distance_km: float,
    reliability_penalty: bool,
) -> Decimal:
    effective_rating = Decimal(str(rating)) if rating is not None else Decimal("4.0")
    penalty = Decimal("3000") if reliability_penalty else Decimal("0")
    return (
        (Decimal("5000") - weekly_earnings) * 2
        + Decimal("1000") * effective_rating
        - Decimal("500") * Decimal(str(distance_km))
        - penalty
    )
```

Write tests verifying the seed data expected scores:
```python
def test_suresh_score():
    # WeeklyEarnings=200, Rating=4.2, Distance=2.5km, no penalty
    score = compute_dispatch_score(Decimal("200"), 4.2, 2.5, False)
    assert 12500 < score < 12600  # expected ~12,550

def test_meena_score():
    # WeeklyEarnings=4500, Rating=4.9, Distance=0.3km, no penalty
    score = compute_dispatch_score(Decimal("4500"), 4.9, 0.3, False)
    assert 5700 < score < 5800  # expected ~5,750
```

## ✅ How to know it's done

- [ ] Suresh score test passes (~12,550)
- [ ] Meena score test passes (~5,750)
- [ ] All 4 seed worker scores match Appendix A of PRD

---
**Depends on:** #44, #45, #46""",
"labels": ["epic-2", "backend", "p0-must-have"],
},

{
"title": "[2.5] Create the seed data script with 4 test workers",
"body": """## 📁 What this issue is about

Create a script that fills the database with test data.
This is needed so we can verify the dispatch ranking before building any UI.

## ⚠️ Do this first: #35, #38 (registration logic to understand how to create users)

## 📋 Exactly what to do

Create `backend/app/seed.py`:

Workers to create (these exact values — they produce the deterministic ranking):

| Name | Weekly Earnings | Rating | Lat | Lng | Expected Rank |
|---|---|---|---|---|---|
| Suresh Kumar | ₹200 (via past booking) | 4.2 | 26.9244 | 75.7734 | 1st |
| Priya Gupta | ₹0 (no bookings) | null | 26.8784 | 75.7453 | 2nd |
| Anil Yadav | ₹2000 (via past booking) | 4.5 | 26.9284 | 75.7627 | 3rd |
| Meena Verma | ₹4500 (via past bookings) | 4.9 | 26.9106 | 75.7909 | 4th |

Also create 2 citizen users: Ravi Sharma and Anita Singh.

The script should:
1. Clear all existing data (for clean reruns)
2. Create the users + worker profiles
3. Create past `completed` bookings to produce the weekly earnings numbers
4. Print a success message

## ✅ How to know it's done

- [ ] `python app/seed.py` runs without errors
- [ ] 4 workers and 2 citizens exist in the database
- [ ] Past bookings give Suresh ₹200, Anil ₹2000, Meena ₹4500 in weekly earnings

---
**Depends on:** #35 (tables to insert into)""",
"labels": ["epic-2", "backend", "p0-must-have"],
},

{
"title": "[2.6] 🚦 MILESTONE GATE: Build GET /workers endpoint (ranked list)",
"body": """## 📁 What this issue is about

Build the endpoint that returns workers ranked by dispatch score.
**This is the most important endpoint in the project — the hackathon demo depends on it.**

## ⚠️ Do this first: #44, #45, #46, #47, #48 (ALL dispatch functions + seed data)

## 📋 Exactly what to do

Create `backend/app/routers/workers.py`:

```python
@router.get("/workers")
def get_workers(skill: str, lat: float, lng: float, db: Session = Depends(get_db)):
    # 1. Find all workers with matching skill, verified=True, availability=True
    # 2. Filter to those within 5km using haversine_km()
    # 3. For each worker:
    #    - compute weekly_earnings using get_weekly_earnings()
    #    - compute has_penalty using has_reliability_penalty()
    #    - compute distance
    #    - compute score using compute_dispatch_score()
    # 4. Sort by score descending
    # 5. Return list with rank, score, worker info
```

## 🚦 MILESTONE GATE — verify this BEFORE starting Epic 3:
```bash
# With seed data loaded:
curl "http://localhost:8000/workers?skill=electrician&lat=26.9124&lng=75.7873"

# Expected order:
# 1. Suresh Kumar  (~12,550)
# 2. Priya Gupta   (~12,000)
# 3. Anil Yadav    (~9,750)
# 4. Meena Verma   (~5,750)
```

## ✅ How to know it's done

- [ ] Endpoint returns 4 workers in correct order with seed data
- [ ] Unverified workers do NOT appear
- [ ] Unavailable workers do NOT appear
- [ ] Workers > 5km away do NOT appear
- [ ] `rating_is_default: true` appears for Priya (who has null rating)

---
**Depends on:** #44, #45, #46, #47, #48""",
"labels": ["epic-2", "backend", "p0-must-have", "milestone-gate"],
},


# ════════════════════════════════════════════════════════════════════════════
# EPIC 3 — BOOKING & OFFER CASCADE
# ════════════════════════════════════════════════════════════════════════════

{
"title": "[3.1] Build POST /bookings endpoint (create a booking)",
"body": """## 📁 What this issue is about

Build the endpoint where a citizen creates a booking.

## ⚠️ Do this first: #49 (milestone gate MUST pass first), #40 (auth middleware)

## 📋 Exactly what to do

Add to `backend/app/routers/bookings.py`:

```python
@router.post("/bookings", status_code=201)
def create_booking(
    data: BookingCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 1. Check current_user.role == 'citizen' → 403 if not
    # 2. Create Booking row with status='pending', job_price from category rate
    # 3. Commit to DB
    # 4. Return booking_id and status
    # (Dispatch happens in next issue)
```

Job price by skill (hardcoded for MVP):
```python
JOB_PRICES = {
    "electrician": 350, "plumber": 300, "carpenter": 400,
    "painter": 250, "domestic helper": 200, "caregiver": 300,
    "driver": 150, "gardener": 200, "cleaner": 180, "technician": 350
}
```

## ✅ How to know it's done

- [ ] Citizen can create a booking → 201 with booking_id
- [ ] Worker trying to create a booking → 403
- [ ] Unauthenticated request → 401
- [ ] Test passes

---
**Depends on:** #49 (milestone gate), #40 (auth middleware)""",
"labels": ["epic-3", "backend", "p0-must-have"],
},

{
"title": "[3.2] Build offer dispatch: send first offer when booking is created",
"body": """## 📁 What this issue is about

When a booking is created, automatically find the top-ranked worker and create an offer for them.

## ⚠️ Do this first: #50 (create booking endpoint)

## 📋 Exactly what to do

Create `backend/app/services/booking.py`:

```python
def dispatch_first_offer(booking_id: str, db: Session):
    booking = db.query(Booking).filter_by(id=booking_id).first()
    # 1. Call GET /workers logic (reuse the ranking function)
    # 2. Take the rank-1 worker
    # 3. Create BookingOffer row:
    #    - booking_id, worker_id
    #    - rank_at_offer = 1
    #    - dispatch_score = computed score (STORE IT NOW — never recompute)
    #    - status = 'offered'
    #    - expires_at = datetime.utcnow() + timedelta(minutes=2)
    # 4. If no eligible workers: set booking.status = 'cancelled'
```

Call `dispatch_first_offer` from the `POST /bookings` endpoint after creating the booking.

## ✅ How to know it's done

- [ ] After creating a booking, a `booking_offers` row exists with `rank_at_offer=1`
- [ ] `dispatch_score` is stored in the offer row
- [ ] `expires_at` is 2 minutes in the future
- [ ] If no workers exist: booking status = 'cancelled'

---
**Depends on:** #50 (create booking)""",
"labels": ["epic-3", "backend", "p0-must-have"],
},

{
"title": "[3.3] Build worker accept endpoint (with row lock for concurrency safety)",
"body": """## 📁 What this issue is about

Build the endpoint where a worker accepts a job offer.
**Critical: must use a database row lock to prevent two workers accidentally taking the same job.**

## ⚠️ Do this first: #51 (offer dispatch)

## 📋 Exactly what to do

Create `backend/app/routers/offers.py`:

```python
@router.put("/booking-offers/{offer_id}")
def respond_to_offer(
    offer_id: str,
    data: OfferActionRequest,  # action: 'accept' or 'decline'
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if data.action == "accept":
        # ROW LOCK — prevents double-accept
        booking = (
            db.query(Booking)
            .filter(Booking.id == offer.booking_id)
            .with_for_update()  # <-- this is the lock
            .first()
        )
        if booking.status != "pending":
            raise HTTPException(409, "Booking already taken")
        # Update booking: status='assigned', worker_id=current_user.id
        # Update offer: status='accepted'
        # Update worker: availability=False
```

Write a test that verifies:
- Two simultaneous accepts: one gets 200, one gets 409
(Hint: you can simulate this by calling accept twice in the test)

## ✅ How to know it's done

- [ ] Accept → booking.status = 'assigned', worker.availability = False
- [ ] Second accept on same booking → 409
- [ ] Tests pass

---
**Depends on:** #51 (dispatch — need an offer to accept)""",
"labels": ["epic-3", "backend", "p0-must-have"],
},

{
"title": "[3.4] Build worker decline + cascade to next worker",
"body": """## 📁 What this issue is about

When a worker declines, the system should automatically offer the job to the next-ranked worker.
If all workers decline, the booking is cancelled.

## ⚠️ Do this first: #52 (accept endpoint, same router file)

## 📋 Exactly what to do

Add decline handling to the `PUT /booking-offers/{offer_id}` endpoint:

```python
if data.action == "decline":
    offer.status = "declined"
    db.commit()
    # Find next eligible worker (rank > current offer's rank)
    next_worker = get_next_worker(booking, current_rank=offer.rank_at_offer, db=db)
    if next_worker:
        # Create new BookingOffer for next_worker
        # rank_at_offer = offer.rank_at_offer + 1
        # Store dispatch_score (immutable after this)
        # expires_at = now + 2 minutes
    else:
        booking.status = "cancelled"
```

Write tests:
- Worker declines → new offer created for rank-2 worker
- All workers decline → booking cancelled

## ✅ How to know it's done

- [ ] Decline creates a new offer for the next ranked worker
- [ ] All decline → booking.status = 'cancelled'
- [ ] Tests pass

---
**Depends on:** #52 (accept endpoint)""",
"labels": ["epic-3", "backend", "p0-must-have"],
},

{
"title": "[3.5] Build lazy offer expiry (auto-skip if worker doesn't respond in 2 min)",
"body": """## 📁 What this issue is about

If a worker doesn't respond to an offer within 2 minutes, the offer expires automatically.
We check for expiry every time someone reads or acts on an offer — no background job needed.

## ⚠️ Do this first: #53 (decline + cascade)

## 📋 Exactly what to do

Create a helper function in `backend/app/services/booking.py`:

```python
from datetime import datetime, timezone

def check_and_expire_offer(offer, db: Session):
    \"\"\"
    Call this at the start of any function that reads an offer.
    If the offer is expired, mark it expired and cascade to next worker.
    \"\"\"
    now = datetime.now(timezone.utc)
    if offer.status == "offered" and offer.expires_at < now:
        offer.status = "expired"
        db.commit()
        # trigger cascade (same logic as decline)
        cascade_to_next_worker(offer, db)
```

Call `check_and_expire_offer(offer, db)` at the start of:
- `GET /booking-offers/booking/{booking_id}`
- `PUT /booking-offers/{offer_id}`

Write a test:
- Create an offer with `expires_at` in the past
- Call any endpoint that reads it
- Verify the offer status = 'expired' and a new offer was created

## ✅ How to know it's done

- [ ] Expired offer is auto-marked on the next read
- [ ] Cascade creates next offer after expiry
- [ ] Test passes

---
**Depends on:** #53 (cascade logic)""",
"labels": ["epic-3", "backend", "p0-must-have"],
},

{
"title": "[3.6] Build GET /booking-offers/booking/{id} — offer audit trail API",
"body": """## 📁 What this issue is about

Build the endpoint that shows the full history of offers for a booking.
This is what the federation view uses to show the cascade demo.

## ⚠️ Do this first: #54 (expiry — so the audit trail includes expired offers too)

## 📋 Exactly what to do

Add to `backend/app/routers/offers.py`:

```python
@router.get("/booking-offers/booking/{booking_id}")
def get_offer_trail(booking_id: str, db: Session = Depends(get_db)):
    offers = (
        db.query(BookingOffer)
        .filter(BookingOffer.booking_id == booking_id)
        .order_by(BookingOffer.rank_at_offer)
        .all()
    )
    return [
        {
            "worker_name": offer.worker.name,
            "rank_at_offer": offer.rank_at_offer,
            "dispatch_score": float(offer.dispatch_score),  # stored value, NOT recomputed
            "status": offer.status,
            "created_at": offer.created_at.isoformat(),
        }
        for offer in offers
    ]
```

## ✅ How to know it's done

- [ ] After a cascade (Suresh declines → Priya offered → Priya accepts), the endpoint returns 2 rows
- [ ] `dispatch_score` is the value stored at offer time (not recomputed)
- [ ] Rows are ordered by `rank_at_offer` ascending

---
**Depends on:** #54 (expiry)""",
"labels": ["epic-3", "backend", "p0-must-have"],
},

{
"title": "[3.7] Build the booking status page (citizen UI)",
"body": """## 📁 What this issue is about

Build the page citizens see after creating a booking — it shows whether a worker has been found.

## ⚠️ Do this first: #42 (routing), #50, #51, #52 (booking + offer APIs)

## 📋 Exactly what to do

Create `src/pages/BookingStatusPage.tsx`:

Three visual states based on `booking.status`:

**1. Pending** — "Finding a worker..."
- Subtle pulsing green dot + text
- Uses `--color-brand-light` background

**2. Assigned** — Worker card
- Worker name (large, bold)
- "Society Verified ✓" badge in green (if verified)
- Rating: ★★★★☆
- Skill + distance

**3. Completed** — Summary
- Job price
- Worker payout: ₹X (95%)
- Cooperative Welfare Fund: ₹X (5%) — use `--color-welfare` violet
- "Rate [Worker Name]" button

**Notion-style design:**
- White cards with `var(--shadow-sm)`
- Generous whitespace with `var(--space-6)`
- Status text in `var(--color-text-secondary)`
- No heavy gradients

Use `useQuery` (TanStack Query) to poll the booking status every 3 seconds.

## ✅ How to know it's done

- [ ] Pending state shows animated pulse
- [ ] Assigned state shows worker card with name and badge
- [ ] Completed state shows the 95/5 split with violet welfare chip
- [ ] Page auto-updates without a page refresh

---
**Depends on:** #50–55 (all booking APIs)""",
"labels": ["epic-3", "frontend", "p0-must-have"],
},

{
"title": "[3.8] Build the booking creation form (citizen UI — 4 steps)",
"body": """## 📁 What this issue is about

Build the booking form — citizens pick a skill, enter their location, add an optional note, and submit.

## ⚠️ Do this first: #56 (booking status page — you need to redirect there after submit)

## 📋 Exactly what to do

Create `src/pages/BookingPage.tsx` with a 4-step flow:

**Step 1 — Choose service:**
- 10 skill chips in a grid: Electrician ⚡, Plumber 🔧, Carpenter 🪵, etc.
- Tapping a chip selects it and shows a "Next →" button

**Step 2 — Enter location:**
- Two text inputs: Latitude, Longitude (with helpful label: "Get your coordinates from Google Maps")
- A simple help link: "How do I find my coordinates?"

**Step 3 — Optional note:**
- Textarea: "Describe the problem (optional)"
- Character count

**Step 4 — Confirm and submit:**
- Summary card: Service, Location, Estimated price
- "Book Now" button → calls `POST /bookings`
- On success → redirect to `/booking/:id`

**Notion-style design:**
- Step indicator at top (dots or "Step 1 of 4")
- Each step is a clean white card
- Back button on steps 2–4

## ✅ How to know it's done

- [ ] Can navigate through all 4 steps
- [ ] Submit creates a booking and redirects to `/booking/:id`
- [ ] Error shown if API fails

---
**Depends on:** #50 (create booking API), #56 (booking status page to redirect to)""",
"labels": ["epic-3", "frontend", "p0-must-have"],
},

{
"title": "[3.9] Build the worker offer inbox (worker UI)",
"body": """## 📁 What this issue is about

Build the page workers see when they receive a job offer — they can accept or decline.

## ⚠️ Do this first: #52, #53 (accept/decline APIs)

## 📋 Exactly what to do

Create `src/pages/WorkerOffersPage.tsx`:

**Offer card design:**
- Left green accent bar (4px, `var(--color-brand)`)
- Job info: "Electrical job · 2.5 km away · ₹350"
- Citizen area (not full address)
- **Accept** button: full-width, green, large (min-height 56px)
- **Decline** button: full-width, red outline, below Accept

**Expiry countdown:**
- When less than 90 seconds remain, show a thin progress bar at top of card
- Changes from green to amber to red

**Accept flow:**
- Tap Accept → show a confirmation dialog: "Take this job? Your status will be set to Busy."
- Confirm → call API → show success message

**Empty state:**
- "No open offers right now. You'll be notified when a job matches your skill and area."
- Notion-style: simple text, no heavy illustration

Use `useQuery` to refresh offers every 5 seconds.

## ✅ How to know it's done

- [ ] Offer card shows with correct info
- [ ] Accept shows confirmation then calls API
- [ ] Decline calls API and removes offer from view
- [ ] Empty state shown when no offers

---
**Depends on:** #52, #53 (accept/decline APIs)""",
"labels": ["epic-3", "frontend", "p0-must-have"],
},


# ════════════════════════════════════════════════════════════════════════════
# EPIC 4 — COMPLETION & ECONOMICS
# ════════════════════════════════════════════════════════════════════════════

{
"title": "[4.1] Build PUT /bookings/{id}/complete endpoint",
"body": """## 📁 What this issue is about

Build the endpoint where a worker marks a job as done.
When the job completes, the platform fee (5%) is recorded and the worker becomes available again.

## ⚠️ Do this first: #52 (accept must work first)

## 📋 Exactly what to do

Add to `backend/app/routers/bookings.py`:

```python
@router.put("/bookings/{booking_id}/complete")
def complete_booking(
    booking_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    booking = db.query(Booking).filter_by(id=booking_id).first()
    # Check booking.worker_id == current_user.id → 403 if not
    # Check booking.status == 'assigned' → 400 if not
    booking.status = "completed"
    booking.platform_fee = booking.job_price * Decimal("0.05")
    worker_profile.availability = True
    db.commit()
    return {"message": "Job completed", "worker_payout": float(booking.job_price * Decimal("0.95"))}
```

Write tests:
- Assigned worker marks complete → 200
- Different worker tries to complete → 403

## ✅ How to know it's done

- [ ] Worker can mark their own booking complete → 200
- [ ] `platform_fee` is set to `job_price * 0.05`
- [ ] Worker's `availability` → True after completion
- [ ] Tests pass

---
**Depends on:** #52 (accept)""",
"labels": ["epic-4", "backend", "p0-must-have"],
},

{
"title": "[4.2] Build GET /wallet/{worker_id} — worker earnings endpoint",
"body": """## 📁 What this issue is about

Build the wallet API that shows a worker's earnings history.

## ⚠️ Do this first: #60 (job completion — need completed bookings to show)

## 📋 Exactly what to do

Add to `backend/app/routers/workers.py` or create `backend/app/routers/wallet.py`:

```python
@router.get("/wallet/{worker_id}")
def get_wallet(worker_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Only the worker themselves (or admin) can see their wallet
    completed = db.query(Booking).filter(
        Booking.worker_id == worker_id,
        Booking.status == "completed"
    ).all()

    weekly_earnings = get_weekly_earnings(worker_id, db)  # from dispatch.py
    lifetime = sum(b.job_price * Decimal("0.95") for b in completed)

    return {
        "weekly_earnings": float(weekly_earnings),
        "lifetime_earnings": float(lifetime),
        "bookings": [
            {
                "date": b.created_at.date().isoformat(),
                "skill": b.skill,
                "job_price": float(b.job_price),
                "worker_payout": float(b.job_price * Decimal("0.95")),
                "platform_fee": float(b.platform_fee or 0),
            }
            for b in completed
        ]
    }
```

## ✅ How to know it's done

- [ ] Returns correct weekly_earnings for a worker with completed bookings
- [ ] Returns 0 for a new worker
- [ ] Booking list shows correct payout split

---
**Depends on:** #60 (completion — need completed bookings)""",
"labels": ["epic-4", "backend", "p0-must-have"],
},

{
"title": "[4.3] Build GET /welfare-fund/summary endpoint",
"body": """## 📁 What this issue is about

Build the endpoint that shows the total Cooperative Welfare Fund balance.
This is money collected from all completed jobs (5% of each job price).

## ⚠️ Do this first: #60 (completion — need platform_fee to be set)

## 📋 Exactly what to do

Add to a new router or existing one:

```python
@router.get("/welfare-fund/summary")
def get_welfare_fund(db: Session = Depends(get_db)):
    result = db.execute(
        text("SELECT COALESCE(SUM(platform_fee), 0) as total, COUNT(*) as count FROM bookings WHERE status = 'completed'")
    ).fetchone()
    return {
        "total_fees": float(result.total),
        "completed_bookings": result.count
    }
```

## ✅ How to know it's done

- [ ] Returns `{total_fees: 17.5, completed_bookings: 1}` after 1 completed job of ₹350
- [ ] Returns `{total_fees: 0, completed_bookings: 0}` when no completed jobs

---
**Depends on:** #60 (completion API)""",
"labels": ["epic-4", "backend", "p0-must-have"],
},

{
"title": "[4.4] Build worker wallet page (UI)",
"body": """## 📁 What this issue is about

Build the wallet page workers see after completing jobs — shows earnings history.

## ⚠️ Do this first: #61 (wallet API)

## 📋 Exactly what to do

Create `src/pages/WorkerWalletPage.tsx`:

**Top section:**
- Large weekly earnings number in monospace font (`var(--font-mono)`)
- Label: "Earned this week"
- Resets every Monday automatically

**Earnings table:**
| Date | Service | Job Price | Your Cut (95%) | Welfare Fund (5%) |
|---|---|---|---|---|

**Notion-style design:**
- Clean table with thin `var(--color-border)` dividers
- No zebra striping — simple whitespace separation
- Welfare Fund column in `var(--color-welfare)` violet text
- Monospace font for all numbers

**Empty state:**
- "No completed jobs yet. Accept your first offer to start earning."

After marking a job complete (from the offers page), the weekly earnings chip animates upward.

## ✅ How to know it's done

- [ ] Weekly earnings shown in monospace
- [ ] Table shows completed jobs with correct split
- [ ] Violet color used for welfare fund column
- [ ] Empty state shown for new workers

---
**Depends on:** #61 (wallet API)""",
"labels": ["epic-4", "frontend", "p0-must-have"],
},

{
"title": "[4.5] Add mark-complete button and welfare fund chip to worker dashboard",
"body": """## 📁 What this issue is about

Add the UI for marking a job complete and showing the welfare fund contribution.

## ⚠️ Do this first: #64 (wallet page), #60 (completion API)

## 📋 Exactly what to do

In `src/pages/WorkerDashboard.tsx` (or offers page), when a job is `assigned`:

1. Show the job details card
2. Show a large "Mark as Complete" button (green, full-width)
3. On tap: call `PUT /bookings/{id}/complete`
4. On success: show a toast notification:
   - "₹X added to your wallet" (green)
   - "₹Y added to the Cooperative Welfare Fund" (violet)
5. Weekly earnings counter animates upward (count-up, 500ms)

**Welfare fund chip (after completion on citizen side too):**
- Small violet pill: "₹17.50 → Cooperative Welfare Fund"
- Use `var(--color-welfare)` and `var(--color-welfare-light)`

## ✅ How to know it's done

- [ ] "Mark Complete" button appears when job is assigned
- [ ] Tapping it calls the API and shows toast
- [ ] Welfare fund amount shown in violet

---
**Depends on:** #60 (completion API)""",
"labels": ["epic-4", "frontend", "p0-must-have"],
},


# ════════════════════════════════════════════════════════════════════════════
# EPIC 5 — ADMIN, RATING, FEDERATION
# ════════════════════════════════════════════════════════════════════════════

{
"title": "[5.1] Build PATCH /admin/workers/{id}/verify endpoint",
"body": """## 📁 What this issue is about

Build the admin endpoint to verify workers.
Unverified workers don't appear in the dispatch list — only verified cooperative workers do.

## ⚠️ Do this first: #49 (GET /workers — verification is already filtered there)

## 📋 Exactly what to do

Add to `backend/app/routers/admin.py`:

```python
@router.patch("/admin/workers/{worker_id}/verify")
def verify_worker(
    worker_id: str,
    data: dict,  # {"verified": true}
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "admin":
        raise HTTPException(403, "Admin only")
    profile = db.query(WorkerProfile).filter_by(user_id=worker_id).first()
    profile.verified = data.get("verified", True)
    db.commit()
    return {"message": "Updated", "verified": profile.verified}
```

For the hackathon demo: the seed script sets all workers as `verified=True` automatically.

## ✅ How to know it's done

- [ ] Admin can toggle worker verified status
- [ ] Unverified worker disappears from `GET /workers`
- [ ] Non-admin gets 403

---
**Depends on:** #49 (dispatch endpoint — so verification affects dispatch)""",
"labels": ["epic-5", "backend", "p1-should-have"],
},

{
"title": "[5.2] Build POST /bookings/{id}/rating endpoint",
"body": """## 📁 What this issue is about

Build the rating endpoint where a citizen rates a worker after a completed job (1–5 stars).
Ratings feed into the dispatch algorithm — higher rated workers score better.

## ⚠️ Do this first: #60 (job completion must work first)

## 📋 Exactly what to do

Add to `backend/app/routers/bookings.py`:

```python
@router.post("/bookings/{booking_id}/rating")
def submit_rating(
    booking_id: str,
    data: dict,  # {"rating": 4}
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    booking = db.query(Booking).filter_by(id=booking_id).first()
    # Check: booking.citizen_id == current_user.id
    # Check: booking.status == 'completed'
    # Check: booking.rating is None (prevent double rating → 409)
    # Validate: 1 <= data["rating"] <= 5 → 422 if not
    booking.rating = data["rating"]
    # Update worker_profiles.rating = running average of all ratings
    db.commit()
```

## ✅ How to know it's done

- [ ] Valid rating (1–5) updates worker's rating average
- [ ] Rating a second time → 409
- [ ] Rating outside 1–5 → 422
- [ ] Tests pass

---
**Depends on:** #60 (completion)""",
"labels": ["epic-5", "backend", "p1-should-have"],
},

{
"title": "[5.3] Build the rating UI (star input after job completes)",
"body": """## 📁 What this issue is about

Add the star rating UI to the booking status page after a job is completed.

## ⚠️ Do this first: #56 (booking status page), #67 (rating API)

## 📋 Exactly what to do

In `src/pages/BookingStatusPage.tsx`, when `status === 'completed'` and no rating submitted yet:

1. Show: "How was [Worker Name]?"
2. 5 star buttons (★★★★★)
3. "Submit Rating" button
4. On submit: call rating API
5. On success: replace stars with "Thank you for your feedback!"

Also add a "Society Verified ✓" badge component to `src/components/VerifiedBadge.tsx`:
```tsx
export function VerifiedBadge() {
  return (
    <span style={{
      background: 'var(--color-brand-light)',
      color: 'var(--color-brand)',
      padding: '2px 8px',
      borderRadius: 'var(--radius-full)',
      fontSize: 'var(--text-xs)',
      fontWeight: 600,
    }}>
      ✓ Society Verified
    </span>
  )
}
```

Show this badge on any worker card where `verified === true`.

## ✅ How to know it's done

- [ ] Stars render and are clickable
- [ ] Submitting a rating calls the API
- [ ] Verified badge shows on assigned worker card

---
**Depends on:** #56 (booking status page UI), #67 (rating API)""",
"labels": ["epic-5", "frontend", "p1-should-have"],
},

{
"title": "[5.4] Build the federation / ministry view (UI)",
"body": """## 📁 What this issue is about

Build a read-only dashboard for judges and ministry officials to verify the platform's fairness.
This is the most important UI for the hackathon judges.

## ⚠️ Do this first: #55 (audit trail API), #62 (welfare fund API)

## 📋 Exactly what to do

Create `src/pages/FederationPage.tsx`:

**Three summary counters at top:**
| Registered Workers | Completed Bookings | Cooperative Welfare Fund |
|---|---|---|
| 6 | 3 | ₹52.50 |

Welfare Fund counter uses a violet background (`var(--color-welfare-light)` background, `var(--color-welfare)` text).

**Booking list:**
- Table of all bookings: ID, Skill, Date, Status
- Click a row → expand to show the offer cascade

**Offer cascade for a booking:**
```
Rank | Worker Name      | Dispatch Score | Status
1    | Suresh Kumar     | 12,550         | Declined
2    | Priya Gupta      | 12,000         | Declined
3    | Anil Yadav       | 9,750          | Declined
4    | Meena Verma      | 5,750          | Accepted
```
- Dispatch scores in monospace font
- "Accepted" row highlighted in green

**Notion-style design:**
- Plain table, no heavy borders
- Thin `var(--color-border)` dividers
- Clean typography, lots of whitespace
- Expandable rows (click to show cascade)

## ✅ How to know it's done

- [ ] Welfare fund counter shows correct total in violet
- [ ] Booking list loads and is clickable
- [ ] Cascade table shows all 4 workers with ranks and scores for the demo booking

---
**Depends on:** #55 (audit trail API), #62 (welfare fund API)""",
"labels": ["epic-5", "frontend", "p0-must-have"],
},

{
"title": "[5.5] Write integration tests for the full booking cascade",
"body": """## 📁 What this issue is about

Write automated tests that simulate the full demo flow: book → offer → decline × 3 → accept → complete → rate.
This ensures nothing is broken before the hackathon presentation.

## ⚠️ Do this first: All Epic 3 and 4 backend issues

## 📋 Exactly what to do

Create `backend/tests/test_cascade.py`:

```python
def test_full_cascade():
    # 1. Register 1 citizen + 4 workers
    # 2. Seed data so workers have correct weekly earnings
    # 3. Citizen creates a booking
    # 4. Check: offer created for rank-1 worker (Suresh)
    # 5. Suresh declines → check: offer created for rank-2 (Priya)
    # 6. Priya declines → check: offer created for rank-3 (Anil)
    # 7. Anil declines → check: offer created for rank-4 (Meena)
    # 8. Meena accepts → check: booking.status == 'assigned'
    # 9. Meena marks complete → check: platform_fee set, availability=True
    # 10. Citizen rates Meena 4 stars → check: worker rating updated
    # 11. GET /welfare-fund/summary → check: total_fees > 0
    # 12. GET /booking-offers/booking/{id} → check: 4 rows in correct order
```

## ✅ How to know it's done

- [ ] Test runs and passes in CI (GitHub Actions)
- [ ] All 12 checks pass
- [ ] Test runs in < 10 seconds

---
**Depends on:** All Epic 3 + 4 backend issues""",
"labels": ["epic-5", "backend", "p0-must-have"],
},

{
"title": "[5.6] Final demo validation checklist",
"body": """## 📁 What this issue is about

This is the final pre-demo verification. Go through this checklist with the full team before the presentation.
It's not a coding task — it's a testing and fixing task.

## 📋 Exactly what to do

Go through each item and fix any issues found:

### Backend checks:
- [ ] `python app/seed.py` runs without errors
- [ ] `GET /workers?skill=electrician&lat=26.9124&lng=75.7873` returns: Suresh (rank 1) > Priya (rank 2) > Anil (rank 3) > Meena (rank 4)
- [ ] All 4 dispatch scores roughly match Appendix A of PRD
- [ ] `pytest tests/` — all tests pass
- [ ] `GET /welfare-fund/summary` after cascade demo → shows correct total

### Frontend checks:
- [ ] Login and register work for both roles
- [ ] Citizen can create a booking
- [ ] Worker offer card loads and shows the expiry countdown
- [ ] Accept and decline work
- [ ] Mark complete → wallet updates → welfare fund chip shows in violet
- [ ] Rating UI works and shows confirmation
- [ ] Federation view shows 4-row cascade table with correct dispatch scores

### Design checks:
- [ ] All colors come from tokens.css (no hardcoded hex values)
- [ ] Text contrast is readable (check at least brand green on white)
- [ ] Mobile layout works at 375px width (test in browser DevTools)
- [ ] No broken layout on the cascade table at desktop width

### Performance:
- [ ] Initial page load < 3 seconds
- [ ] No console errors in the browser

---
**Depends on:** Everything else — do this last""",
"labels": ["epic-5", "fullstack", "p0-must-have"],
},

]

def create_issue(issue, index):
    labels = ",".join(issue["labels"])
    cmd = [
        "gh", "issue", "create",
        "--title", issue["title"],
        "--body", issue["body"],
        "--label", labels,
        "--repo", REPO,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if result.returncode == 0:
        url = result.stdout.strip()
        number = url.split("/")[-1]
        print(f"  ✅ #{number} [{index+1}/{len(issues)}] {issue['title'][:60]}")
        return int(number)
    else:
        print(f"  ❌ [{index+1}/{len(issues)}] FAILED: {issue['title'][:60]}")
        print(f"     {result.stderr.strip()[:200]}")
        return None
    time.sleep(1.0)

print(f"Creating {len(issues)} issues on {REPO}...")
numbers = []
for i, issue in enumerate(issues):
    n = create_issue(issue, i)
    numbers.append(n)
    time.sleep(1.0)

print(f"\n✅ Done! Created {sum(1 for n in numbers if n)} / {len(issues)} issues")
print("\nIssue number map (for 'depends on' links):")
for i, (issue, n) in enumerate(zip(issues, numbers)):
    if n:
        print(f"  #{n}: {issue['title'][:70]}")
