# app/routes/maintenance_routes.py - Preventive maintenance scheduling
"""Preventive maintenance schedules, auto work orders, reminders."""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.routes.auth_routes import login_required, role_required
from app.models.maintenance_schedule import get_all, get_due_soon, get_by_id, create, update_next_due, complete_and_reschedule
from app.models.equipment import get_all as get_equipment
from app.models.user import get_technicians
from app.utils.validators import sanitize_string
from app.models.audit_log import log as audit_log
from app.models.work_order import create as create_work_order
from datetime import datetime, timedelta

maintenance_bp = Blueprint('maintenance', __name__)


def _next_due(frequency, from_date=None):
    d = from_date or datetime.now().date()
    if isinstance(d, str):
        d = datetime.strptime(d, '%Y-%m-%d').date()
    if frequency == 'daily':
        return (d + timedelta(days=1)).strftime('%Y-%m-%d')
    if frequency == 'weekly':
        return (d + timedelta(weeks=1)).strftime('%Y-%m-%d')
    if frequency == 'biweekly':
        return (d + timedelta(weeks=2)).strftime('%Y-%m-%d')
    if frequency == 'monthly':
        m, y = d.month + 1, d.year
        if m > 12:
            m, y = 1, y + 1
        return f"{y}-{m:02d}-{min(d.day, 28):02d}"
    if frequency == 'quarterly':
        return (d + timedelta(days=90)).strftime('%Y-%m-%d')
    if frequency == 'annually':
        return f"{d.year + 1}-{d.month:02d}-{d.day:02d}"
    return (d + timedelta(days=30)).strftime('%Y-%m-%d')


@maintenance_bp.route('')
@login_required
@role_required('Admin', 'Maintenance Manager')
def list_schedules():
    schedules = get_all()
    due_soon = get_due_soon(14)
    today_plus_14 = (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')
    return render_template('maintenance/list.html', schedules=schedules, due_soon=due_soon, today_plus_14=today_plus_14)


@maintenance_bp.route('/add', methods=['GET', 'POST'])
@login_required
@role_required('Admin', 'Maintenance Manager')
def add():
    if request.method == 'POST':
        equipment_id = request.form.get('equipment_id')
        if not equipment_id or not str(equipment_id).isdigit():
            flash('Please select equipment.', 'danger')
            return redirect(url_for('maintenance.add'))
        equipment_id = int(equipment_id)
        task_name = sanitize_string(request.form.get('task_name'), 200)
        frequency = request.form.get('frequency', 'monthly')
        next_due = request.form.get('next_due_date')
        assigned_to = request.form.get('assigned_to') or None
        if assigned_to and str(assigned_to).isdigit():
            assigned_to = int(assigned_to)
        else:
            assigned_to = None
        notes = sanitize_string(request.form.get('notes'), 500)
        if not task_name or not next_due:
            flash('Task name and next due date are required.', 'danger')
            return redirect(url_for('maintenance.add'))
        if frequency not in ['daily', 'weekly', 'biweekly', 'monthly', 'quarterly', 'annually']:
            frequency = 'monthly'
        sched_id = create(equipment_id, task_name, frequency, next_due, assigned_to, notes)
        audit_log(session['user_id'], 'CREATE', 'maintenance_schedule', sched_id, new_value=task_name)
        flash('Maintenance schedule created.', 'success')
        return redirect(url_for('maintenance.list_schedules'))
    equipment = get_equipment()
    technicians = get_technicians()
    default_next = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
    return render_template('maintenance/form.html', schedule=None, equipment=equipment, technicians=technicians, default_next=default_next)


@maintenance_bp.route('/<int:sched_id>/complete', methods=['POST'])
@login_required
@role_required('Admin', 'Maintenance Manager')
def complete(sched_id):
    complete_and_reschedule(sched_id, session.get('user_id'))
    flash('Maintenance completed and next due date updated.', 'success')
    return redirect(url_for('maintenance.list_schedules'))


@maintenance_bp.route('/generate-work-orders')
@login_required
@role_required('Admin', 'Maintenance Manager')
def generate_work_orders():
    """Auto-generate work orders for due preventive tasks."""
    due = get_due_soon(0)  # Overdue or due today
    created = 0
    for sched in due:
        wo_id = create_work_order(
            equipment_id=sched['equipment_id'],
            assigned_to=sched.get('assigned_to'),
            title=f"Preventive: {sched['task_name']}",
            description=sched.get('notes', ''),
            priority='medium',
            status='pending',
            created_by=session.get('user_id')
        )
        if wo_id:
            created += 1
    flash(f'Generated {created} work order(s) for due preventive maintenance.', 'success')
    return redirect(url_for('maintenance.list_schedules'))
