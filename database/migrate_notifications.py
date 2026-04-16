import sqlite3
import os

DB_FILE = os.path.join(os.path.dirname(__file__), '..', 'cmms.db')

def migrate():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        cursor.execute("ALTER TABLE notifications ADD COLUMN task_id INTEGER REFERENCES work_orders(id) ON DELETE SET NULL")
        print("Added task_id column.")
    except sqlite3.OperationalError as e:
        print(f"Skipping task_id: {e}")

    try:
        cursor.execute("ALTER TABLE notifications ADD COLUMN channel TEXT DEFAULT 'in-app' CHECK(channel IN ('in-app', 'email', 'sms'))")
        print("Added channel column.")
    except sqlite3.OperationalError as e:
        print(f"Skipping channel: {e}")

    try:
        cursor.execute("ALTER TABLE notifications ADD COLUMN status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'sent', 'failed'))")
        print("Added status column.")
    except sqlite3.OperationalError as e:
        print(f"Skipping status: {e}")

    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == '__main__':
    migrate()
