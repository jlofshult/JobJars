from datetime import datetime
from uuid import uuid4

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tinydb import Query

from app.auth import get_password_hash
from app.database import users_table
from app.routers import auth, chores, rewards, users

app = FastAPI(title="JobJars API", version="1.0.0")

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(chores.router, prefix="/api")
app.include_router(rewards.router, prefix="/api")


# ---------------------------------------------------------------------------
# Startup: seed default parent account
# ---------------------------------------------------------------------------

@app.on_event("startup")
def seed_default_parent() -> None:
    table = users_table()
    if len(table.all()) == 0:
        default_parent = {
            "id": str(uuid4()),
            "username": "parent",
            "password_hash": get_password_hash("parent123"),
            "role": "parent",
            "name": "Parent",
            "age": None,
            "parent_id": None,
            "balance": 0.0,
            "created_at": datetime.utcnow().isoformat(),
        }
        table.insert(default_parent)
        print("[JobJars] Default parent account created: username='parent', password='parent123'")


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.get("/", tags=["health"])
def root():
    return {"status": "ok", "app": "JobJars API", "version": "1.0.0"}


@app.get("/health", tags=["health"])
def health():
    return {"status": "healthy"}
