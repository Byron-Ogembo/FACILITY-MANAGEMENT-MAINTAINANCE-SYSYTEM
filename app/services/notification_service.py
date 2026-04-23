import datetime
import threading
import os
from flask_mail import Mail, Message

mail = Mail()

def notify_assignment(user_id, ticket_info):
    """
    Unified entry point for assigning a work order.
    1. Records in-app notification.
    2. Sends email asynchronously.
    3. Emits WebSocket alert.
    """
    from app.models.notification import create as create_notification
    from app.models.user import get_by_id as get_user
    
    title = ticket_info.get('title', 'New Assignment')
    priority = ticket_info.get('priority', 'medium')
    wo_id = ticket_info.get('id')
    message_text = f"You have been assigned to: {title} (Priority: {priority})"
    
    # 1. Create In-App Notification (this triggers emit_realtime_notification internally)
    create_notification(
        user_id=user_id,
        title="Task Update",
        message=message_text,
        type="info",
        task_id=wo_id,
        channel='email', 
        status='pending'
    )
    
    # 2. Lookup user email and send in background
    user = get_user(user_id)
    if user and user.get('email'):
        threading.Thread(
            target=send_assignment_email, 
            args=(user['email'], ticket_info)
        ).start()

def send_assignment_email(technician_email, ticket_info):
    """Notify technician that they have a new ticket assigned."""
    if not os.environ.get('MAIL_USERNAME'):
        print("Mail error: MAIL_USERNAME not set in env.")
        return False
        
    msg = Message(
        subject="New Ticket Assignment - TINDI CMMS",
        sender=os.environ.get('MAIL_USERNAME'),
        recipients=[technician_email]
    )
    
    title = ticket_info.get('title', 'Work Order')
    priority = ticket_info.get('priority', 'medium').capitalize()
    description = ticket_info.get('description', 'No description provided.')
    
    msg.html = f"""
    <div style="font-family: sans-serif; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #eee; border-radius: 10px;">
        <h2 style="color: #f85149;">TINDI CMMS - New Assignment</h2>
        <p>Hello,</p>
        <p>You have been assigned to a new work order: <strong>{title}</strong></p>
        <div style="padding: 15px; background: #f9f9f9; border-left: 4px solid #f85149; margin: 15px 0;">
            <p style="margin: 5px 0;"><strong>Priority:</strong> {priority}</p>
            <p style="margin: 5px 0;"><strong>Description:</strong> {description}</p>
        </div>
        <p style="margin-top: 20px;">Please check your dashboard for more details.</p>
        <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
        <p style="font-size: 12px; color: #888;">This is an automated message from the TINDI Facility Management System.</p>
    </div>
    """
    
    try:
        from wsgi import app
        with app.app_context():
            mail.send(msg)
            return True
    except Exception as e:
        print(f"Email Thread Error: {e}")
        return False

def send_status_update_email(client_email, ticket_info):
    """Notify client of ticket status updates."""
    if not os.environ.get('MAIL_USERNAME') or not client_email:
        return False
        
    msg = Message(
        subject=f"Ticket Status Update - {ticket_info.get('title')}",
        sender=os.environ.get('MAIL_USERNAME'),
        recipients=[client_email]
    )
    msg.html = f"""
    <h3>TINDI CMMS Alert</h3>
    <p>The status of your ticket <strong>{ticket_info.get('title')}</strong> is now: <strong>{ticket_info.get('status')}</strong>.</p>
    """
    try:
        from wsgi import app
        with app.app_context():
            mail.send(msg)
            return True
    except Exception as e:
        print("Mail error:", e)
        return False

def emit_realtime_notification(user_id=None, role=None, message="", title="Alert", n_type="info", broadcast=False):
    """
    Broadcasts real-time WebSockets notifications safely.
    """
    try:
        from app.app import socketio
        payload = {
            'title': title,
            'message': message,
            'type': n_type,
            'timestamp': datetime.datetime.now().isoformat()
        }
        if broadcast:
            socketio.emit('new_notification', payload)
        elif role:
            socketio.emit('new_notification', payload, to=role)
        elif user_id:
            socketio.emit('new_notification', payload, to=str(user_id))
    except Exception as e:
        print(f"SocketIO Broadcasting Err: {e}")
