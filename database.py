import sqlite3
import os

DB_FILE = "cmms.db"

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS equipment (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT,
        status TEXT,
        location TEXT
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS work_orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        equipment_id INTEGER,
        assigned_to INTEGER,
        status TEXT,
        description TEXT,
        date_created TEXT,
        date_completed TEXT,
        FOREIGN KEY (equipment_id) REFERENCES equipment (id),
        FOREIGN KEY (assigned_to) REFERENCES users (id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS maintenance_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        work_order_id INTEGER,
        actions_taken TEXT,
        parts_used TEXT,
        completion_status TEXT,
        FOREIGN KEY (work_order_id) REFERENCES work_orders (id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        part_name TEXT NOT NULL,
        quantity INTEGER DEFAULT 0,
        reorder_level INTEGER DEFAULT 0
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS maintenance_schedule (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        equipment_id INTEGER,
        frequency TEXT,
        next_date TEXT,
        FOREIGN KEY (equipment_id) REFERENCES equipment (id)
    )
    ''')
    
    # Insert default admin user if not exists
    cursor.execute("SELECT id FROM users WHERE email='admin@cmms.com'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (name, email, password, role) VALUES ('Admin', 'admin@cmms.com', 'admin123', 'Maintenance Manager')")
        
    conn.commit()
    conn.close()

def execute_query(query, params=(), fetch_one=False, fetch_all=False):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    
    result = None
    if fetch_one:
        row = cursor.fetchone()
        if row:
            result = dict(row)
    elif fetch_all:
        rows = cursor.fetchall()
        result = [dict(row) for row in rows]
    else:
        conn.commit()
        result = cursor.lastrowid
        
    conn.close()
    return result

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully.")
