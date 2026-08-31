"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import CORS_ALLOWED_ORIGINS
from app.routers.users import router as users_router

app = FastAPI(
    title="Users API",
    description="A small internal service for managing user accounts.",
    version="1.0.0",
    debug=True,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(users_router)


@app.get(
    "/health",
    tags=["health"],
    summary="Health check",
    description="Report whether the service is running.",
)
def health() -> dict:
    """Return a simple liveness indicator."""
    return {"status": "ok"}
