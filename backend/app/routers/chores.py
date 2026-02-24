from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from tinydb import Query

from app.auth import get_current_user, require_parent
from app.database import assignments_table, chores_table, users_table
from app.models import (
    AssignmentResponse,
    ChoreCreate,
    ChoreResponse,
    ChoreUpdate,
    RejectAssignmentRequest,
)

router = APIRouter(prefix="/chores", tags=["chores"])


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _get_chore_or_404(chore_id: str) -> dict:
    Chore = Query()
    chore = chores_table().get(Chore.id == chore_id)
    if chore is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chore not found")
    return chore


def _get_assignment_or_404(assignment_id: str) -> dict:
    Assign = Query()
    assignment = assignments_table().get(Assign.id == assignment_id)
    if assignment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found"
        )
    return assignment


# ---------------------------------------------------------------------------
# Chore CRUD
# ---------------------------------------------------------------------------

@router.get("", response_model=list[ChoreResponse])
def list_chores(current_user: dict = Depends(get_current_user)):
    Chore = Query()
    table = chores_table()

    if current_user["role"] == "parent":
        chores = table.search(Chore.parent_id == current_user["id"])
    else:
        # Child: return active chores appropriate for child's age
        child_age = current_user.get("age") or 0
        all_chores = table.search(
            (Chore.is_active == True) & (Chore.parent_id == current_user["parent_id"])
        )
        chores = []
        for chore in all_chores:
            if chore["age_min"] <= child_age:
                age_max = chore.get("age_max")
                if age_max is None or child_age <= age_max:
                    chores.append(chore)

    return chores


@router.post("", response_model=ChoreResponse, status_code=status.HTTP_201_CREATED)
def create_chore(
    request: ChoreCreate,
    current_user: dict = Depends(require_parent),
):
    chore = {
        "id": str(uuid4()),
        "title": request.title,
        "description": request.description,
        "value": request.value,
        "chore_type": request.chore_type,
        "age_min": request.age_min,
        "age_max": request.age_max,
        "parent_id": current_user["id"],
        "is_active": True,
        "icon": request.icon,
        "created_at": datetime.utcnow().isoformat(),
    }
    chores_table().insert(chore)
    return chore


@router.put("/{chore_id}", response_model=ChoreResponse)
def update_chore(
    chore_id: str,
    request: ChoreUpdate,
    current_user: dict = Depends(require_parent),
):
    chore = _get_chore_or_404(chore_id)

    if chore["parent_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not own this chore",
        )

    updates = request.model_dump(exclude_none=True)
    if updates:
        Chore = Query()
        chores_table().update(updates, Chore.id == chore_id)

    Chore = Query()
    return chores_table().get(Chore.id == chore_id)


