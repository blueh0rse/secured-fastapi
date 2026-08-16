"""Tests for the login endpoint."""

from httpx import AsyncClient

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
