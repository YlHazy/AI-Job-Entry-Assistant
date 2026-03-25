"""Persist analyzed jobs into a lightweight local SQLite history."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from src.config import HISTORY_DB_PATH
from src.schemas import JobRecord


class HistoryStore:
    """Store analyzed jobs for search, dedupe, and history views."""

    def __init__(self, db_path: Path = HISTORY_DB_PATH) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS job_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER DEFAULT 0,
                    company TEXT,
                    job_title TEXT,
                    role_category TEXT,
                    match_direction TEXT,
                    priority TEXT,
                    source_platform TEXT,
                    source_url TEXT,
                    location TEXT,
                    short_note TEXT,
                    raw_text TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            columns = {row[1] for row in conn.execute("PRAGMA table_info(job_history)").fetchall()}
            if "user_id" not in columns:
                conn.execute("ALTER TABLE job_history ADD COLUMN user_id INTEGER DEFAULT 0")

    def insert(self, record: JobRecord, user_id: int = 0) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO job_history (
                    user_id,
                    company, job_title, role_category, match_direction, priority,
                    source_platform, source_url, location, short_note, raw_text
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    record.company,
                    record.job_title,
                    record.role_category,
                    record.match_direction,
                    record.priority,
                    record.source_platform,
                    record.source_url,
                    record.location,
                    record.short_note or record.notes,
                    record.raw_text,
                ),
            )

    def count(self, user_id: int = 0) -> int:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("SELECT COUNT(*) FROM job_history WHERE user_id = ?", (user_id,)).fetchone()
        return int(row[0] if row else 0)

    def recent(self, limit: int = 20, user_id: int = 0) -> list[dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """
                SELECT id, user_id, company, job_title, role_category, match_direction, priority,
                       source_platform, source_url, location, short_note, created_at
                FROM job_history
                WHERE user_id = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (user_id, limit),
            ).fetchall()
        return [dict(row) for row in rows]

    def search_candidates(self, record: JobRecord, limit: int = 50, user_id: int = 0) -> list[dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """
                SELECT id, user_id, company, job_title, source_url, created_at
                FROM job_history
                WHERE user_id = ?
                  AND (
                       source_url = ?
                    OR company = ?
                    OR job_title = ?
                    OR (company = ? AND job_title = ?)
                  )
                ORDER BY id DESC
                LIMIT ?
                """,
                (user_id, record.source_url, record.company, record.job_title, record.company, record.job_title, limit),
            ).fetchall()
        return [dict(row) for row in rows]

    def search(
        self,
        query: str = "",
        priority: str = "",
        match_direction: str = "",
        limit: int = 50,
        user_id: int = 0,
    ) -> list[dict]:
        clauses = ["user_id = ?"]
        params: list[object] = [user_id]
        if query.strip():
            clauses.append("(company LIKE ? OR job_title LIKE ? OR short_note LIKE ?)")
            like = f"%{query.strip()}%"
            params.extend([like, like, like])
        if priority.strip():
            clauses.append("priority = ?")
            params.append(priority.strip())
        if match_direction.strip():
            clauses.append("match_direction = ?")
            params.append(match_direction.strip())

        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        sql = f"""
            SELECT id, company, job_title, role_category, match_direction, priority,
                   source_platform, source_url, location, short_note, created_at
            FROM job_history
            {where}
            ORDER BY id DESC
            LIMIT ?
        """
        params.append(limit)

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(sql, params).fetchall()
        return [dict(row) for row in rows]

    def get_by_id(self, record_id: int, user_id: int = 0) -> dict | None:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                """
                SELECT id, user_id, company, job_title, role_category, match_direction, priority,
                       source_platform, source_url, location, short_note, raw_text, created_at
                FROM job_history
                WHERE id = ? AND user_id = ?
                """,
                (record_id, user_id),
            ).fetchone()
        return dict(row) if row else None
