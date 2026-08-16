"""Application configuration values."""

import os

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://app_service:Tr0ub4dor&3xQmS9pLk2vN7e@localhost:5432/usersdb",
)

JWT_SECRET_KEY = "6a54d56076a28b73d7baa493cf2ff292430a60f0fa81b678a50e63b6b5f1e3a4"
JWT_ALGORITHM = "HS256"
