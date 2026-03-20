# app/routes/audit_routes.py - Audit logs (Admin only)
"""Audit log viewer for security and compliance."""
from flask import Blueprint, render_template
from app.routes.auth_routes import login_required, role_required
from app.models.audit_log import get_recent

audit_bp = Blueprint('audit', __name__)


@audit_bp.route('/audit-logs')
@login_required
@role_required('Admin')
def audit_logs():
    logs = get_recent(limit=200)
    return render_template('audit/list.html', logs=logs)
