# app/routes/api_routes.py - JSON API for charts and SPA (if needed)
"""JSON API endpoints for Chart.js data, notifications, etc."""
from flask import Blueprint, jsonify, session
from app.routes.auth_routes import login_required
from database.db import execute_query
from app.models.notification import get_unread, mark_read, mark_all_read

api_bp = Blueprint('api', __name__)


@api_bp.route('/dashboard/stats')
@login_required
def dashboard_stats():
    total_eq = execute_query("SELECT COUNT(*) as c FROM equipment", fetch_one=True)['c']
    pending_wo = execute_query("SELECT COUNT(*) as c FROM work_orders WHERE status IN ('pending','in_progress')", fetch_one=True)['c']
    completed_wo = execute_query("SELECT COUNT(*) as c FROM work_orders WHERE status='completed'", fetch_one=True)['c']
    return jsonify({
        'total_equipment': total_eq,
        'pending_work_orders': pending_wo,
        'completed_work_orders': completed_wo,
        'system_status': 'Operational'
    })


@api_bp.route('/charts/equipment-by-status')
@login_required
def chart_equipment_status():
    rows = execute_query("SELECT status, COUNT(*) as count FROM equipment GROUP BY status", fetch_all=True)
    return jsonify({'labels': [r['status'] for r in rows], 'data': [r['count'] for r in rows]})


@api_bp.route('/charts/work-orders-by-status')
@login_required
def chart_work_orders():
    rows = execute_query("SELECT status, COUNT(*) as count FROM work_orders GROUP BY status", fetch_all=True)
    return jsonify({'labels': [r['status'] for r in rows], 'data': [r['count'] for r in rows]})


@api_bp.route('/notifications')
@login_required
def notifications():
    notifs = get_unread(session['user_id'])
    return jsonify([{'id': n['id'], 'title': n['title'], 'message': n['message'], 'type': n['type'], 'created_at': n['created_at']} for n in notifs])


@api_bp.route('/notifications/<int:nid>/read', methods=['POST'])
@login_required
def notification_read(nid):
    mark_read(nid)
    return jsonify({'success': True})


@api_bp.route('/notifications/read-all', methods=['POST'])
@login_required
def notification_read_all():
    mark_all_read(session['user_id'])
    return jsonify({'success': True})
