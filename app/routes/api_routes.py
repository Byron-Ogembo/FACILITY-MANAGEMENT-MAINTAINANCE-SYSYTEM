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


@api_bp.route('/test/notification', methods=['POST'])
def test_notification():
    from flask import request, jsonify
    from app.services.notification_service import emit_realtime_notification
    payload = request.get_json() or {}
    message = payload.get('message', 'Test real-time notification')
    n_type = payload.get('type', 'info')
    broadcast = payload.get('broadcast', False)
    role = payload.get('role')
    user_id = payload.get('user_id')
    
    emit_realtime_notification(user_id=user_id, role=role, message=message, title="System Alert", n_type=n_type, broadcast=broadcast)
    return jsonify({"success": True, "message": "Notification triggered successfully!"})


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


@api_bp.route('/notifications/<int:nid>/read', methods=['POST', 'PUT'])
@login_required
def notification_read(nid):
    mark_read(nid)
    return jsonify({'success': True})


@api_bp.route('/notifications/read-all', methods=['POST'])
@login_required
def notification_read_all():
    mark_all_read(session['user_id'])
    return jsonify({'success': True})


@api_bp.route('/notifications/send', methods=['POST'])
def send_notification():
    from flask import request
    from app.models.notification import create
    from app.services.notification_service import emit_realtime_notification, send_assignment_email
    
    payload = request.get_json() or {}
    technician_id = payload.get('technician_id')
    task_id = payload.get('task_id')
    message = payload.get('message')
    channel = payload.get('channel', 'in-app')
    
    if not technician_id or not task_id or not message:
        return jsonify({"success": False, "error": "Missing required fields"}), 400
        
    status = 'pending'
    
    # Simple mockup handling of SMS/Email channels for status simulation
    if channel == 'email':
        ticket_info = execute_query("SELECT title, priority FROM work_orders WHERE id=?", (task_id,), fetch_one=True) or {}
        tech_info = execute_query("SELECT email FROM users WHERE id=?", (technician_id,), fetch_one=True)
        if tech_info and ticket_info:
            # Hardcoded test receiver as requested
            test_receiver = "byronogembo337@gmail.com" 
            sent = send_assignment_email(test_receiver, ticket_info)
            status = 'sent' if sent else 'failed'
    elif channel == 'sms':
        status = 'failed' # SMS gateway not hooked up, default to failed for now
    else:
        status = 'sent'
        
    notif_id = create(
        user_id=technician_id,
        title="Task Update",
        message=message,
        type="info",
        task_id=task_id, 
        channel=channel, 
        status=status
    )
    
    return jsonify({"success": True, "notification_id": notif_id, "status": status})


@api_bp.route('/notifications/<int:technician_id>', methods=['GET'])
@login_required
def get_technician_notifications(technician_id):
    from app.models.notification import get_all_for_user
    notifs = get_all_for_user(technician_id)
    return jsonify([{
        'id': n['id'], 'title': n['title'], 'message': n['message'], 
        'type': n['type'], 'task_id': n['task_id'], 'channel': n['channel'], 
        'status': n['status'], 'is_read': n['is_read'], 'created_at': n['created_at']
    } for n in notifs])


@api_bp.route('/notifications/<int:technician_id>/unread', methods=['GET'])
@login_required
def get_technician_unread(technician_id):
    from app.models.notification import get_unread
    notifs = get_unread(technician_id)
    return jsonify([{
        'id': n['id'], 'title': n['title'], 'message': n['message'], 
        'type': n['type'], 'task_id': n['task_id'], 'channel': n['channel'], 
        'status': n['status'], 'is_read': n['is_read'], 'created_at': n['created_at']
    } for n in notifs])


@api_bp.route('/notifications/<int:notification_id>', methods=['DELETE'])
@login_required
def delete_notification(notification_id):
    from app.models.notification import delete
    delete(notification_id)
    return jsonify({"success": True})
