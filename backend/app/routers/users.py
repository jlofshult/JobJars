from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from tinydb import Query

from app.auth import get_password_hash, require_parent, get_current_user
from app.database import users_table
from app.models import CreateChildRequest, UpdateChildRequest, UserResponse

router = APIRouter(prefix="/users", tags=["users"])


def _safe_user(user: dict) -> dict:
    return {k: v for k, v in user.items() if k != "password_hash"}


@router.get("/children", response_model=list[UserResponse])
def list_children(current_user: dict = Depends(require_parent)):
    User = Query()
    table = users_table()
    children = table.search(
        (User.role == "child") & (User.parent_id == current_user["id"])
    )
    return [_safe_user(c) for c in children]


@router.post("/children", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_child(
    request: CreateChildRequest,
    current_user: dict = Depends(require_parent),
):
    User = Query()
    table = users_table()

    # Enforce unique username
    if table.get(User.username == request.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )

    child = {
        "id": str(uuid4()),
        "username": request.username,
        "password_hash": get_password_hash(request.password),
        "role": "child",
        "name": request.name,
        "age": request.age,
        "parent_id": current_user["id"],
        "balance": 0.0,
        "created_at": datetime.utcnow().isoformat(),
    }
    table.insert(child)
    return _safe_user(child)


@router.put("/children/{child_id}", response_model=UserResponse)
def update_child(
    child_id: str,
    request: UpdateChildRequest,
    current_user: dict = Depends(require_parent),
):
    User = Query()
    table = users_table()

    child = table.get(User.id == child_id)
    if child is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Child not found")

    # Ensure child belongs to this parent
    if child.get("parent_id") != current_user["id"] or child.get("role") != "child":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this child",
        )

    updates: dict = {}

    if request.username is not None:
        # Check uniqueness (exclude the child itself)
        existing = table.get(User.username == request.username)
        if existing and existing["id"] != child_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists",
            )
        updates["username"] = request.username

    if request.password is not None:
        updates["password_hash"] = get_password_hash(request.password)

    if request.name is not None:
        updates["name"] = request.name

    if request.age is not None:
        updates["age"] = request.age

    if updates:
        table.update(updates, User.id == child_id)

    # Re-fetch updated record
    updated_child = table.get(User.id == child_id)
    return _safe_user(updated_child)


@router.delete("/children/{child_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_child(
    child_id: str,
    current_user: dict = Depends(require_parent),
):
    User = Query()
    table = users_table()

    child = table.get(User.id == child_id)
    if child is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Child not found")

    if child.get("parent_id") != current_user["id"] or child.get("role") != "child":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this child",
        )

    table.remove(User.id == child_id)
    return None
