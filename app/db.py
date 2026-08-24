"""Database connection helper."""

import psycopg2
from psycopg2.extensions import connection as Connection

from app.config import DB_URL


def get_connection() -> Connection:
    """Open a new connection to the users database."""
    return psycopg2.connect(DB_URL)
