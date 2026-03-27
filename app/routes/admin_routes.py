# app/routes/admin_routes.py - Admin-only: user management, login activity
"""Admin: manage users, view new/recent logins, full system control."""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.routes.auth_routes import login_required, role_required
from app.models.user import get_all_users, get_by_id, create as create_user
from app.models.login_activity import get_recent_logins
from app.utils.security import hash_password
from app.utils.validators import sanitize_string
from app.models.audit_log import log as audit_log

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/admin')
@login_required
@role_required('Admin')
def dashboard():
    """Admin dashboard: recent logins, new staff logins."""
    recent = get_recent_logins(limit=30)
    new_logins = [r for r in recent if r.get('is_first_login')]
    return render_template('admin/dashboard.html', recent_logins=recent, new_logins=new_logins)


@admin_bp.route('/admin/logins')
@login_required
@role_required('Admin')
def login_activity():
    """Full login activity list."""
    logins = get_recent_logins(limit=100)
    return render_template('admin/logins.html', logins=logins)


@admin_bp.route('/admin/users')
@login_required
@role_required('Admin')
def users():
    """User management - list all staff."""
    users_list = get_all_users()
    return render_template('admin/users.html', users=users_list)


@admin_bp.route('/admin/users/add', methods=['GET', 'POST'])
@login_required
@role_required('Admin')
def add_user():
    """Add new staff - Admin creates users with default credentials."""
    if request.method == 'POST':
        name = sanitize_string(request.form.get('name', ''), 100)
        email = sanitize_string(request.form.get('email', ''), 100)
        password = request.form.get('password', '')
        role = request.form.get('role', 'Technician')
        if role not in ['Admin', 'Maintenance Manager', 'Technician', 'Store Manager']:
            role = 'Technician'
        if not name or not email or not password:
            flash('Name, email and password are required.', 'danger')
            return redirect(url_for('admin.add_user'))
        from app.models.user import get_by_email
        if get_by_email(email):
            flash('Email already exists. Staff credentials must be unique.', 'danger')
            return redirect(url_for('admin.add_user'))
        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return redirect(url_for('admin.add_user'))
        pw_hash = hash_password(password)
        create_user(name, email, pw_hash, role, password)
        audit_log(session['user_id'], 'CREATE', 'user', None, new_value=f'{name} ({email})')
        flash(f'Staff {name} added. They can sign in with the credentials you provided.', 'success')
        return redirect(url_for('admin.users'))
    return render_template('admin/user_form.html', user=None)


@admin_bp.route('/admin/users/<int:uid>/edit', methods=['GET', 'POST'])
@login_required
@role_required('Admin')
def edit_user(uid):
    """Edit staff - change role, reset password."""
    from app.models.user import get_by_id
    from database.db import execute_query
    user = get_by_id(uid)
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('admin.users'))
    if request.method == 'POST':
        name = sanitize_string(request.form.get('name', ''), 100)
        role = request.form.get('role', user['role'])
        if role not in ['Admin', 'Maintenance Manager', 'Technician', 'Store Manager']:
            role = user['role']
        new_password = request.form.get('password', '')
        execute_query(
            "UPDATE users SET name=?, role=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
            (name, role, uid)
        )
        if new_password and len(new_password) >= 6:
            pw_hash = hash_password(new_password)
            execute_query("UPDATE users SET password_hash=? WHERE id=?", (pw_hash, uid))
            flash('User updated. Password reset.', 'success')
        else:
            flash('User updated.', 'success')
        audit_log(session['user_id'], 'UPDATE', 'user', uid, new_value=name)
        return redirect(url_for('admin.users'))
    return render_template('admin/user_form.html', user=user)


@admin_bp.route('/admin/users/<int:uid>/deactivate', methods=['POST'])
@login_required
@role_required('Admin')
def deactivate_user(uid):
    """Deactivate staff (Admin cannot deactivate self)."""
    if uid == session.get('user_id'):
        flash('You cannot deactivate yourself.', 'danger')
        return redirect(url_for('admin.users'))
    user = get_by_id(uid)
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('admin.users'))
    from database.db import execute_query
    execute_query("UPDATE users SET is_active=0 WHERE id=?", (uid,))
    audit_log(session['user_id'], 'DEACTIVATE', 'user', uid, old_value=user['name'])
    flash(f'{user["name"]} has been deactivated.', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/admin/users/<int:uid>/activate', methods=['POST'])
@login_required
@role_required('Admin')
def activate_user(uid):
    """Reactivate staff."""
    from database.db import execute_query
    execute_query("UPDATE users SET is_active=1 WHERE id=?", (uid,))
    audit_log(session['user_id'], 'ACTIVATE', 'user', uid)
    flash('User reactivated.', 'success')
    return redirect(url_for('admin.users'))
