#!/usr/bin/env python3
"""
TINDI CMMS - Factory Facility Equipment Maintenance Management System
Coca-Cola Plant Case Study

Run: python run.py
"""
import os
import sys

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Initialize database before starting app
from database.db import init_db

if __name__ == '__main__':
    print("Initializing database...")
    init_db()
    print("Starting TINDI CMMS server...")
    from app.app import create_app, socketio
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=True, allow_unsafe_werkzeug=True)
