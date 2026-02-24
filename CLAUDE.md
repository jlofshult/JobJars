# CLAUDE.md — JobJars

This file provides context and guidance for AI assistants (Claude, Copilot, etc.) working in this repository.

---

## Project Overview

**JobJars** is a local web application that lets parents create a list of chores their kids can pick from and complete to earn rewards. Parents manage chores and approve completions; children claim chores, mark them done, and redeem their earned balance.

### Key Features
- Two login roles: **parent** and **child**
- Chores have a **reward value**, a **type** (one-time or repetitive), and an **age range**
- Children only see chores appropriate for their age
- Parents **approve** completed chores and reward redemption requests
- Reward **balance** accumulates per child and can be redeemed

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Vue 3 (Composition API, `<script setup>`) + Vite + Pinia + Vue Router 4 + Tailwind CSS v3 |
| Backend | Python 3.10+ + FastAPI + uvicorn |
| Database | TinyDB 4.8 (file-based NoSQL — `backend/data/jobjars.json`) |
| Auth | JWT (python-jose) + bcrypt (passlib) |
| HTTP client | Axios (frontend → backend via Vite proxy) |

---

## Repository Structure

```
JobJars/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI app, CORS, startup seeding
│   │   ├── database.py      # TinyDB instance + table helpers
│   │   ├── auth.py          # JWT/bcrypt utils + FastAPI dependencies
│   │   ├── models.py        # Pydantic v2 request/response models
│   │   └── routers/
│   │       ├── __init__.py
│   │       ├── auth.py      # /api/auth/login, /api/auth/me
│   │       ├── users.py     # /api/users/children CRUD
│   │       ├── chores.py    # /api/chores + assignments lifecycle
│   │       └── rewards.py   # /api/rewards balance + redemptions
│   ├── data/                # Auto-created; contains jobjars.json (git-ignored)
│   ├── requirements.txt
│   └── run.py               # uvicorn entry point
│
├── frontend/
│   ├── src/
│   │   ├── main.js
│   │   ├── App.vue
│   │   ├── style.css        # Tailwind directives
│   │   ├── api/
│   │   │   └── index.js     # Axios instance + all named API functions
│   │   ├── stores/
│   │   │   └── auth.js      # Pinia store: user, token, login/logout
│   │   ├── router/
│   │   │   └── index.js     # Routes + auth/role navigation guards
│   │   ├── components/
│   │   │   └── NavBar.vue
│   │   └── views/
│   │       ├── LoginView.vue
│   │       ├── parent/
│   │       │   ├── ParentDashboard.vue   # Stats + quick links
│   │       │   ├── ManageChores.vue      # Chore CRUD with modal form
│   │       │   ├── ManageChildren.vue    # Child account CRUD
│   │       │   └── ApprovalsView.vue     # Approve chores + redemptions
│   │       └── child/
│   │           ├── ChildDashboard.vue    # Claim + complete chores
│   │           └── RewardsView.vue       # Balance + redemption requests
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js       # Proxies /api → localhost:8000
│   ├── tailwind.config.js
│   └── postcss.config.js
│
├── .gitignore
├── CLAUDE.md                ← This file
└── README.md
```

---

## Development Workflow

### Running Locally

**Backend** (terminal 1):
```bash
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python run.py
# → http://localhost:8000  (Swagger UI at /docs)
```

**Frontend** (terminal 2):
```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

Default credentials seeded on first run: `parent` / `parent123`

### Branching

- Main branch: `main`
- Feature branches: `feature/<short-description>`
- Bug fixes: `fix/<short-description>`
- AI-generated branches: `claude/<session-id>`

### Commits

Use clear, imperative commit messages:
```
Add chore approval notification
Fix balance not updating after rejection
Update age filter logic for edge case
```

### Pull Requests

- Keep PRs focused on a single concern
- Reference related issues when applicable

---

## Commands

```bash
# Backend — install deps
pip install -r backend/requirements.txt

# Backend — start dev server
python backend/run.py

# Frontend — install deps
npm install --prefix frontend

# Frontend — start dev server
npm run dev --prefix frontend

