# app/utils/security.py - Password hashing and security utilities
"""
Password hashing using Werkzeug (bcrypt-compatible).
Never store plain-text passwords.
"""
from werkzeug.security import generate_password_hash, check_password_hash
import re


def hash_password(password):
    """Hash a password using Werkzeug's secure hashing (pbkdf2:sha256)."""
    return generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)


def verify_password(password_hash, password):
    """Verify a password against its hash."""
    return check_password_hash(password_hash, password)


def validate_email(email):
    """Basic email validation."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email)) if email else False


def validate_password_strength(password):
    """Validate password meets minimum requirements."""
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    return True, None
