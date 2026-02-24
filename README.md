# JobJars 🫙

A web application for parents to create chore lists their kids can pick from, complete, and earn rewards.

## Features

- **Parent accounts** — create and manage chores, approve completions, manage children, approve reward redemptions
- **Child accounts** — view age-appropriate chores, claim and complete them, earn and redeem reward balances
- **Chore types** — one-time (claimable once) or repetitive (claimable again after approval)
- **Age filtering** — each chore has a minimum (and optional maximum) age so kids only see appropriate tasks
- **Reward system** — each chore has a point/dollar value; completed chores credit the child's balance; children request redemptions that parents approve

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Vue 3 + Vite + Pinia + Vue Router + Tailwind CSS |
| Backend | Python + FastAPI |
| Database | TinyDB (file-based NoSQL — no server required) |

---

## Prerequisites

- **Python 3.10+**
- **Node.js 18+** and **npm**

---

## Setup & Running

### 1. Backend

```bash
cd backend

# Create and activate a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the API server (runs on http://localhost:8000)
python run.py
```

The database file is created automatically at `backend/data/jobjars.json` on first run.

A default parent account is seeded automatically:
- **Username:** `parent`
- **Password:** `parent123`

> Change this password via the Manage Children screen after first login (or directly in the DB file).

### 2. Frontend

In a **separate terminal**:

```bash
cd frontend

# Install dependencies
npm install

# Start the dev server (runs on http://localhost:5173)
npm run dev
```

Open **http://localhost:5173** in your browser.

---

## First-Time Setup

1. Log in as **parent / parent123**
2. Go to **Children** → add your kids (name, username, password, age)
3. Go to **Chores** → create chores with values, types, and age ranges
4. Have each child log in and start picking chores!

---

## Project Structure

```
JobJars/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app, CORS, startup seeding
│   │   ├── database.py      # TinyDB setup (data/jobjars.json)
│   │   ├── auth.py          # JWT + bcrypt utilities, FastAPI deps
│   │   ├── models.py        # Pydantic request/response models
│   │   └── routers/
│   │       ├── auth.py      # POST /api/auth/login, GET /api/auth/me
│   │       ├── users.py     # CRUD for child accounts
│   │       ├── chores.py    # Chore CRUD + claim/complete/approve/reject
│   │       └── rewards.py   # Balance, redemption requests + approval
│   ├── requirements.txt
│   └── run.py               # uvicorn entry point
│
├── frontend/
│   ├── src/
│   │   ├── api/index.js         # Axios client + all API functions
│   │   ├── stores/auth.js       # Pinia auth store (token persistence)
│   │   ├── router/index.js      # Vue Router + auth/role guards
│   │   ├── components/
│   │   │   └── NavBar.vue
│   │   └── views/
│   │       ├── LoginView.vue
│   │       ├── parent/
│   │       │   ├── ParentDashboard.vue
│   │       │   ├── ManageChores.vue
│   │       │   ├── ManageChildren.vue
│   │       │   └── ApprovalsView.vue
│   │       └── child/
│   │           ├── ChildDashboard.vue
│   │           └── RewardsView.vue
│   ├── package.json
│   └── vite.config.js       # Proxies /api → localhost:8000
│
├── CLAUDE.md
└── README.md
```

---

## API Reference

The backend exposes a REST API at `http://localhost:8000/api`. Interactive docs are available at **http://localhost:8000/docs** (Swagger UI).

| Group | Endpoints |
|-------|-----------|
| Auth | `POST /api/auth/login`, `GET /api/auth/me` |
| Users | `GET/POST /api/users/children`, `PUT/DELETE /api/users/children/{id}` |
| Chores | `GET/POST /api/chores`, `PUT/DELETE /api/chores/{id}` |
| Assignments | `GET /api/chores/assignments`, `POST /api/chores/{id}/claim`, `PUT …/complete`, `PUT …/approve`, `PUT …/reject` |
| Rewards | `GET /api/rewards/balance`, `GET/POST /api/rewards/redemptions`, `PUT …/approve`, `PUT …/reject` |

---

## Development Notes

- The TinyDB JSON file (`backend/data/jobjars.json`) is the entire database — back it up to preserve data
- The Vite dev server proxies `/api/*` to `http://localhost:8000` so no CORS issues during development
- JWT tokens expire after 8 hours; logging out clears localStorage
- The `data/` directory is git-ignored to avoid committing user data
