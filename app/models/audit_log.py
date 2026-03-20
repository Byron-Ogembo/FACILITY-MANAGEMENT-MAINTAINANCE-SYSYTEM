# app/models/audit_log.py - Audit logging for security and compliance
"""Audit log for tracking user actions."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from database.db import execute_query


def log(user_id, action, entity_type=None, entity_id=None, old_value=None, new_value=None, ip_address=None):
    """Add audit log entry."""
    execute_query(
        """INSERT INTO audit_logs (user_id, action, entity_type, entity_id, old_value, new_value, ip_address)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (user_id, action, entity_type, entity_id, str(old_value)[:1000] if old_value else None,
         str(new_value)[:1000] if new_value else None, ip_address)
    )


def get_recent(limit=100, user_id=None):
    """Get recent audit logs."""
    if user_id:
        return execute_query(
            """SELECT al.*, u.name as user_name FROM audit_logs al
               LEFT JOIN users u ON al.user_id = u.id WHERE al.user_id = ?
               ORDER BY al.created_at DESC LIMIT ?""",
            (user_id, limit), fetch_all=True
        )
    return execute_query(
        """SELECT al.*, u.name as user_name FROM audit_logs al
           LEFT JOIN users u ON al.user_id = u.id
           ORDER BY al.created_at DESC LIMIT ?""",
        (limit,), fetch_all=True
    )
