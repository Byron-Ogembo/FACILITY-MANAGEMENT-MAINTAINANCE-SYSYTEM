# config.py - Application configuration for TINDI CMMS
"""
Central configuration for the CMMS application.
Uses environment variables where applicable for deployment flexibility.
"""
import os

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load env variables
from dotenv import load_dotenv
load_dotenv(os.path.join(BASE_DIR, '.env'))

# SQLite database — platform-aware path
# Vercel:        /tmp (ephemeral)
# Render free:   /tmp (ephemeral — data resets on cold start, auto-reseeded)
# Render paid:   persistent disk mounted at RENDER_DISK_PATH (/data)
# Local:         instance/cmms.db
if os.environ.get('VERCEL') or (os.environ.get('RENDER') and not os.environ.get('RENDER_DISK_PATH')):
    DATABASE = '/tmp/cmms.db'
elif os.environ.get('RENDER_DISK_PATH'):
    _disk = os.environ['RENDER_DISK_PATH']
    os.makedirs(_disk, exist_ok=True)
    DATABASE = os.path.join(_disk, 'cmms.db')
else:
    DATABASE = os.path.join(BASE_DIR, 'instance', 'cmms.db')
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
