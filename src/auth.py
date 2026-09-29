import hashlib
import os
import sqlite3
import logging
from typing import Optional
from src.database import DatabaseManager
from src.models import User
from src.exceptions import UserAuthenticationError

logger = logging.getLogger("AuthService")


class AuthService:
    """Handles secure user registration, password verification, and authentication."""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    @staticmethod
    def _hash_password(password: str, salt: Optional[bytes] = None) -> str:
        """Hashes password using PBKDF2 with SHA256 and salt."""
        if not salt:
            salt = os.urandom(16)
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return f"{salt.hex()}:{key.hex()}"

    @staticmethod
    def _verify_password(password: str, stored_hash: str) -> bool:
        """Verifies password against stored salt:hash combination."""
        try:
            salt_hex, key_hex = stored_hash.split(":")
            salt = bytes.fromhex(salt_hex)
            expected_key = bytes.fromhex(key_hex)
            new_key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
            return new_key == expected_key
        except Exception:
            return False

    def register_user(self, username: str, email: str, password: str, role: str = "student") -> User:
        """Registers a new user account."""
        if len(password) < 6:
            raise UserAuthenticationError("Password must be at least 6 characters long.")

        pwd_hash = self._hash_password(password)
        query = "INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)"

        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (username.strip(), email.strip().lower(), pwd_hash, role))
                user_id = cursor.lastrowid
                conn.commit()
                logger.info(f"User '{username}' registered successfully with ID {user_id}.")
                return User(user_id=user_id, username=username, email=email, role=role)
        except sqlite3.IntegrityError:
            logger.warning(f"Registration failed: Username or email already exists.")
            raise UserAuthenticationError("Username or email is already registered.")

    def authenticate_user(self, username_or_email: str, password: str) -> User:
        """Authenticates user and returns User instance upon success."""
        query = "SELECT user_id, username, email, password_hash, role FROM users WHERE username = ? OR email = ?"
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (username_or_email.strip(), username_or_email.strip().lower()))
            row = cursor.fetchone()

            if not row:
                raise UserAuthenticationError("Invalid username or password.")

            user_id, username, email, stored_hash, role = row
            if not self._verify_password(password, stored_hash):
                raise UserAuthenticationError("Invalid username or password.")

            logger.info(f"User '{username}' authenticated successfully.")
            return User(user_id=user_id, username=username, email=email, role=role)
