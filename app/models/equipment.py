# app/models/equipment.py - Equipment (asset) model
"""Equipment management model with history logging."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from database.db import execute_query


def get_all():
    """Get all equipment with optional status filter."""
    return execute_query(
        "SELECT * FROM equipment ORDER BY name",
        fetch_all=True
    )


def get_by_id(eq_id):
    """Get equipment by ID."""
    return execute_query("SELECT * FROM equipment WHERE id = ?", (eq_id,), fetch_one=True)


def create(name, category, location='', status='active', serial_number='', notes='', qr_code=None):
    """Create new equipment. Returns new id."""
    return execute_query(
        """INSERT INTO equipment (name, category, location, status, serial_number, notes, qr_code)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (name, category, location, status, serial_number, notes, qr_code)
    )


def update(eq_id, name, category, location, status, serial_number='', notes=''):
    """Update equipment."""
    execute_query(
        """UPDATE equipment SET name=?, category=?, location=?, status=?, serial_number=?, notes=?, updated_at=CURRENT_TIMESTAMP
           WHERE id=?""",
        (name, category, location, status, serial_number, notes, eq_id)
    )


def delete(eq_id):
    """Delete equipment by ID."""
    execute_query("DELETE FROM equipment WHERE id = ?", (eq_id,))


def add_history(equipment_id, action, description='', performed_by=None):
    """Log equipment history entry."""
    execute_query(
        "INSERT INTO equipment_history (equipment_id, action, description, performed_by) VALUES (?, ?, ?, ?)",
        (equipment_id, action, description, performed_by)
    )


def get_history(equipment_id, limit=50):
    """Get equipment history log."""
    return execute_query(
        """SELECT eh.*, u.name as performed_by_name FROM equipment_history eh
           LEFT JOIN users u ON eh.performed_by = u.id
           WHERE eh.equipment_id = ? ORDER BY eh.created_at DESC LIMIT ?""",
        (equipment_id, limit), fetch_all=True
    )
