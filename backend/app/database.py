import os
from tinydb import TinyDB, Query
from tinydb.storages import JSONStorage
from pathlib import Path

# Resolve the data directory relative to this file's location (backend/app/database.py)
# We want backend/data/jobjars.json
_BASE_DIR = Path(__file__).resolve().parent.parent  # backend/
_DATA_DIR = _BASE_DIR / "data"
_DB_PATH = _DATA_DIR / "jobjars.json"


def _ensure_data_dir() -> None:
    _DATA_DIR.mkdir(parents=True, exist_ok=True)


def get_db() -> TinyDB:
    """Return a TinyDB instance pointing at the persistent JSON file."""
    _ensure_data_dir()
    return TinyDB(str(_DB_PATH), storage=JSONStorage, indent=2)


def users_table():
    return get_db().table("users")


def chores_table():
    return get_db().table("chores")


def assignments_table():
    return get_db().table("assignments")


def redemptions_table():
    return get_db().table("redemptions")
