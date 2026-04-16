import os
from flask_mail import Mail, Message
from flask import current_app

mail = Mail()

def send_assignment_email(technician_email, ticket_info):
    """Notify technician that they have a new ticket assigned."""
    if not os.environ.get('MAIL_USERNAME'):
        return False
        
    msg = Message(
        subject="New Ticket Assignment",
        sender=os.environ.get('MAIL_USERNAME'),
        recipients=[technician_email]
    )
    msg.html = f"""
    <h3>TINDI CMMS - New Assignment</h3>
    <p>You have been assigned to: <strong>{ticket_info.get('title')}</strong></p>
    <p>Priority: <span style="badge" class="badge-priority-{ticket_info.get('priority')}">{ticket_info.get('priority')}</span></p>
    <p>Please check your dashboard for more details.</p>
    """
    try:
        mail.send(msg)
        return True
    except Exception as e:
        print("Mail error:", e)
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
        mail.send(msg)
        return True
    except Exception as e:
        print("Mail error:", e)
        return False

import datetime

def emit_realtime_notification(user_id=None, role=None, message="", title="Alert", n_type="info", broadcast=False):
    """
    Broadcasts real-time WebSockets notifications safely and robustly.
    Can target an explicit user_id, an entire access role, or global broadcast.
    """
    from flask import current_app
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
    except RuntimeError:
        pass # Ignore in scenarios without application context or during test booting
    except Exception as e:
        print(f"SocketIO Broadcasting Err: {e}")
