# app/models/work_order.py - Work order model
"""Work order management with priority, status, and assignment."""
import sys
import os
from datetime import date
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from database.db import execute_query


def get_all(assigned_to_user_id=None):
    """Get all work orders. If assigned_to_user_id given, filter to that user (for Technician)."""
    if assigned_to_user_id:
        return execute_query(
            """SELECT w.*, e.name as equipment_name, e.location as equipment_location,
                      u.name as assigned_to_name, u.email as assigned_to_email
               FROM work_orders w
               LEFT JOIN equipment e ON w.equipment_id = e.id
               LEFT JOIN users u ON w.assigned_to = u.id
               WHERE w.assigned_to = ?
               ORDER BY w.date_created DESC""",
            (assigned_to_user_id,), fetch_all=True
        )
    return execute_query(
        """SELECT w.*, e.name as equipment_name, e.location as equipment_location,
                  u.name as assigned_to_name, u.email as assigned_to_email
           FROM work_orders w
           LEFT JOIN equipment e ON w.equipment_id = e.id
           LEFT JOIN users u ON w.assigned_to = u.id
           ORDER BY w.date_created DESC""",
        fetch_all=True
    )


def get_by_id(wo_id):
    """Get work order by ID with related data."""
    return execute_query(
        """SELECT w.*, e.name as equipment_name, e.location as equipment_location,
                  u.name as assigned_to_name, u.email as assigned_to_email
           FROM work_orders w
           LEFT JOIN equipment e ON w.equipment_id = e.id
           LEFT JOIN users u ON w.assigned_to = u.id
           WHERE w.id = ?""",
        (wo_id,), fetch_one=True
    )


def create(equipment_id, assigned_to, title, description, priority='medium', status='pending', created_by=None):
    """Create work order. Returns new id."""
    return execute_query(
        """INSERT INTO work_orders (equipment_id, assigned_to, title, description, priority, status, created_by)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (equipment_id, assigned_to, title, description, priority, status, created_by)
    )


def update_status(wo_id, status, maintenance_notes=None):
    """Update work order status. Sets date_completed when status=completed."""
    extra = ""
    params = [status]
    if status == 'completed':
        extra = ", date_completed = date('now')"
    if maintenance_notes is not None:
        extra += ", maintenance_notes = ?"
        params.append(maintenance_notes)
    params.append(wo_id)
    execute_query(
        f"UPDATE work_orders SET status = ?{extra} WHERE id = ?",
        tuple(params)
    )


def update(wo_id, equipment_id, assigned_to, title, description, priority, status, maintenance_notes=None):
    """Full update of work order."""
    wo = get_by_id(wo_id)
    notes = maintenance_notes if maintenance_notes is not None else (wo.get('maintenance_notes') or '') if wo else ''
    execute_query(
        """UPDATE work_orders SET equipment_id=?, assigned_to=?, title=?, description=?, priority=?, status=?,
           maintenance_notes=?, date_completed=CASE WHEN ? = 'completed' THEN date('now') ELSE date_completed END WHERE id=?""",
        (equipment_id, assigned_to, title, description, priority, status, notes, status, wo_id)
    )


def delete(wo_id):
    """Delete work order."""
    execute_query("DELETE FROM work_orders WHERE id = ?", (wo_id,))


def add_maintenance_record(work_order_id, actions_taken, parts_used, completion_status, hours_spent=0):
    """Add maintenance record to work order."""
    return execute_query(
        """INSERT INTO maintenance_records (work_order_id, actions_taken, parts_used, completion_status, hours_spent)
           VALUES (?, ?, ?, ?, ?)""",
        (work_order_id, actions_taken, parts_used, completion_status, hours_spent)
    )
