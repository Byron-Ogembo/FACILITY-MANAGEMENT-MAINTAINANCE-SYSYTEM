# app/models/user.py - User model and operations
"""User model for authentication and role-based access control."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from database.db import execute_query


def get_by_email(email):
    """Get user by email. Uses parameterized query."""
    return execute_query(
        "SELECT id, name, email, password_hash, role, is_active FROM users WHERE email = ? AND is_active = 1",
        (email,), fetch_one=True
    )


def get_by_id(user_id):
    """Get user by ID."""
    return execute_query(
        "SELECT id, name, email, role, is_active FROM users WHERE id = ?",
        (user_id,), fetch_one=True
    )


def create(name, email, password_hash, role, password):
    """Create new user. Returns new user id."""
    return execute_query(
        "INSERT INTO users (name, email, password_hash, role, password) VALUES (?, ?, ?, ?, ?)",
        (name, email, password_hash, role, password)
    )


def get_all_users():
    """Get all users."""
    return execute_query(
        "SELECT id, name, email, role, is_active, created_at, password FROM users ORDER BY name",
        fetch_all=True
    )


def get_technicians():
    """Get users with Technician or Maintenance Manager role for work order assignment."""
    return execute_query(
        "SELECT id, name, email, role FROM users WHERE role IN ('Technician', 'Maintenance Manager', 'Admin') AND is_active = 1 ORDER BY name",
        fetch_all=True
    )
