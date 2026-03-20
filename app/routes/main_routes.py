# app/routes/main_routes.py - Main pages and dashboard
"""Dashboard - role-specific views."""
from flask import Blueprint, render_template, session, redirect, url_for
from app.routes.auth_routes import login_required
from database.db import execute_query
from app.models.notification import get_unread
from app.models.inventory import get_low_stock
from app.models.maintenance_schedule import get_due_soon
from app.models.work_order import get_all as get_work_orders

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Landing page - redirect to login if not authenticated, else dashboard."""
    from flask import session, redirect, url_for
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard - role-specific: Admin full, Technician my tasks, Store Manager inventory, Maintenance Manager maintenance."""
    role = session.get('user_role', 'Technician')
    notifications = get_unread(session['user_id']) if session.get('user_id') else []

    # Admin: redirect to admin dashboard for full control
    if role == 'Admin':
        return redirect(url_for('admin.dashboard'))

    # Common data by role
    total_equipment = execute_query("SELECT COUNT(*) as c FROM equipment", fetch_one=True)['c']
    active_wo = execute_query("SELECT COUNT(*) as c FROM work_orders WHERE status IN ('pending','in_progress')", fetch_one=True)['c']
    completed_wo = execute_query("SELECT COUNT(*) as c FROM work_orders WHERE status='completed'", fetch_one=True)['c']
    faulty_equipment = execute_query("SELECT COUNT(*) as c FROM equipment WHERE status IN ('faulty','under_maintenance')", fetch_one=True)['c']
    eq_by_status = execute_query("SELECT status, COUNT(*) as count FROM equipment GROUP BY status", fetch_all=True)
    wo_by_status = execute_query("SELECT status, COUNT(*) as count FROM work_orders GROUP BY status", fetch_all=True)
    low_stock = get_low_stock()
    due_maintenance = get_due_soon(7)

    # Technician: my work orders only
    my_work_orders = []
    if role == 'Technician':
        my_work_orders = get_work_orders(assigned_to_user_id=session['user_id'])
        my_work_orders = [w for w in my_work_orders if w.get('status') in ('pending', 'in_progress')][:10]

    total_parts = execute_query("SELECT COUNT(*) as c FROM inventory", fetch_one=True)['c'] if role == 'Store Manager' else 0

    return render_template('dashboard.html',
        role=role,
        total_equipment=total_equipment,
        active_work_orders=active_wo,
        completed_work_orders=completed_wo,
        faulty_equipment=faulty_equipment,
        eq_by_status=eq_by_status,
        wo_by_status=wo_by_status,
        notifications=notifications,
        low_stock=low_stock,
        due_maintenance=due_maintenance,
        my_work_orders=my_work_orders,
        total_parts=total_parts
    )
