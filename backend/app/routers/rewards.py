from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from tinydb import Query

from app.auth import get_current_user, require_parent
from app.database import redemptions_table, users_table
from app.models import RedemptionCreate, RedemptionResponse, RejectRedemptionRequest

router = APIRouter(prefix="/rewards", tags=["rewards"])


def _get_redemption_or_404(redemption_id: str) -> dict:
    Redeem = Query()
    redemption = redemptions_table().get(Redeem.id == redemption_id)
    if redemption is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Redemption not found"
        )
    return redemption


@router.get("/balance")
def get_balance(current_user: dict = Depends(get_current_user)):
    """Return the current user's reward balance."""
    if current_user["role"] == "parent":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Balance is only available for children",
        )
    return {"balance": current_user.get("balance", 0.0)}


@router.get("/redemptions", response_model=list[RedemptionResponse])
def list_redemptions(current_user: dict = Depends(get_current_user)):
    Redeem = Query()
    table = redemptions_table()

    if current_user["role"] == "parent":
        redemptions = table.search(Redeem.parent_id == current_user["id"])
    else:
        redemptions = table.search(Redeem.child_id == current_user["id"])

    return redemptions


@router.post("/redeem", response_model=RedemptionResponse, status_code=status.HTTP_201_CREATED)
def request_redemption(
    request: RedemptionCreate,
    current_user: dict = Depends(get_current_user),
):
    if current_user["role"] != "child":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only children can request redemptions",
        )

    if request.amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Redemption amount must be positive",
        )

    current_balance = current_user.get("balance", 0.0)
    if request.amount > current_balance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient balance. Current balance: {current_balance}",
        )

    redemption = {
        "id": str(uuid4()),
        "child_id": current_user["id"],
        "parent_id": current_user["parent_id"],
        "amount": request.amount,
        "description": request.description,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat(),
        "resolved_at": None,
    }
    redemptions_table().insert(redemption)
    return redemption


@router.put("/redemptions/{redemption_id}/approve", response_model=RedemptionResponse)
def approve_redemption(
    redemption_id: str,
    current_user: dict = Depends(require_parent),
):
    redemption = _get_redemption_or_404(redemption_id)

    if redemption["parent_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not manage this redemption",
        )

    if redemption["status"] != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot approve redemption with status '{redemption['status']}'",
        )

    # Deduct from child's balance
    User = Query()
    users_tbl = users_table()
    child = users_tbl.get(User.id == redemption["child_id"])
    if child is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Child account not found",
        )

    current_balance = child.get("balance", 0.0)
    if redemption["amount"] > current_balance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Child has insufficient balance ({current_balance}) for this redemption",
        )

    new_balance = round(current_balance - redemption["amount"], 2)
    users_tbl.update({"balance": new_balance}, User.id == redemption["child_id"])

    # Update redemption status
    Redeem = Query()
    redemptions_table().update(
        {"status": "approved", "resolved_at": datetime.utcnow().isoformat()},
        Redeem.id == redemption_id,
    )

    return redemptions_table().get(Redeem.id == redemption_id)


@router.put("/redemptions/{redemption_id}/reject", response_model=RedemptionResponse)
def reject_redemption(
    redemption_id: str,
    request: RejectRedemptionRequest,
    current_user: dict = Depends(require_parent),
):
    redemption = _get_redemption_or_404(redemption_id)

    if redemption["parent_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not manage this redemption",
        )

    if redemption["status"] != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot reject redemption with status '{redemption['status']}'",
        )

    Redeem = Query()
    redemptions_table().update(
        {"status": "rejected", "resolved_at": datetime.utcnow().isoformat()},
        Redeem.id == redemption_id,
    )

    return redemptions_table().get(Redeem.id == redemption_id)
