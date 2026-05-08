"""User model and authentication."""

import uuid
import hashlib
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class User:
    """Represents a user account."""
    username: str
    password_hash: str
    email: str = ""
    display_name: str = ""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)

    @staticmethod
    def hash_password(password: str, salt: Optional[str] = None) -> str:
        """Hash a password with salt."""
        if salt is None:
            salt = os.urandom(16).hex()
        hashed = hashlib.sha256((salt + password).encode()).hexdigest()
        return f"{salt}${hashed}"

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify a password against its hash."""
        salt, hashed = password_hash.split("$", 1)
        return User.hash_password(password, salt) == password_hash

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "display_name": self.display_name,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        user = cls(
            username=data["username"],
            password_hash=data["password_hash"],
            email=data.get("email", ""),
            display_name=data.get("display_name", ""),
        )
        user.id = data.get("id", user.id)
        if data.get("created_at"):
            user.created_at = datetime.fromisoformat(data["created_at"])
        return user
