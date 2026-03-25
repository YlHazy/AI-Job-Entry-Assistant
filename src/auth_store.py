"""SQLite-backed user accounts and token sessions."""

from __future__ import annotations

import hashlib
import hmac
import secrets
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

from src.config import AUTH_DB_PATH, AUTH_SESSION_DAYS


class AuthError(RuntimeError):
    """Base error for authentication and account flows."""


class AuthenticationError(AuthError):
    """Raised when credentials or session tokens are invalid."""


class ConflictError(AuthError):
    """Raised when a unique account constraint is violated."""


class AuthStore:
    """Manage users and bearer-token sessions."""

    def __init__(self, db_path: Path = AUTH_DB_PATH) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    password_salt TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    token TEXT PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
                """
            )

    def register(self, username: str, password: str) -> dict:
        normalized_username = username.strip().lower()
        self._validate_credentials(normalized_username, password)
        salt = secrets.token_hex(16)
        password_hash = _hash_password(password, salt)

        try:
            with self._connect() as conn:
                cursor = conn.execute(
                    """
                    INSERT INTO users (username, password_hash, password_salt)
                    VALUES (?, ?, ?)
                    """,
                    (normalized_username, password_hash, salt),
                )
                user_id = int(cursor.lastrowid)
        except sqlite3.IntegrityError as exc:
            raise ConflictError("该用户名已被注册。") from exc

        return {"id": user_id, "username": normalized_username}

    def authenticate(self, username: str, password: str) -> dict:
        normalized_username = username.strip().lower()
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT id, username, password_hash, password_salt
                FROM users
                WHERE username = ?
                """,
                (normalized_username,),
            ).fetchone()

        if not row:
            raise AuthenticationError("用户名或密码错误。")

        expected_hash = _hash_password(password, row["password_salt"])
        if not hmac.compare_digest(expected_hash, row["password_hash"]):
            raise AuthenticationError("用户名或密码错误。")

        return {"id": int(row["id"]), "username": row["username"]}

    def create_session(self, user_id: int) -> str:
        token = secrets.token_urlsafe(32)
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(days=AUTH_SESSION_DAYS)
        with self._connect() as conn:
            conn.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
            conn.execute(
                """
                INSERT INTO sessions (token, user_id, created_at, expires_at)
                VALUES (?, ?, ?, ?)
                """,
                (token, user_id, now.isoformat(), expires_at.isoformat()),
            )
        return token

    def get_user_by_token(self, token: str) -> dict:
        if not token.strip():
            raise AuthenticationError("缺少登录凭证。")

        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT users.id, users.username, sessions.expires_at
                FROM sessions
                JOIN users ON users.id = sessions.user_id
                WHERE sessions.token = ?
                """,
                (token.strip(),),
            ).fetchone()

        if not row:
            raise AuthenticationError("登录状态已失效，请重新登录。")

        expires_at = datetime.fromisoformat(row["expires_at"])
        if expires_at <= datetime.now(timezone.utc):
            self.revoke_session(token)
            raise AuthenticationError("登录状态已过期，请重新登录。")

        return {"id": int(row["id"]), "username": row["username"]}

    def revoke_session(self, token: str) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM sessions WHERE token = ?", (token.strip(),))

    def count_users(self) -> int:
        with self._connect() as conn:
            row = conn.execute("SELECT COUNT(*) AS count FROM users").fetchone()
        return int(row["count"] if row else 0)

    @staticmethod
    def _validate_credentials(username: str, password: str) -> None:
        if len(username) < 3:
            raise ValueError("用户名至少需要 3 个字符。")
        if len(password) < 6:
            raise ValueError("密码至少需要 6 个字符。")


def _hash_password(password: str, salt: str) -> str:
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120000)
    return digest.hex()
