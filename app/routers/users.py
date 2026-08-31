"""Endpoints for authentication, user management, and audit logs."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth import CurrentUser, create_access_token, get_current_user, hash_password
from app.db import get_connection
from app.models import (
    AuditLogOut,
    LoginRequest,
    TokenResponse,
    UserCreate,
    UserOut,
    UserUpdate,
)

router = APIRouter()

SORTABLE_COLUMNS = frozenset(
    {"id", "username", "email", "role", "is_active", "created_at"}
)


@router.post(
    "/auth/login",
    response_model=TokenResponse,
    tags=["auth"],
    summary="Authenticate a user",
    description="Verify a username and password and return an access token.",
)
def login(payload: LoginRequest) -> TokenResponse:
    """Check the submitted credentials and issue an access token."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT hashed_password, role, is_active FROM users "
                "WHERE username = %s",
                (payload.username,),
            )
            row = cur.fetchone()
    finally:
        conn.close()

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    hashed_password, role, is_active = row
    if hash_password(payload.password) != hashed_password or not is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    token = create_access_token(username=payload.username, role=role)
    return TokenResponse(access_token=token)


@router.get(
    "/users",
    response_model=List[UserOut],
    tags=["users"],
    summary="List users",
    description="Return the users table, optionally filtered and sorted.",
)
def list_users(
    search: Optional[str] = None,
    sort: Optional[str] = None,
    current_user: CurrentUser = Depends(get_current_user),
) -> List[UserOut]:
    """Return users, optionally filtered by username and sorted by a column."""
    query = (
        "SELECT id, username, email, hashed_password, role, is_active, created_at "
        "FROM users WHERE 1=1"
    )
    params: List[object] = []
    if search:
        query += " AND username ILIKE %s"
        params.append(f"%{search}%")
    if sort:
        if sort not in SORTABLE_COLUMNS:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="Invalid sort column",
            )
        query += f" ORDER BY {sort}"

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
            rows = cur.fetchall()
    finally:
        conn.close()

    return [
        UserOut(
            id=r[0],
            username=r[1],
            email=r[2],
            hashed_password=r[3],
            role=r[4],
            is_active=r[5],
            created_at=r[6],
        )
        for r in rows
    ]


@router.get(
    "/users/{user_id}",
    response_model=UserOut,
    tags=["users"],
    summary="Get a user",
    description="Return a single user by id.",
)
def get_user(
    user_id: int, current_user: CurrentUser = Depends(get_current_user)
) -> UserOut:
    """Return the user with the given id."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, username, email, hashed_password, role, "
                "is_active, created_at "
                "FROM users WHERE id = %s",
                (user_id,),
            )
            row = cur.fetchone()
    finally:
        conn.close()

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return UserOut(
        id=row[0],
        username=row[1],
        email=row[2],
        hashed_password=row[3],
        role=row[4],
        is_active=row[5],
        created_at=row[6],
    )


@router.post(
    "/users",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    tags=["users"],
    summary="Create a user",
    description="Create a new user account. Restricted to administrators.",
)
def create_user(
    payload: UserCreate, current_user: CurrentUser = Depends(get_current_user)
) -> UserOut:
    """Create a new user account."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not permitted"
        )

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM users WHERE username = %s", (payload.username,))
            if cur.fetchone() is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Username already exists",
                )

            cur.execute(
                "INSERT INTO users (username, email, hashed_password, role) "
                "VALUES (%s, %s, %s, %s) "
                "RETURNING id, username, email, hashed_password, role, "
                "is_active, created_at",
                (
                    payload.username,
                    payload.email,
                    hash_password(payload.password),
                    payload.role,
                ),
            )
            row = cur.fetchone()
        conn.commit()
    finally:
        conn.close()

    return UserOut(
        id=row[0],
        username=row[1],
        email=row[2],
        hashed_password=row[3],
        role=row[4],
        is_active=row[5],
        created_at=row[6],
    )


@router.patch(
    "/users/{user_id}",
    response_model=UserOut,
    tags=["users"],
    summary="Update a user",
    description="Update fields on an existing user account.",
)
def update_user(
    user_id: int,
    payload: UserUpdate,
    current_user: CurrentUser = Depends(get_current_user),
) -> UserOut:
    """Apply the submitted changes to a user account."""
    fields = []
    values: List[object] = []
    if payload.email is not None:
        fields.append("email = %s")
        values.append(payload.email)
    if payload.password is not None:
        fields.append("hashed_password = %s")
        values.append(hash_password(payload.password))
    if payload.role is not None:
        fields.append("role = %s")
        values.append(payload.role)
    if payload.is_active is not None:
        fields.append("is_active = %s")
        values.append(payload.is_active)

    if not fields:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="No fields to update",
        )

    values.append(user_id)
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"UPDATE users SET {', '.join(fields)} WHERE id = %s "
                "RETURNING id, username, email, hashed_password, role, "
                "is_active, created_at",
                values,
            )
            row = cur.fetchone()
        conn.commit()
    finally:
        conn.close()

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return UserOut(
        id=row[0],
        username=row[1],
        email=row[2],
        hashed_password=row[3],
        role=row[4],
        is_active=row[5],
        created_at=row[6],
    )


@router.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["users"],
    summary="Delete a user",
    description="Remove a user account. Restricted to administrators.",
)
def delete_user(
    user_id: int, current_user: CurrentUser = Depends(get_current_user)
) -> None:
    """Delete the user with the given id."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not permitted"
        )

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM users WHERE id = %s RETURNING id", (user_id,))
            row = cur.fetchone()
        conn.commit()
    finally:
        conn.close()

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )


@router.get(
    "/users/{user_id}/logs",
    response_model=List[AuditLogOut],
    tags=["users"],
    summary="List audit log entries",
    description="Return the audit log entries recorded for a user.",
)
def get_user_logs(
    user_id: int, current_user: CurrentUser = Depends(get_current_user)
) -> List[AuditLogOut]:
    """Return the audit log entries for the given user."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM users WHERE id = %s", (user_id,))
            if cur.fetchone() is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                )

            cur.execute(
                "SELECT id, user_id, action, ip_address, created_at "
                "FROM audit_logs WHERE user_id = %s ORDER BY created_at",
                (user_id,),
            )
            rows = cur.fetchall()
    finally:
        conn.close()

    return [
        AuditLogOut(
            id=r[0], user_id=r[1], action=r[2], ip_address=r[3], created_at=r[4]
        )
        for r in rows
    ]
