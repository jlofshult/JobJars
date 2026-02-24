from datetime import timedelta

from fastapi import APIRouter, HTTPException, status
from tinydb import Query

from app.auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    get_current_user,
    verify_password,
)
from app.database import users_table
from app.models import LoginRequest, Token, UserResponse
from fastapi import Depends

router = APIRouter(prefix="/auth", tags=["auth"])


def _safe_user(user: dict) -> dict:
    """Return user dict without the password hash."""
    return {k: v for k, v in user.items() if k != "password_hash"}


@router.post("/login", response_model=Token)
def login(request: LoginRequest):
    User = Query()
    table = users_table()
    user = table.get(User.username == request.username)

    if user is None or not verify_password(request.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": user["id"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": _safe_user(user),
    }


@router.get("/me", response_model=UserResponse)
def get_me(current_user: dict = Depends(get_current_user)):
    return _safe_user(current_user)
