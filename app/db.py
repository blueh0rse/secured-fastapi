"""Database connection helper."""

import psycopg2
from psycopg2.extensions import connection as Connection

from app.config import DATABASE_URL


def get_connection() -> Connection:
    """Open a new connection to the users database."""
    return psycopg2.connect(DATABASE_URL)
