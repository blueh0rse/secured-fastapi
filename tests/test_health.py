"""Tests for the health check endpoint."""

from httpx import AsyncClient


async def test_health_returns_ok(client_anon: AsyncClient) -> None:
    """The health endpoint reports the service as running."""
    response = await client_anon.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
