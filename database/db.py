# database/db.py - Database connection and query execution
"""
Provides database connection and safe query execution using prepared statements.
Protection against SQL injection via parameterized queries.
"""
import sqlite3
import os
import sys

# Add parent dir for config import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DATABASE


def get_connection():
    """Return a database connection with row factory for dict-like access."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def execute_query(query, params=(), fetch_one=False, fetch_all=False, commit=True):
    """
    Execute a parameterized query (prevents SQL injection).
    Uses ? placeholders - never concatenate user input into queries.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)

    result = None
    if fetch_one:
        row = cursor.fetchone()
        result = dict(row) if row else None
    elif fetch_all:
        rows = cursor.fetchall()
        result = [dict(row) for row in rows]
    else:
        if commit:
            conn.commit()
        result = cursor.lastrowid

    conn.close()
    return result


def init_db():
    """Initialize database from schema.sql and run migrations if needed."""
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    conn = get_connection()
    with open(schema_path, 'r') as f:
        conn.executescript(f.read())
    # Migration: add last_login to users if missing
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT last_login FROM users LIMIT 1")
    except sqlite3.OperationalError:
        conn.cursor().execute("ALTER TABLE users ADD COLUMN last_login TIMESTAMP")
        conn.commit()
    conn.close()
