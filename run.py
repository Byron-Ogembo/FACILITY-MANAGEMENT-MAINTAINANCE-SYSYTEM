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
from app.app import create_app, socketio

print("Initializing database...")
init_db()

app = create_app()

if __name__ == '__main__':
    print("Starting TINDI CMMS server...")
    port = int(os.environ.get('PORT', 5000))
    # We no longer strictly need allow_unsafe_werkzeug since eventlet will be installed,
    # but eventlet will be picked up automatically by socketio.run
    socketio.run(app, host='0.0.0.0', port=port, debug=True)
