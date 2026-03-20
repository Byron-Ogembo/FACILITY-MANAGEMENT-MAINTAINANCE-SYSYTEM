# app/routes/auth_routes.py - Authentication routes
"""Staff sign-in: company-provided credentials. Admin adds users."""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from functools import wraps
from app.models.user import get_by_email, get_by_id
from app.utils.security import verify_password, validate_email
from app.utils.validators import sanitize_string
from app.models.audit_log import log as audit_log
from app.models.login_activity import record_login, has_ever_logged_in, mark_user_logged_in

auth_bp = Blueprint('auth', __name__)


def login_required(f):
    """Decorator to require login."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


def role_required(*allowed_roles):
    """Decorator to require specific role(s)."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in.', 'warning')
                return redirect(url_for('auth.login'))
            user = get_by_id(session['user_id'])
            if not user or user['role'] not in allowed_roles:
                flash('Access denied. Insufficient permissions.', 'danger')
                return redirect(url_for('main.dashboard'))
            return f(*args, **kwargs)
        return decorated
    return decorator


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        role = request.form.get('role', '').strip()
        email = sanitize_string(request.form.get('email', ''), 100)
        password = request.form.get('password', '')
        valid_roles = ['Admin', 'Maintenance Manager', 'Technician', 'Store Manager']
        if not role or role not in valid_roles:
            flash('Please select your role.', 'danger')
            return render_template('auth/login.html')
        if not email or not password:
            flash('Email and password are required.', 'danger')
            return render_template('auth/login.html')
        if not validate_email(email):
            flash('Invalid email format.', 'danger')
            return render_template('auth/login.html')
        user = get_by_email(email)
        if not user or not verify_password(user['password_hash'], password):
            flash('Invalid email or password. Use the credentials provided by the company.', 'danger')
            return render_template('auth/login.html')
        if user['role'] != role:
            flash(f'Role does not match. Your account is registered as {user["role"]}.', 'danger')
            return render_template('auth/login.html')
        is_first = not has_ever_logged_in(user['id'])
        record_login(user['id'], request.remote_addr, is_first=is_first)
        mark_user_logged_in(user['id'])
        session['user_id'] = user['id']
        session['user_name'] = user['name']
        session['user_role'] = user['role']
        session.permanent = True
        audit_log(user['id'], 'LOGIN', 'user', user['id'], ip_address=request.remote_addr)
        if is_first:
            flash(f'Welcome, {user["name"]}! This is your first login.', 'success')
        else:
            flash(f'Welcome back, {user["name"]}!', 'success')
        return redirect(url_for('main.dashboard'))
    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    if 'user_id' in session:
        audit_log(session.get('user_id'), 'LOGOUT', ip_address=request.remote_addr)
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
