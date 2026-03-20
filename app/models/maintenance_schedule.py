# app/models/maintenance_schedule.py - Preventive maintenance scheduling
"""Preventive maintenance schedules and auto work order generation."""
import sys
import os
from datetime import datetime, timedelta
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from database.db import execute_query
from app.models.work_order import create as create_work_order


def get_all():
    """Get all maintenance schedules with equipment names."""
    return execute_query(
        """SELECT ms.*, e.name as equipment_name, e.location, u.name as assigned_to_name
           FROM maintenance_schedule ms
           LEFT JOIN equipment e ON ms.equipment_id = e.id
           LEFT JOIN users u ON ms.assigned_to = u.id
           WHERE ms.is_active = 1 ORDER BY ms.next_due_date""",
        fetch_all=True
    )


def get_due_soon(days=7):
    """Get schedules due within next N days."""
    return execute_query(
        """SELECT ms.*, e.name as equipment_name FROM maintenance_schedule ms
           LEFT JOIN equipment e ON ms.equipment_id = e.id
           WHERE ms.is_active = 1 AND ms.next_due_date <= date('now', '+{} days') AND ms.next_due_date >= date('now')
           ORDER BY ms.next_due_date""".format(days),
        fetch_all=True
    )


def get_by_id(sched_id):
    """Get schedule by ID."""
    return execute_query(
        "SELECT * FROM maintenance_schedule WHERE id = ?",
        (sched_id,), fetch_one=True
    )


def create(equipment_id, task_name, frequency, next_due_date, assigned_to=None, notes=''):
    """Create maintenance schedule. Returns new id."""
    return execute_query(
        """INSERT INTO maintenance_schedule (equipment_id, task_name, frequency, next_due_date, assigned_to, notes)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (equipment_id, task_name, frequency, next_due_date, assigned_to, notes)
    )


def update_next_due(sched_id, next_date):
    """Update next due date after completion."""
    execute_query(
        "UPDATE maintenance_schedule SET next_due_date=?, last_completed_date=date('now') WHERE id=?",
        (next_date, sched_id)
    )


def _next_date_from_frequency(current, frequency):
    """Calculate next due date from frequency."""
    d = datetime.strptime(current, '%Y-%m-%d').date() if isinstance(current, str) else current
    if frequency == 'daily':
        return (d + timedelta(days=1)).strftime('%Y-%m-%d')
    if frequency == 'weekly':
        return (d + timedelta(weeks=1)).strftime('%Y-%m-%d')
    if frequency == 'biweekly':
        return (d + timedelta(weeks=2)).strftime('%Y-%m-%d')
    if frequency == 'monthly':
        # Simple month add
        if d.month == 12:
            return f"{d.year + 1}-01-{d.day:02d}"
        return f"{d.year}-{d.month + 1:02d}-{d.day:02d}"
    if frequency == 'quarterly':
        return (d + timedelta(days=90)).strftime('%Y-%m-%d')
    if frequency == 'annually':
        return f"{d.year + 1}-{d.month:02d}-{d.day:02d}"
    return (d + timedelta(days=30)).strftime('%Y-%m-%d')


def complete_and_reschedule(sched_id, created_by=None):
    """
    Mark schedule as completed, create work order, and reschedule next due.
    Called when preventive maintenance is performed.
    """
    sched = get_by_id(sched_id)
    if not sched:
        return None
    # Create work order for this preventive task
    wo_id = create_work_order(
        equipment_id=sched['equipment_id'],
        assigned_to=sched['assigned_to'],
        title=f"Preventive: {sched['task_name']}",
        description=sched.get('notes', ''),
        priority='medium',
        status='completed',
        created_by=created_by
    )
    # Update work order date_completed
    from database.db import execute_query
    execute_query("UPDATE work_orders SET date_completed=date('now') WHERE id=?", (wo_id,))
    # Reschedule
    next_d = _next_date_from_frequency(sched['next_due_date'], sched['frequency'])
    update_next_due(sched_id, next_d)
    return wo_id