# Frontend — production build
npm run build --prefix frontend
```

---

## Database Schema (TinyDB)

TinyDB stores all data in `backend/data/jobjars.json` as JSON tables.

### `users` table
| Field | Type | Notes |
|-------|------|-------|
| id | str (uuid4) | Primary key |
| username | str | Unique |
| password_hash | str | bcrypt |
| role | "parent" \| "child" | |
| name | str | Display name |
| age | int \| None | Children only |
| parent_id | str \| None | Children only |
| balance | float | Children only (default 0) |
| created_at | str | ISO datetime |

### `chores` table
| Field | Type | Notes |
|-------|------|-------|
| id | str | |
| title | str | |
| description | str | |
| value | float | Reward amount |
| chore_type | "one-time" \| "repetitive" | |
| age_min | int | |
| age_max | int \| None | |
| parent_id | str | Owner |
| is_active | bool | |
| icon | str | Emoji |
| created_at | str | |

### `assignments` table (chore lifecycle)
| Field | Type | Notes |
|-------|------|-------|
| id | str | |
| chore_id | str | |
| child_id | str | |
| parent_id | str | |
| status | "in_progress" \| "pending_approval" \| "approved" \| "rejected" | |
| claimed_at | str | |
| completed_at | str \| None | |
| approved_at | str \| None | |
| rejected_reason | str \| None | |

### `redemptions` table
| Field | Type | Notes |
|-------|------|-------|
| id | str | |
| child_id | str | |
| parent_id | str | |
| amount | float | |
| description | str | What they want |
| status | "pending" \| "approved" \| "rejected" | |
| created_at | str | |
| resolved_at | str \| None | |

---

## API Overview

All endpoints are under `/api`. Auth uses `Authorization: Bearer <jwt>`.

| Method | Path | Role | Description |
|--------|------|------|-------------|
| POST | /api/auth/login | any | Get JWT token |
| GET | /api/auth/me | any | Current user |
| GET | /api/users/children | parent | List children |
| POST | /api/users/children | parent | Create child |
| PUT | /api/users/children/{id} | parent | Update child |
| DELETE | /api/users/children/{id} | parent | Delete child |
| GET | /api/chores | both | Parent: all; Child: age-filtered |
| POST | /api/chores | parent | Create chore |
| PUT | /api/chores/{id} | parent | Update chore |
| DELETE | /api/chores/{id} | parent | Deactivate chore |
| GET | /api/chores/assignments | both | Assignments (scoped by role) |
| POST | /api/chores/{id}/claim | child | Claim a chore |
| PUT | /api/chores/assignments/{id}/complete | child | Mark done |
| PUT | /api/chores/assignments/{id}/approve | parent | Approve + credit balance |
| PUT | /api/chores/assignments/{id}/reject | parent | Reject with reason |
| GET | /api/rewards/balance | child | Current balance |
| GET | /api/rewards/redemptions | both | Redemptions (scoped by role) |
| POST | /api/rewards/redeem | child | Request redemption |
| PUT | /api/rewards/redemptions/{id}/approve | parent | Approve + deduct balance |
| PUT | /api/rewards/redemptions/{id}/reject | parent | Reject |

---

## Coding Conventions

### Python (Backend)
- FastAPI with dependency injection for auth (`get_current_user`, `require_parent`)
- Pydantic v2 for all request/response validation
- TinyDB `Query()` for all DB queries; never manipulate the JSON directly
- UUIDs (`str(uuid4())`) for all record IDs
- ISO datetime strings (`datetime.utcnow().isoformat()`) for timestamps
- Return HTTP 400/401/403/404 with descriptive `detail` messages

### JavaScript (Frontend)
- Vue 3 Composition API with `<script setup>` exclusively
- Pinia for all shared state; no component-level Vuex/global state
- All API calls go through `src/api/index.js` named functions
- `ref()` for primitives, reactive data; `computed()` for derived values
- `onMounted()` to fetch data; loading + error state per component
- Tailwind utility classes only — no separate CSS files except `style.css`

### General
- No secrets or `.env` files committed
- `backend/data/` is git-ignored (contains live DB)
- Keep functions small and single-purpose
- No speculative features — only implement what is requested

---

## Environment Variables

None required for local development. All configuration is hardcoded for local use.

If deploying, consider externalising:
```
SECRET_KEY=<random string for JWT signing>
DATABASE_PATH=<path to jobjars.json>
ALLOWED_ORIGINS=<comma-separated frontend URLs>
```

---

## AI Assistant Notes

- **Read before editing:** Always read existing files before modifying them
- **Minimal changes:** Only change what is necessary for the task
- **No speculative features:** Do not add features not explicitly requested
- **Branch discipline:** Always develop on the designated `claude/<session-id>` branch
- **Database:** Use TinyDB `Query()` — never manipulate `jobjars.json` directly
- **Auth pattern:** Backend deps `get_current_user` / `require_parent` handle all auth checks
- **Frontend API:** All HTTP calls go through `src/api/index.js` — do not use axios directly in components

---

_Last updated: 2026-02-24_
