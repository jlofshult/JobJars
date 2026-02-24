from typing import Optional, List
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Auth models
# ---------------------------------------------------------------------------

class LoginRequest(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict


# ---------------------------------------------------------------------------
# User / child models
# ---------------------------------------------------------------------------

class UserResponse(BaseModel):
    id: str
    username: str
    role: str
    name: str
    age: Optional[int] = None
    parent_id: Optional[str] = None
    balance: float = 0.0
    created_at: str


class CreateChildRequest(BaseModel):
    username: str
    password: str
    name: str
    age: int


class UpdateChildRequest(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    name: Optional[str] = None
    age: Optional[int] = None


# ---------------------------------------------------------------------------
# Chore models
# ---------------------------------------------------------------------------

class ChoreCreate(BaseModel):
    title: str
    description: str
    value: float
    chore_type: str = Field(default="one-time", pattern="^(one-time|repetitive)$")
    age_min: int = 5
    age_max: Optional[int] = None
    icon: str = "⭐"


class ChoreUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    value: Optional[float] = None
    chore_type: Optional[str] = Field(default=None, pattern="^(one-time|repetitive)$")
    age_min: Optional[int] = None
    age_max: Optional[int] = None
    icon: Optional[str] = None
    is_active: Optional[bool] = None


class ChoreResponse(BaseModel):
    id: str
    title: str
    description: str
    value: float
    chore_type: str
    age_min: int
    age_max: Optional[int] = None
    parent_id: str
    is_active: bool
    icon: str
    created_at: str


# ---------------------------------------------------------------------------
# Assignment models
# ---------------------------------------------------------------------------

class AssignmentResponse(BaseModel):
    id: str
    chore_id: str
    child_id: str
    parent_id: str
    status: str
    claimed_at: str
    completed_at: Optional[str] = None
    approved_at: Optional[str] = None
    rejected_reason: Optional[str] = None


class RejectAssignmentRequest(BaseModel):
    reason: str


# ---------------------------------------------------------------------------
# Redemption models
# ---------------------------------------------------------------------------

class RedemptionCreate(BaseModel):
    amount: float
    description: str


class RedemptionResponse(BaseModel):
    id: str
    child_id: str
    parent_id: str
    amount: float
    description: str
    status: str
    created_at: str
    resolved_at: Optional[str] = None


class RejectRedemptionRequest(BaseModel):
    reason: Optional[str] = None
