# app/app.py - Flask application factory
"""
TINDI CMMS - Factory Facility Equipment Maintenance Management System
Coca-Cola Plant Case Study
"""
import os
from flask import Flask
from config import SECRET_KEY, DATABASE

# Ensure instance folder exists
os.makedirs(os.path.dirname(DATABASE), exist_ok=True)


def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config['SECRET_KEY'] = SECRET_KEY

    # Register blueprints
    from app.routes import auth_bp, main_bp, equipment_bp, work_order_bp, inventory_bp, maintenance_bp, reports_bp, api_bp, audit_bp, admin_bp
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
