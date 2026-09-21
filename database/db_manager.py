"""
db_manager.py
-------------
Owns the single SQLite connection for the whole app and applies schema.sql.

Design notes:
- Every model (Task, Habit, Goal, ...) goes through DatabaseManager rather
  than opening its own sqlite3.connect(). This keeps transactions,
  connection settings (foreign keys, row_factory), and error handling
  in one place.
- `get_db()` returns a process-wide singleton, same pattern as Settings.
"""

from __future__ import annotations

import shutil
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

from config.settings import settings, PROJECT_ROOT
from utils.logger import get_logger

log = get_logger("database.db_manager")

SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"


class DatabaseManager:
    """Thin wrapper around sqlite3 with schema init, queries, and backups."""

    _instance: "DatabaseManager | None" = None

    def __new__(cls) -> "DatabaseManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._connect()
            cls._instance._initialize_schema()
        return cls._instance

    # -- setup -----------------------------------------------------
    def _connect(self) -> None:
        db_path = settings.resolve_path(settings.database.path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON;")
        log.info("Connected to database at %s", db_path)

    def _initialize_schema(self) -> None:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            self._conn.executescript(f.read())
        self._conn.commit()
        log.info("Schema initialized/verified.")

    # -- core query helpers -----------------------------------------
    def execute(self, query: str, params: Iterable[Any] = ()) -> sqlite3.Cursor:
        """Run an INSERT/UPDATE/DELETE and commit. Returns the cursor (for lastrowid)."""
        cur = self._conn.cursor()
        cur.execute(query, params)
        self._conn.commit()
        return cur

    def executemany(self, query: str, seq_of_params: Iterable[Iterable[Any]]) -> None:
        cur = self._conn.cursor()
        cur.executemany(query, seq_of_params)
        self._conn.commit()

    def fetch_one(self, query: str, params: Iterable[Any] = ()) -> sqlite3.Row | None:
        cur = self._conn.cursor()
        cur.execute(query, params)
        return cur.fetchone()

    def fetch_all(self, query: str, params: Iterable[Any] = ()) -> list[sqlite3.Row]:
        cur = self._conn.cursor()
        cur.execute(query, params)
        return cur.fetchall()

    # -- backups (feature 18) ----------------------------------------
    def backup_now(self) -> Path:
        """Copy the live .db file into backups/ with a timestamp suffix."""
        db_path = settings.resolve_path(settings.database.path)
        backup_dir = settings.resolve_path(settings.database.backup_dir)
        backup_dir.mkdir(parents=True, exist_ok=True)

        stamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        dest = backup_dir / f"momentum_{stamp}.db"
        shutil.copy2(db_path, dest)
        log.info("Backup created at %s", dest)
        return dest

    def close(self) -> None:
        self._conn.close()
        log.info("Database connection closed.")


def get_db() -> DatabaseManager:
    """Return the shared DatabaseManager instance (creates it on first call)."""
    return DatabaseManager()
