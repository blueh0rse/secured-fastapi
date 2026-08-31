"""Shared fixtures for the test suite."""

import os
from typing import AsyncIterator

import psycopg2
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.auth import hash_password
from app.config import DB_URL
from app.main import app

ADMIN_PASS = os.environ.get("SEED_PASSWORD_ADMIN", "NO_VALUE")
ALICE_PASS = os.environ.get("SEED_PASSWORD_ALICE", "NO_VALUE")
BOB_PASS = os.environ.get("SEED_PASSWORD_BOB", "NO_VALUE")
CAROL_PASS = os.environ.get("SEED_PASSWORD_CAROL", "NO_VALUE")
DAVE_PASS = os.environ.get("SEED_PASSWORD_DAVE", "NO_VALUE")

SEED_PASSWORDS = {
    "admin": ADMIN_PASS,
    "alice": ALICE_PASS,
    "bob": BOB_PASS,
    "carol": CAROL_PASS,
    "dave": DAVE_PASS,
}


SEED_HASHES = {name: hash_password(pw) for name, pw in SEED_PASSWORDS.items()}


@pytest.fixture(autouse=True)
def db() -> None:
    """Reset the users and audit_logs tables to a known state before each test."""
    conn = psycopg2.connect(DB_URL)
    try:
        with conn.cursor() as cur:
            cur.execute("TRUNCATE audit_logs, users RESTART IDENTITY CASCADE")
            cur.execute(
                "INSERT INTO users (username, email, hashed_password, role, is_active) "
                "VALUES (%s, %s, %s, %s, %s)",
                (
                    "admin",
                    "admin@example.com",
                    SEED_HASHES["admin"],
                    "admin",
                    True,
                ),
            )
            cur.execute(
                "INSERT INTO users (username, email, hashed_password, role, is_active) "
                "VALUES (%s, %s, %s, %s, %s)",
                (
                    "alice",
                    "alice@example.com",
                    SEED_HASHES["alice"],
                    "user",
                    True,
                ),
            )
            cur.execute(
                "INSERT INTO users (username, email, hashed_password, role, is_active) "
                "VALUES (%s, %s, %s, %s, %s)",
                ("bob", "bob@example.com", SEED_HASHES["bob"], "user", True),
            )
            cur.execute(
                "INSERT INTO users (username, email, hashed_password, role, is_active) "
                "VALUES (%s, %s, %s, %s, %s)",
                (
                    "carol",
                    "carol@example.com",
                    SEED_HASHES["carol"],
                    "user",
                    False,
                ),
            )
            cur.execute(
                "INSERT INTO users (username, email, hashed_password, role, is_active) "
                "VALUES (%s, %s, %s, %s, %s)",
                (
                    "dave",
                    "dave@example.com",
                    SEED_HASHES["dave"],
                    "admin",
                    True,
                ),
            )
            cur.execute(
                "INSERT INTO audit_logs (user_id, action, ip_address) VALUES "
                "(1, 'login', '10.0.0.11'), (2, 'login', '10.0.0.24'), "
                "(3, 'login', '10.0.0.31')"
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