@router.delete("/{chore_id}", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_chore(
    chore_id: str,
    current_user: dict = Depends(require_parent),
):
    chore = _get_chore_or_404(chore_id)

    if chore["parent_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not own this chore",
        )

    Chore = Query()
    chores_table().update({"is_active": False}, Chore.id == chore_id)
    return None


# ---------------------------------------------------------------------------
# Assignments
# ---------------------------------------------------------------------------

@router.get("/assignments", response_model=list[AssignmentResponse])
def list_assignments(current_user: dict = Depends(get_current_user)):
    Assign = Query()
    table = assignments_table()

    if current_user["role"] == "parent":
        assignments = table.search(Assign.parent_id == current_user["id"])
    else:
        assignments = table.search(Assign.child_id == current_user["id"])

    return assignments


@router.post("/{chore_id}/claim", response_model=AssignmentResponse, status_code=status.HTTP_201_CREATED)
def claim_chore(
    chore_id: str,
    current_user: dict = Depends(get_current_user),
):
    if current_user["role"] != "child":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only children can claim chores",
        )

    chore = _get_chore_or_404(chore_id)

    if not chore.get("is_active"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This chore is not active",
        )

    # Age check
    child_age = current_user.get("age") or 0
    if child_age < chore["age_min"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You do not meet the minimum age requirement for this chore",
        )
    age_max = chore.get("age_max")
    if age_max is not None and child_age > age_max:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You exceed the maximum age for this chore",
        )

    Assign = Query()
    table = assignments_table()
    existing = table.search(
        (Assign.chore_id == chore_id) & (Assign.child_id == current_user["id"])
    )

    if chore["chore_type"] == "one-time":
        # Cannot claim if any non-rejected assignment exists
        active_or_approved = [
            a for a in existing if a["status"] in ("in_progress", "pending_approval", "approved")
        ]
        if active_or_approved:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already claimed or completed this one-time chore",
            )
    else:
        # Repetitive: cannot claim if there is an in-progress or pending_approval assignment
        blocking = [
            a for a in existing if a["status"] in ("in_progress", "pending_approval")
        ]
        if blocking:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You already have an active assignment for this chore",
            )

    assignment = {
        "id": str(uuid4()),
        "chore_id": chore_id,
        "child_id": current_user["id"],
        "parent_id": chore["parent_id"],
        "status": "in_progress",
        "claimed_at": datetime.utcnow().isoformat(),
        "completed_at": None,
        "approved_at": None,
        "rejected_reason": None,
    }
    table.insert(assignment)
    return assignment


@router.put("/assignments/{assignment_id}/complete", response_model=AssignmentResponse)
def complete_assignment(
    assignment_id: str,
    current_user: dict = Depends(get_current_user),
):
    if current_user["role"] != "child":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only children can mark chores complete",
        )

    assignment = _get_assignment_or_404(assignment_id)

    if assignment["child_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This is not your assignment",
        )

    if assignment["status"] != "in_progress":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot complete assignment with status '{assignment['status']}'",
        )

    Assign = Query()
    updates = {
        "status": "pending_approval",
        "completed_at": datetime.utcnow().isoformat(),
    }
    assignments_table().update(updates, Assign.id == assignment_id)

    return assignments_table().get(Assign.id == assignment_id)


@router.put("/assignments/{assignment_id}/approve", response_model=AssignmentResponse)
def approve_assignment(
    assignment_id: str,
    current_user: dict = Depends(require_parent),
):
    assignment = _get_assignment_or_404(assignment_id)

    if assignment["parent_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not manage this assignment",
        )

    if assignment["status"] != "pending_approval":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot approve assignment with status '{assignment['status']}'",
        )

    # Get chore value to add to child's balance
    Chore = Query()
    chore = chores_table().get(Chore.id == assignment["chore_id"])
    if chore is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated chore not found",
        )

    chore_value = chore["value"]

    # Update assignment
    Assign = Query()
    assignments_table().update(
        {"status": "approved", "approved_at": datetime.utcnow().isoformat()},
        Assign.id == assignment_id,
    )

    # Add value to child's balance
    User = Query()
    users_tbl = users_table()
    child = users_tbl.get(User.id == assignment["child_id"])
    if child:
        new_balance = round(child.get("balance", 0.0) + chore_value, 2)
        users_tbl.update({"balance": new_balance}, User.id == assignment["child_id"])

    return assignments_table().get(Assign.id == assignment_id)


@router.put("/assignments/{assignment_id}/reject", response_model=AssignmentResponse)
def reject_assignment(
    assignment_id: str,
    request: RejectAssignmentRequest,
    current_user: dict = Depends(require_parent),
):
    assignment = _get_assignment_or_404(assignment_id)

    if assignment["parent_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not manage this assignment",
        )

    if assignment["status"] != "pending_approval":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot reject assignment with status '{assignment['status']}'",
        )

    Assign = Query()
    assignments_table().update(
        {"status": "rejected", "rejected_reason": request.reason},
        Assign.id == assignment_id,
    )

    return assignments_table().get(Assign.id == assignment_id)
