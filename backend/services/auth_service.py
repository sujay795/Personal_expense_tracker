"""
Authentication Service for Personal Expense Tracker
Handles user registration, login, password hashing, and session management.
"""
import re
from datetime import datetime
from typing import Optional, Tuple
from werkzeug.security import generate_password_hash, check_password_hash

from backend.database.connection import get_db
from shared.constants.app_constants import (
    ErrorMessages, AuthConfig, FormFieldNames
)


class AuthService:
    """Authentication service for user management."""

    EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

    def __init__(self):
        self.db = get_db()

    def validate_registration(self, name: str, email: str, password: str, confirm_password: str) -> Tuple[bool, list]:
        """Validate registration input."""
        errors = []

        if not name or not name.strip():
            errors.append({FormFieldNames.NAME: ErrorMessages.REQUIRED_FIELD})

        if not email or not email.strip():
            errors.append({FormFieldNames.EMAIL: ErrorMessages.REQUIRED_FIELD})
        elif not self.EMAIL_REGEX.match(email):
            errors.append({FormFieldNames.EMAIL: ErrorMessages.INVALID_EMAIL})

        if not password:
            errors.append({FormFieldNames.PASSWORD: ErrorMessages.REQUIRED_FIELD})
        elif len(password) < 6:
            errors.append({FormFieldNames.PASSWORD: ErrorMessages.PASSWORD_TOO_SHORT})

        if not confirm_password:
            errors.append({FormFieldNames.CONFIRM_PASSWORD: ErrorMessages.REQUIRED_FIELD})
        elif password != confirm_password:
            errors.append({FormFieldNames.CONFIRM_PASSWORD: ErrorMessages.PASSWORD_MISMATCH})

        return len(errors) == 0, errors

    def validate_login(self, email: str, password: str) -> Tuple[bool, list]:
        """Validate login input."""
        errors = []

        if not email or not email.strip():
            errors.append({FormFieldNames.EMAIL: ErrorMessages.REQUIRED_FIELD})

        if not password:
            errors.append({FormFieldNames.PASSWORD: ErrorMessages.REQUIRED_FIELD})

        return len(errors) == 0, errors

    def register_user(self, name: str, email: str, password: str) -> Tuple[bool, Optional[int], list]:
        """Register a new user. Returns (success, user_id, errors)."""
        # Validate input
        is_valid, errors = self.validate_registration(name, email, password, password)
        if not is_valid:
            return False, None, errors

        # Check if email exists
        with self.db.get_db() as conn:
            existing = conn.execute(
                "SELECT user_id FROM users WHERE email = ?", (email.lower(),)
            ).fetchone()

            if existing:
                return False, None, [{FormFieldNames.EMAIL: ErrorMessages.EMAIL_EXISTS}]

            # Hash password and create user
            password_hash = generate_password_hash(password)
            cursor = conn.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                (name.strip(), email.lower().strip(), password_hash)
            )
            user_id = cursor.lastrowid

        return True, user_id, []

    def login_user(self, email: str, password: str) -> Tuple[bool, Optional[dict], list]:
        """Authenticate user login. Returns (success, user_dict, errors)."""
        is_valid, errors = self.validate_login(email, password)
        if not is_valid:
            return False, None, errors

        with self.db.get_db() as conn:
            user = conn.execute(
                "SELECT user_id, name, email, password_hash FROM users WHERE email = ?",
                (email.lower().strip(),)
            ).fetchone()

            if not user or not check_password_hash(user['password_hash'], password):
                return False, None, [{'general': ErrorMessages.INVALID_CREDENTIALS}]

            # Update last login (optional)
            conn.execute(
                "UPDATE users SET created_at = created_at WHERE user_id = ?",
                (user['user_id'],)
            )

            user_dict = {
                'user_id': user['user_id'],
                'name': user['name'],
                'email': user['email'],
            }

        return True, user_dict, []

    def get_user_by_id(self, user_id: int) -> Optional[dict]:
        """Get user by ID."""
        with self.db.get_db() as conn:
            user = conn.execute(
                "SELECT user_id, name, email, created_at FROM users WHERE user_id = ?",
                (user_id,)
            ).fetchone()

            if user:
                return dict(user)
        return None

    def hash_password(self, password: str) -> str:
        """Hash a password."""
        return generate_password_hash(password)

    def verify_password(self, password_hash: str, password: str) -> bool:
        """Verify a password against hash."""
        return check_password_hash(password_hash, password)


# Global auth service instance
auth_service = AuthService()