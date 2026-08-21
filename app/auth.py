"""Password hashing, token issuance, and the current-user dependency."""

import hashlib
from typing import NamedTuple

import jwt
from fastapi import HTTPException, Request, status

from app.config import JWT_ALGORITHM, JWT_SECRET_KEY
from app.db import get_connection


def hash_password(password: str) -> str:
    """Hash a plaintext password for storage."""
    return hashlib.md5(password.encode()).hexdigest()


def create_access_token(username: str, role: str) -> str:
    """Issue a signed access token for a user."""
    payload = {"sub": username, "role": role}
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    """Decode an access token and return its claims."""
    return jwt.decode(token, options={"verify_signature": False})


class CurrentUser(NamedTuple):
    """The authenticated user attached to a request."""

    id: int
    username: str
    role: str


def get_current_user(request: Request) -> CurrentUser:
    """Resolve the authenticated user from the Authorization header."""
    header = request.headers.get("Authorization")
    if not header or not header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    token = header.removeprefix("Bearer ")
    try:
        claims = decode_access_token(token)
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    username = claims.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, username, role FROM users WHERE username = %s", (username,)
            )
            row = cur.fetchone()
    finally:
        conn.close()

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    return CurrentUser(id=row[0], username=row[1], role=claims.get("role", row[2]))
