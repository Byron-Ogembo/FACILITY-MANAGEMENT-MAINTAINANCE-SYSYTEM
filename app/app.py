# app/app.py - Flask application factory
"""
TINDI CMMS - Factory Facility Equipment Maintenance Management System
Coca-Cola Plant Case Study
"""
import os
from flask import Flask
from flask_socketio import SocketIO
from config import SECRET_KEY, DATABASE

# Ensure instance folder exists
os.makedirs(os.path.dirname(DATABASE), exist_ok=True)

socketio = SocketIO()

def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config['SECRET_KEY'] = SECRET_KEY

    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')

    # Init extensions
    socketio.init_app(app)
    from app.services.notification_service import mail
    mail.init_app(app)

    @socketio.on('join')
    def on_join(data):
        from flask_socketio import join_room
        room = str(data.get('room'))
        role = str(data.get('role', ''))
        join_room(room)
        if role and role != 'None':
            join_room(role)

    # Register blueprints
    from app.routes import auth_bp, main_bp, equipment_bp, work_order_bp, inventory_bp, maintenance_bp, reports_bp, api_bp, audit_bp, admin_bp
    from app.routes.chatbot import chatbot_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(equipment_bp, url_prefix='/equipment')
    app.register_blueprint(work_order_bp, url_prefix='/work-orders')
    app.register_blueprint(inventory_bp, url_prefix='/inventory')
    app.register_blueprint(maintenance_bp, url_prefix='/maintenance')
    app.register_blueprint(reports_bp, url_prefix='/reports')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(audit_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(chatbot_bp, url_prefix='/chatbot')

    # Context processor for template variables
    @app.context_processor
    def inject_user():
        from flask import session
        from app.models.user import get_by_id
        from app.models.notification import get_unread
        ctx = {}
        if session.get('user_id'):
            ctx['current_user'] = get_by_id(session['user_id'])
            ctx['notifications'] = get_unread(session['user_id'])
        else:
            ctx['current_user'] = None
            ctx['notifications'] = []
        return ctx

    return app
