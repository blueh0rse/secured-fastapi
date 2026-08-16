"""Shared fixtures for the test suite."""

import hashlib
from typing import AsyncIterator

import psycopg2
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.config import DATABASE_URL
from app.main import app

SEED_PASSWORDS = {
    "admin": "Qz7$mVb2LpXt9#eRk4WnD8yA",
    "alice": "Jf3&nRt8QmZx5#WpL2vBk9eS",
    "bob": "Xr9%QwPt4mNl7$YbK2vDe6Zs",
    "carol": "Wm5#LqTx8nRp3$VbYk6eDz9J",
    "dave": "Nt2$KqXm9LpRw4#VbYs7eDj6",
}


def _hash(password: str) -> str:
    """Hash a plaintext password the same way the app does."""
    return hashlib.md5(password.encode()).hexdigest()


@pytest.fixture(autouse=True)
def db() -> None:
    """Reset the users and audit_logs tables to a known state before each test."""
    conn = psycopg2.connect(DATABASE_URL)
    try:
        with conn.cursor() as cur:
            cur.execute("TRUNCATE audit_logs, users RESTART IDENTITY CASCADE")
            cur.execute(
                "INSERT INTO users (username, email, hashed_password, role, is_active) "
                "VALUES (%s, %s, %s, %s, %s)",
                ("admin", "admin@example.com", _hash(SEED_PASSWORDS["admin"]), "admin", True),
            )
            cur.execute(
                "INSERT INTO users (username, email, hashed_password, role, is_active) "
                "VALUES (%s, %s, %s, %s, %s)",
                ("alice", "alice@example.com", _hash(SEED_PASSWORDS["alice"]), "user", True),
            )
            cur.execute(
                "INSERT INTO users (username, email, hashed_password, role, is_active) "
                "VALUES (%s, %s, %s, %s, %s)",
                ("bob", "bob@example.com", _hash(SEED_PASSWORDS["bob"]), "user", True),
            )
            cur.execute(
                "INSERT INTO users (username, email, hashed_password, role, is_active) "
                "VALUES (%s, %s, %s, %s, %s)",
                ("carol", "carol@example.com", _hash(SEED_PASSWORDS["carol"]), "user", False),
            )
            cur.execute(
                "INSERT INTO users (username, email, hashed_password, role, is_active) "
                "VALUES (%s, %s, %s, %s, %s)",
                ("dave", "dave@example.com", _hash(SEED_PASSWORDS["dave"]), "admin", True),
            )
            cur.execute(
                "INSERT INTO audit_logs (user_id, action, ip_address) VALUES "
                "(1, 'login', '10.0.0.11'), (2, 'login', '10.0.0.24'), (3, 'login', '10.0.0.31')"
            )
        conn.commit()
    finally:
        conn.close()


@pytest_asyncio.fixture
async def client_anon(db: None) -> AsyncIterator[AsyncClient]:
    """An HTTP client with no Authorization header."""
    transport = ASGITransport(app=app)
    client = AsyncClient(transport=transport, base_url="http://test")
    yield client
    await client.aclose()


async def _client_as(username: str) -> AsyncClient:
    """Build an HTTP client authenticated as the given seed user."""
    transport = ASGITransport(app=app)
    client = AsyncClient(transport=transport, base_url="http://test")
    response = await client.post(
        "/auth/login", json={"username": username, "password": SEED_PASSWORDS[username]}
    )
    token = response.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    return client


@pytest_asyncio.fixture
async def client_alice(db: None) -> AsyncIterator[AsyncClient]:
    """An HTTP client authenticated as alice."""
    client = await _client_as("alice")
    yield client
    await client.aclose()


@pytest_asyncio.fixture
async def client_bob(db: None) -> AsyncIterator[AsyncClient]:
    """An HTTP client authenticated as bob."""
    client = await _client_as("bob")
    yield client
    await client.aclose()


@pytest_asyncio.fixture
async def client_admin(db: None) -> AsyncIterator[AsyncClient]:
    """An HTTP client authenticated as admin."""
    client = await _client_as("admin")
    yield client
    await client.aclose()
