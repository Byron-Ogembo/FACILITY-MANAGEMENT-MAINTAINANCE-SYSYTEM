# config.py - Application configuration for TINDI CMMS
"""
Central configuration for the CMMS application.
Uses environment variables where applicable for deployment flexibility.
"""
import os

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# SQLite database
DATABASE = os.path.join(BASE_DIR, 'instance', 'cmms.db')
# Ensure instance folder exists
os.makedirs(os.path.join(BASE_DIR, 'instance'), exist_ok=True)

# Flask secret key (change in production!)
SECRET_KEY = os.environ.get('SECRET_KEY', 'tindi-cmms-dev-secret-change-in-production')

# Session
SESSION_TYPE = 'filesystem'
PERMANENT_SESSION_LIFETIME = 3600  # 1 hour

# User roles (for access control)
ROLES = ['Admin', 'Maintenance Manager', 'Technician', 'Store Manager']

# Equipment statuses
EQUIPMENT_STATUSES = ['active', 'faulty', 'under_maintenance', 'inactive']

# Work order priorities
WORK_ORDER_PRIORITIES = ['low', 'medium', 'high', 'critical']

# Work order statuses
WORK_ORDER_STATUSES = ['pending', 'in_progress', 'completed', 'cancelled']

# Maintenance frequency options
MAINTENANCE_FREQUENCIES = ['daily', 'weekly', 'biweekly', 'monthly', 'quarterly', 'annually']
