import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
import os


def get_db_path() -> str:
    return os.getenv("DB_PATH", "data/archai.db")


def _get_connection() -> sqlite3.Connection:
    db_path = get_db_path()
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def _ensure_table(conn: sqlite3.Connection):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            status TEXT NOT NULL,
            idea_summary TEXT
        )
    """)
    conn.commit()


def generate_session_id() -> str:
    return str(uuid.uuid4())[:8]


def save_session_metadata(session_id: str, idea_summary: str = "") -> None:
    conn = _get_connection()
    try:
        _ensure_table(conn)
        now = datetime.utcnow().isoformat()
        conn.execute(
            "INSERT OR REPLACE INTO sessions (session_id, created_at, updated_at, status, idea_summary) VALUES (?, ?, ?, ?, ?)",
            (session_id, now, now, "started", idea_summary),
        )
        conn.commit()
    finally:
        conn.close()


def update_session_status(session_id: str, status: str) -> None:
    conn = _get_connection()
    try:
        _ensure_table(conn)
        now = datetime.utcnow().isoformat()
        conn.execute(
            "UPDATE sessions SET status = ?, updated_at = ? WHERE session_id = ?",
            (status, now, session_id),
        )
        conn.commit()
    finally:
        conn.close()


def list_recent_sessions(limit: int = 10) -> list[dict]:
    conn = _get_connection()
    try:
        _ensure_table(conn)
        rows = conn.execute(
            "SELECT * FROM sessions ORDER BY updated_at DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()
