"""Tests for the user management and audit log endpoints."""

from httpx import AsyncClient

ALICE_ID = 2
DAVE_ID = 5


async def test_list_users_requires_authentication(client_anon: AsyncClient) -> None:
    """A request with no Authorization header is rejected."""
    response = await client_anon.get("/users")
    assert response.status_code == 401


async def test_list_users_rejects_malformed_header(client_anon: AsyncClient) -> None:
    """A request with a malformed Authorization header is rejected."""
    client_anon.headers["Authorization"] = "Token not-a-bearer-token"
    response = await client_anon.get("/users")
    assert response.status_code == 401


async def test_list_users(client_alice: AsyncClient) -> None:
    """An authenticated user can list users."""
    response = await client_alice.get("/users")
    assert response.status_code == 200
    usernames = {user["username"] for user in response.json()}
    assert "alice" in usernames


async def test_get_user_by_id(client_alice: AsyncClient) -> None:
    """An authenticated user can fetch a user record by id."""
    response = await client_alice.get(f"/users/{ALICE_ID}")
    assert response.status_code == 200
    assert response.json()["username"] == "alice"


async def test_get_user_not_found(client_alice: AsyncClient) -> None:
    """A non-existent id returns 404."""
    response = await client_alice.get("/users/9999")
    assert response.status_code == 404


async def test_create_user_as_admin(client_admin: AsyncClient) -> None:
    """An administrator can create a new user."""
    response = await client_admin.post(
        "/users",
        json={
            "username": "erin",
            "email": "erin@example.com",
            "password": "a-fresh-password",
        },
    )
    assert response.status_code == 201
    assert response.json()["username"] == "erin"


async def test_create_user_invalid_payload(client_admin: AsyncClient) -> None:
    """A creation request missing a required field is rejected."""
    response = await client_admin.post("/users", json={"email": "erin@example.com"})
    assert response.status_code == 422


async def test_create_user_duplicate_username(client_admin: AsyncClient) -> None:
    """Creating a user with an existing username is rejected."""
    response = await client_admin.post(
        "/users",
        json={
            "username": "alice",
            "email": "alice2@example.com",
            "password": "another-password",
        },
    )
    assert response.status_code == 409


async def test_update_own_user(client_alice: AsyncClient) -> None:
    """A user can update their own record."""
    response = await client_alice.patch(
        f"/users/{ALICE_ID}", json={"email": "alice.new@example.com"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "alice.new@example.com"


async def test_delete_user_as_admin(client_admin: AsyncClient) -> None:
    """An administrator can delete a user."""
    response = await client_admin.delete(f"/users/{DAVE_ID}")
    assert response.status_code == 204


async def test_get_own_logs(client_alice: AsyncClient) -> None:
    """A user can read their own audit log entries."""
    response = await client_alice.get(f"/users/{ALICE_ID}/logs")
    assert response.status_code == 200
    assert all(entry["user_id"] == ALICE_ID for entry in response.json())
