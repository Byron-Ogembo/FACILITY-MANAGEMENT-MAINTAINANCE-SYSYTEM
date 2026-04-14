from database.db import get_connection

def assign_technician(work_order_id):
    conn = get_connection()
    cursor = conn.cursor()
    
    # Simple logic: Find a technician with least assigned active work orders
    cursor.execute("""
        SELECT u.id, COUNT(w.id) as active_tasks 
        FROM users u
        LEFT JOIN work_orders w ON u.id = w.assigned_to AND w.status IN ('pending', 'in_progress')
        WHERE u.role = 'Technician' AND u.is_active = 1
        GROUP BY u.id
        ORDER BY active_tasks ASC
        LIMIT 1
    """)
    tech = cursor.fetchone()
    
    if tech:
        tech_id = tech['id']
        cursor.execute("UPDATE work_orders SET assigned_to = ? WHERE id = ?", (tech_id, work_order_id))
        
        # Create a notification
        cursor.execute(
            "INSERT INTO notifications (user_id, title, message, type) VALUES (?, ?, ?, ?)",
            (tech_id, "New Task Assigned", f"You have been automatically assigned to Work Order #{work_order_id}", "info")
        )
        conn.commit()
        conn.close()
        return tech_id
    
    conn.close()
    return None
