# app/models/login_activity.py - Login activity tracking for Admin
"""Track staff logins - new logins, first-time logins for Admin visibility."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from database.db import execute_query


def record_login(user_id, ip_address=None, is_first=False):
    """Record a login event."""
    return execute_query(
        "INSERT INTO login_activity (user_id, ip_address, is_first_login) VALUES (?, ?, ?)",
        (user_id, ip_address, 1 if is_first else 0)
    )


def get_recent_logins(limit=50, first_time_only=False):
    """Get recent logins for Admin dashboard."""
    if first_time_only:
        return execute_query(
            """SELECT la.*, u.name, u.email, u.role FROM login_activity la
               JOIN users u ON la.user_id = u.id
               WHERE la.is_first_login = 1
               ORDER BY la.login_at DESC LIMIT ?""",
            (limit,), fetch_all=True
        )
    return execute_query(
        """SELECT la.*, u.name, u.email, u.role FROM login_activity la
           JOIN users u ON la.user_id = u.id
           ORDER BY la.login_at DESC LIMIT ?""",
        (limit,), fetch_all=True
    )


def has_ever_logged_in(user_id):
    """Check if user has logged in before (for first-time detection)."""
    row = execute_query(
        "SELECT id FROM login_activity WHERE user_id = ? LIMIT 1",
        (user_id,), fetch_one=True
    )
    return row is not None


def mark_user_logged_in(user_id):
    """Update user last_login timestamp."""
    try:
        execute_query(
            "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
            (user_id,)
        )
    except Exception:
        pass  # Column might not exist in older DBs
