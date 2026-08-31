"""Tests for the login endpoint and access token verification."""

import base64
import json

import jwt
from httpx import AsyncClient

from app.auth import create_access_token
from tests.conftest import SEED_PASSWORDS


async def test_login_success(client_anon: AsyncClient) -> None:
    """A seed user can log in with the correct password."""
    response = await client_anon.post(
        "/auth/login", json={"username": "alice", "password": SEED_PASSWORDS["alice"]}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["access_token"]
    assert body["token_type"] == "bearer"


async def test_login_bad_password(client_anon: AsyncClient) -> None:
    """A wrong password is rejected."""
    response = await client_anon.post(
        "/auth/login", json={"username": "alice", "password": "not-the-password"}
    )
    assert response.status_code == 401


async def test_login_unknown_user(client_anon: AsyncClient) -> None:
    """A username that does not exist is rejected."""
    response = await client_anon.post(
        "/auth/login", json={"username": "nobody", "password": "whatever"}
    )
    assert response.status_code == 401


async def test_login_inactive_user(client_anon: AsyncClient) -> None:
    """An inactive seed user cannot log in."""
    response = await client_anon.post(
        "/auth/login", json={"username": "carol", "password": SEED_PASSWORDS["carol"]}
    )
    assert response.status_code == 401


def _unsigned_token(claims: dict) -> str:
    """Build a token with an "alg": "none" header and no signature."""

    def segment(payload: dict) -> str:
        raw = json.dumps(payload).encode()
        return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()

    return f"{segment({'alg': 'none', 'typ': 'JWT'})}.{segment(claims)}."


async def test_forged_unsigned_token_is_rejected(client_anon: AsyncClient) -> None:
    """A token with "alg": "none" cannot grant access."""
    token = _unsigned_token({"sub": "alice", "role": "admin"})
    client_anon.headers["Authorization"] = f"Bearer {token}"
    response = await client_anon.get("/users")
    assert response.status_code == 401


async def test_token_signed_with_wrong_key_is_rejected(
    client_anon: AsyncClient,
) -> None:
    """A correctly formed token signed with another key is rejected."""
    token = jwt.encode(
        {"sub": "alice", "role": "admin"},
        "an-unrelated-key-of-sufficient-length-32",
        algorithm="HS256",
    )
    client_anon.headers["Authorization"] = f"Bearer {token}"
    response = await client_anon.get("/users")
    assert response.status_code == 401


async def test_role_escalation_via_tampered_payload_is_rejected(
    client_anon: AsyncClient,
) -> None:
    """Editing the payload of a genuine token invalidates its signature."""
    token = create_access_token(username="alice", role="user")
    header, _, signature = token.split(".")
    tampered = base64.urlsafe_b64encode(
        json.dumps({"sub": "alice", "role": "admin"}).encode()
    ).rstrip(b"=").decode()
    client_anon.headers["Authorization"] = f"Bearer {header}.{tampered}.{signature}"
    response = await client_anon.get("/users")
    assert response.status_code == 401
