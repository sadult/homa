"""SQLite-backed memory: conversation history + long-term key/value facts."""
import json
import sqlite3
import time
from pathlib import Path

from config import settings

_conn: sqlite3.Connection | None = None


def _db() -> sqlite3.Connection:
    global _conn
    if _conn is None:
        _conn = sqlite3.connect(settings.DB_PATH, check_same_thread=False)
        _conn.row_factory = sqlite3.Row
        _init(_conn)
    return _conn


def _init(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            ts REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS facts (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            ts REAL NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_msg_session ON messages(session);
        """
    )
    conn.commit()


# ── Conversation history ─────────────────────────────────
def add_message(session: str, role: str, content: str) -> None:
    _db().execute(
        "INSERT INTO messages(session, role, content, ts) VALUES (?,?,?,?)",
        (session, role, content, time.time()),
    )
    _db().commit()


def get_history(session: str, limit: int = 12) -> list[dict]:
    rows = _db().execute(
        "SELECT role, content FROM messages WHERE session=? ORDER BY id DESC LIMIT ?",
        (session, limit),
    ).fetchall()
    return [{"role": r["role"], "content": r["content"]} for r in reversed(rows)]


def clear_history(session: str) -> int:
    cur = _db().execute("DELETE FROM messages WHERE session=?", (session,))
    _db().commit()
    return cur.rowcount


# ── Long-term facts ───────────────────────────────────
def remember(key: str, value: str) -> None:
    _db().execute(
        "INSERT INTO facts(key, value, ts) VALUES (?,?,?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value, ts=excluded.ts",
        (key, value, time.time()),
    )
    _db().commit()


def recall(key: str) -> str | None:
    row = _db().execute("SELECT value FROM facts WHERE key=?", (key,)).fetchone()
    return row["value"] if row else None


def search_facts(query: str) -> list[dict]:
    rows = _db().execute(
        "SELECT key, value FROM facts WHERE key LIKE ? OR value LIKE ?",
        (f"%{query}%", f"%{query}%"),
    ).fetchall()
    return [{"key": r["key"], "value": r["value"]} for r in rows]


def list_facts() -> list[dict]:
    rows = _db().execute("SELECT key, value FROM facts ORDER BY ts DESC").fetchall()
    return [{"key": r["key"], "value": r["value"]} for r in rows]


def forget(key: str) -> bool:
    cur = _db().execute("DELETE FROM facts WHERE key=?", (key,))
    _db().commit()
    return cur.rowcount > 0
