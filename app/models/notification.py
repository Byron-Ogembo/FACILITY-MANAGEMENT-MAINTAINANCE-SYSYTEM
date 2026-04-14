# app/models/notification.py - User notifications
"""Notifications for pending maintenance, low stock, etc."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from database.db import execute_query


def create(user_id, title, message, type='info'):
    """Create notification."""
    notif_id = execute_query(
        "INSERT INTO notifications (user_id, title, message, type) VALUES (?, ?, ?, ?)",
        (user_id, title, message, type)
    )
    try:
        from app.app import socketio
        socketio.emit('new_notification', {
            'title': title, 
            'message': message,
            'type': type
        }, room=str(user_id))
    except Exception as e:
        print(f"SocketIO err: {e}")
    return notif_id


def get_unread(user_id):
    """Get unread notifications for user."""
    return execute_query(
        "SELECT * FROM notifications WHERE user_id = ? AND is_read = 0 ORDER BY created_at DESC",
        (user_id,), fetch_all=True
    )


def get_all_for_user(user_id, limit=50):
    """Get all notifications for user."""
    return execute_query(
        "SELECT * FROM notifications WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
        (user_id, limit), fetch_all=True
    )


def mark_read(notif_id):
    """Mark notification as read."""
    execute_query("UPDATE notifications SET is_read = 1 WHERE id = ?", (notif_id,))


def mark_all_read(user_id):
    """Mark all notifications as read for user."""
    execute_query("UPDATE notifications SET is_read = 1 WHERE user_id = ?", (user_id,))
