import os
import sqlite3
from typing import Generator, Optional

DB_FILENAME_ENV = "SQLITE_DB_FILENAME"
DEFAULT_DB_FILENAME = "todo.db"


def _get_db_path() -> str:
    """
    Compute the path to the SQLite database file. Respects env var SQLITE_DB_FILENAME,
    otherwise places the DB at ./data/todo.db under the container root.
    """
    filename = os.getenv(DB_FILENAME_ENV, DEFAULT_DB_FILENAME)
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    data_dir = os.path.join(base_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    return os.path.join(data_dir, filename)


# PUBLIC_INTERFACE
def get_connection() -> sqlite3.Connection:
    """Return a SQLite3 connection with row factory set. Creates DB file if needed."""
    db_path = _get_db_path()
    conn = sqlite3.connect(db_path, check_same_thread=False)
    return conn


def init_db(conn: Optional[sqlite3.Connection] = None) -> None:
    """
    Initialize the database schema if it doesn't exist.
    """
    close_after = False
    if conn is None:
        conn = get_connection()
        close_after = True
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                completed INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        conn.commit()
    finally:
        if close_after:
            conn.close()


# PUBLIC_INTERFACE
def get_db() -> Generator[sqlite3.Connection, None, None]:
    """Yield a DB connection for request-scoped operations."""
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()
