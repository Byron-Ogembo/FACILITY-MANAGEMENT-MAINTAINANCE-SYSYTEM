#!/usr/bin/env python3
"""
Seed sample data for TINDI CMMS testing.
Run after init_db: python seed_data.py
"""
import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db import execute_query
from app.utils.security import hash_password


def seed():
    # Check if already seeded
    if execute_query("SELECT COUNT(*) as c FROM users", fetch_one=True)['c'] > 1:
        print("Data already seeded. Skipping.")
        return

    # Users (password: admin123 for admin, tech123 for technicians)
    admin_hash = hash_password('admin123')
    tech_hash = hash_password('tech123')
    execute_query(
        "INSERT OR IGNORE INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
        ('Admin', 'admin@cmms.com', admin_hash, 'Admin')
    )
    execute_query(
        "INSERT OR IGNORE INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
        ('John Technician', 'john@cmms.com', tech_hash, 'Technician')
    )
    execute_query(
        "INSERT OR IGNORE INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
        ('Maria Manager', 'maria@cmms.com', hash_password('manager123'), 'Maintenance Manager')
    )
    execute_query(
        "INSERT OR IGNORE INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
        ('Steve Store', 'steve@cmms.com', hash_password('store123'), 'Store Manager')
    )

    # Equipment (Coca-Cola plant themed)
    equipment = [
        ('Bottling Line 1', 'Bottling Machine', 'Production Hall A', 'active', 'BL-001'),
        ('Bottling Line 2', 'Bottling Machine', 'Production Hall A', 'active', 'BL-002'),
        ('Conveyor A', 'Conveyor', 'Production Hall A', 'active', 'CV-A'),
        ('Conveyor B', 'Conveyor', 'Production Hall B', 'under_maintenance', 'CV-B'),
        ('Filler Unit 1', 'Filler', 'Production Hall A', 'active', 'FU-001'),
        ('Labeler Machine', 'Labeler', 'Packaging Area', 'active', 'LM-001'),
        ('Palletizer', 'Packaging', 'Warehouse', 'active', 'PL-001'),
        ('Compressor Unit', 'Utilities', 'Utility Room', 'faulty', 'CU-001'),
    ]
    for name, cat, loc, status, sn in equipment:
        execute_query(
            "INSERT INTO equipment (name, category, location, status, serial_number) VALUES (?, ?, ?, ?, ?)",
            (name, cat, loc, status, sn)
        )

    # Inventory
    parts = [
        ('Drive Belt Type A', 'DB-A100', 25, 10, 'Units'),
        ('O-Ring Kit', 'OR-KIT', 5, 5, 'Kits'),
        ('Lubricant 1L', 'LUB-1L', 50, 15, 'Bottles'),
        ('Filter Cartridge', 'FLT-CAR', 8, 5, 'Units'),
        ('Gasket Set', 'GAS-SET', 3, 5, 'Sets'),
    ]
    for pn, pnum, qty, reorder, unit in parts:
        execute_query(
            "INSERT INTO inventory (part_name, part_number, quantity, reorder_level, unit) VALUES (?, ?, ?, ?, ?)",
            (pn, pnum, qty, reorder, unit)
        )

    # Work orders
    today = datetime.now().strftime('%Y-%m-%d')
    execute_query(
        """INSERT INTO work_orders (equipment_id, assigned_to, title, description, priority, status, created_by)
           VALUES (4, 2, 'Conveyor B bearing replacement', 'Replace worn bearings on Conveyor B', 'high', 'in_progress', 1)"""
    )
    execute_query(
        """INSERT INTO work_orders (equipment_id, assigned_to, title, description, priority, status, created_by)
           VALUES (8, 2, 'Compressor Unit repair', 'Investigate abnormal noise', 'critical', 'pending', 1)"""
    )
    execute_query(
        """INSERT INTO work_orders (equipment_id, assigned_to, title, description, priority, status, date_completed, created_by)
           VALUES (1, 2, 'Routine lubrication', 'Monthly lubrication completed', 'low', 'completed', date('now'), 1)"""
    )

    # Preventive maintenance schedules
    next_week = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
    next_month = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
    execute_query(
        "INSERT INTO maintenance_schedule (equipment_id, task_name, frequency, next_due_date, assigned_to) VALUES (1, 'Bottling line inspection', 'weekly', ?, 2)",
        (next_week,)
    )
    execute_query(
        "INSERT INTO maintenance_schedule (equipment_id, task_name, frequency, next_due_date, assigned_to) VALUES (5, 'Filler calibration', 'monthly', ?, 2)",
        (next_month,)
    )

    print("Seed data created successfully.")
    print("Login: admin@cmms.com / admin123")


if __name__ == '__main__':
    from database.db import init_db
    init_db()
    seed()
