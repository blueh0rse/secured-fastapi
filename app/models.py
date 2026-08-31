"""Request and response schemas for the users API."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Credentials submitted to the login endpoint."""

    username: str
    password: str


class TokenResponse(BaseModel):
    """Access token returned after a successful login."""

    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    """Fields accepted when an administrator creates a user."""

    username: str
    email: str
    password: str = Field(max_length=72)
    role: str = "user"


class UserUpdate(BaseModel):
    """Fields accepted when updating an existing user."""

    email: Optional[str] = None
    password: Optional[str] = Field(default=None, max_length=72)
    role: Optional[str] = None
    is_active: Optional[bool] = None


class UserOut(BaseModel):
    """A user record as returned by the API."""

    id: int
    username: str
    email: str
    hashed_password: str
    role: str
    is_active: bool
    created_at: datetime


class AuditLogOut(BaseModel):
    """A single audit log entry as returned by the API."""

    id: int
    user_id: int
    action: str
    ip_address: Optional[str] = None
    created_at: datetime
