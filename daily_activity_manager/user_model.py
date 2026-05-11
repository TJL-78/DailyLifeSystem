"""User model and authentication."""

import uuid
import hashlib
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

try:
    import bcrypt
    _USE_BCRYPT = True
except ImportError:
    _USE_BCRYPT = False


@dataclass
class User:
    """Represents a user account."""
    username: str
    password_hash: str
    email: str = ""
    display_name: str = ""
    avatar_url: str = ""
    phone: str = ""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)

    @staticmethod
    def hash_password(password: str, salt: Optional[str] = None) -> str:
        """Hash a password. Uses bcrypt for new passwords, SHA256 when salt is provided (legacy)."""
        if salt is not None:
            # Legacy SHA256 path — used for verifying old passwords
            hashed = hashlib.sha256((salt + password).encode()).hexdigest()
            return f"{salt}${hashed}"
        if _USE_BCRYPT:
            hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
            return "bcrypt$" + hashed.decode()
        salt = os.urandom(16).hex()
        hashed = hashlib.sha256((salt + password).encode()).hexdigest()
        return f"{salt}${hashed}"

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify a password against its hash."""
        if password_hash.startswith("bcrypt$"):
            if not _USE_BCRYPT:
                return False
            stored = password_hash[7:].encode()
            return bcrypt.checkpw(password.encode(), stored)
        salt, hashed = password_hash.split("$", 1)
        return User.hash_password(password, salt) == password_hash

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "display_name": self.display_name,
            "avatar_url": self.avatar_url,
            "phone": self.phone,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        user = cls(
            username=data["username"],
            password_hash=data["password_hash"],
            email=data.get("email", ""),
            display_name=data.get("display_name", ""),
            avatar_url=data.get("avatar_url", ""),
            phone=data.get("phone", ""),
        )
        user.id = data.get("id", user.id)
        if data.get("created_at"):
            user.created_at = datetime.fromisoformat(data["created_at"])
        return user
