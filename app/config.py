"""Application configuration values."""

import os

from dotenv import load_dotenv

load_dotenv()

DB_URL = os.environ.get("DB_URL", "NO_VALUE")
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "NO_VALUE")
JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM", "NO_VALUE")
CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get("CORS_ALLOWED_ORIGINS", "").split(",")
    if origin.strip()
]
