# app/routes/api_routes.py - JSON API for charts and SPA (if needed)
"""JSON API endpoints for Chart.js data, notifications, etc."""
from flask import Blueprint, jsonify, session
from app.routes.auth_routes import login_required
from database.db import execute_query
from app.models.notification import get_unread, mark_read, mark_all_read, create as create_notification
from app.services.notification_service import notify_assignment

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


@api_bp.route('/users', methods=['GET'])
@login_required
def get_users_api():
    from app.models.user import get_all_users
    return jsonify(get_all_users())


@api_bp.route('/equipment', methods=['GET'])
@login_required
def get_equipment_api():
    from app.models.equipment import get_all
    return jsonify(get_all())


@api_bp.route('/inventory', methods=['GET'])
@login_required
def get_inventory_api():
    from app.models.inventory import get_all
    return jsonify(get_all())


@api_bp.route('/work_orders', methods=['GET'])
@login_required
def get_work_orders_api():
    from app.models.work_order import get_all
    return jsonify(get_all())


@api_bp.route('/work_orders', methods=['POST'])
@login_required
def create_work_order_api():
    from flask import request
    from app.models.work_order import create
    payload = request.get_json() or {}
    wo_id = create(
        payload.get('equipment_id'),
        payload.get('assigned_to'),
        payload.get('title', 'New Work Order'),
        payload.get('description'),
        payload.get('priority', 'medium'),
        'pending',
        session.get('user_id')
    )
    if payload.get('assigned_to'):
        notify_assignment(payload['assigned_to'], {
            'id': wo_id, 
            'title': payload.get('title'), 
            'priority': payload.get('priority'),
            'description': payload.get('description')
        })
    return jsonify({"success": True, "id": wo_id})


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
    notif_id = None
    if channel == 'email':
        ticket_info = execute_query("SELECT id, title, priority, description FROM work_orders WHERE id=?", (task_id,), fetch_one=True) or {}
        notify_assignment(technician_id, ticket_info)
        status = 'sent'
    elif channel == 'sms':
        status = 'failed' 
    else:
        status = 'sent'
        notif_id = create_notification(
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


@api_bp.route('/contacts', methods=['GET'])
@login_required
def get_contacts():
    contacts = execute_query("SELECT * FROM external_contacts", fetch_all=True)
    return jsonify(contacts)


@api_bp.route('/contacts', methods=['POST'])
@login_required
def add_contact():
    from flask import request
    payload = request.get_json() or {}
    name = payload.get('name')
    email = payload.get('email')
    org = payload.get('organization')
    
    if not name or not email:
        return jsonify({"success": False, "error": "Name and email required"}), 400
        
    try:
        new_id = execute_query(
            "INSERT INTO external_contacts (name, email, organization) VALUES (?, ?, ?)",
            (name, email, org)
        )
        return jsonify({"success": True, "id": new_id})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route('/contacts/<int:cid>', methods=['DELETE'])
@login_required
def delete_contact(cid):
    execute_query("DELETE FROM external_contacts WHERE id=?", (cid,))
    return jsonify({"success": True})


@api_bp.route('/test/email', methods=['POST'])
@login_required
def test_email():
    """Send a test email to verify mail configuration on Render."""
    import os
    from flask import request, current_app
    from flask_mail import Message
    from app.services.notification_service import mail

    payload = request.get_json() or {}
    to_addr = payload.get('to', os.environ.get('MAIL_USERNAME', 'byronogembo337@gmail.com'))

    if not os.environ.get('MAIL_USERNAME'):
        return jsonify({"success": False, "error": "MAIL_USERNAME not configured on server"}), 500

    msg = Message(
        subject="✅ TINDI CMMS – Email Test",
        sender=os.environ.get('MAIL_USERNAME'),
        recipients=[to_addr]
    )
    msg.html = """
    <div style="font-family:sans-serif;max-width:600px;margin:auto;padding:24px;
                border:1px solid #eee;border-radius:10px;">
        <h2 style="color:#e63946;">TINDI CMMS – Email Delivery Test</h2>
        <p>
            This is a <strong>test email</strong> confirming that the mail system
            on Render is working correctly.
        </p>
        <p style="color:#555;font-size:13px;">Sent from: TINDI CMMS | Coca-Cola Plant</p>
    </div>
    """
    try:
        with current_app.app_context():
            mail.send(msg)
        return jsonify({"success": True, "message": f"Test email sent to {to_addr}"})
    except Exception as e:
        print(f"Test email failed: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
