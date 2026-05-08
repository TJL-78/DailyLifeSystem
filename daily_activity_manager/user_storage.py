"""User storage backends."""

import json
import os
from typing import Optional, List
from .user_model import User


class JSONUserStorage:
    """JSON file-based user storage."""

    def __init__(self, filepath: str = "users.json"):
        self.filepath = filepath
        if not os.path.exists(self.filepath):
            self._write_all([])

    def _read_all(self) -> List[dict]:
        with open(self.filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write_all(self, data: List[dict]):
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def save(self, user: User):
        users = self._read_all()
        for i, u in enumerate(users):
            if u["id"] == user.id:
                users[i] = {**user.to_dict(), "password_hash": user.password_hash}
                self._write_all(users)
                return
        users.append({**user.to_dict(), "password_hash": user.password_hash})
        self._write_all(users)

    def get_by_username(self, username: str) -> Optional[User]:
        for u in self._read_all():
            if u["username"] == username:
                return User.from_dict(u)
        return None

    def get_by_id(self, user_id: str) -> Optional[User]:
        for u in self._read_all():
            if u["id"] == user_id:
                return User.from_dict(u)
        return None

    def username_exists(self, username: str) -> bool:
        return self.get_by_username(username) is not None

    def get_by_phone(self, phone: str) -> Optional[User]:
        for u in self._read_all():
            if u.get("phone") and u["phone"] == phone:
                return User.from_dict(u)
        return None


class MySQLUserStorage:
    """MySQL-based user storage."""

    def __init__(self, get_connection):
        self._get_connection = get_connection
        self._init_table()

    def _init_table(self):
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id VARCHAR(36) PRIMARY KEY,
                        username VARCHAR(100) NOT NULL UNIQUE,
                        password_hash VARCHAR(255) NOT NULL,
                        email VARCHAR(255),
                        display_name VARCHAR(255),
                        avatar_url VARCHAR(500),
                        phone VARCHAR(50),
                        created_at DATETIME NOT NULL
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """)
            conn.commit()
        finally:
            conn.close()

    def save(self, user: User):
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO users (id, username, password_hash, email, display_name, avatar_url, phone, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        password_hash=VALUES(password_hash), email=VALUES(email),
                        display_name=VALUES(display_name), avatar_url=VALUES(avatar_url),
                        phone=VALUES(phone)
                    """,
                    (user.id, user.username, user.password_hash, user.email, user.display_name, user.avatar_url, user.phone, user.created_at),
                )
            conn.commit()
        finally:
            conn.close()

    def get_by_username(self, username: str) -> Optional[User]:
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
                row = cursor.fetchone()
                if row:
                    return User.from_dict(row)
                return None
        finally:
            conn.close()

    def get_by_id(self, user_id: str) -> Optional[User]:
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
                row = cursor.fetchone()
                if row:
                    return User.from_dict(row)
                return None
        finally:
            conn.close()

    def username_exists(self, username: str) -> bool:
        return self.get_by_username(username) is not None

    def get_by_phone(self, phone: str) -> Optional[User]:
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE phone = %s", (phone,))
                row = cursor.fetchone()
                if row:
                    return User.from_dict(row)
                return None
        finally:
            conn.close()
