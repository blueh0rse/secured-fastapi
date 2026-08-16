"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.users import router as users_router

app = FastAPI(
    title="Users API",
    description="A small internal service for managing user accounts.",
    version="1.0.0",
    debug=True,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
