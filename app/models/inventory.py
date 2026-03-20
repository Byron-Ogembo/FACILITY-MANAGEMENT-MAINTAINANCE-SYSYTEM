# app/models/inventory.py - Inventory (spare parts) model
"""Inventory management with low stock alerts and work order linking."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from database.db import execute_query


def get_all():
    """Get all inventory items."""
    return execute_query("SELECT * FROM inventory ORDER BY part_name", fetch_all=True)


def get_by_id(inv_id):
    """Get inventory item by ID."""
    return execute_query("SELECT * FROM inventory WHERE id = ?", (inv_id,), fetch_one=True)


def create(part_name, part_number='', quantity=0, reorder_level=5, unit='Units', location='', supplier='', unit_cost=0):
    """Create inventory item. Returns new id."""
    return execute_query(
        """INSERT INTO inventory (part_name, part_number, quantity, reorder_level, unit, location, supplier, unit_cost)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (part_name, part_number, quantity, reorder_level, unit, location, supplier, unit_cost)
    )


def update(inv_id, part_name, part_number, quantity, reorder_level, unit, location, supplier, unit_cost):
    """Update inventory item."""
    execute_query(
        """UPDATE inventory SET part_name=?, part_number=?, quantity=?, reorder_level=?, unit=?, location=?, supplier=?, unit_cost=?, updated_at=CURRENT_TIMESTAMP WHERE id=?""",
        (part_name, part_number, quantity, reorder_level, unit, location, supplier, unit_cost, inv_id)
    )


def update_quantity(inv_id, quantity_delta):
    """Adjust quantity (positive to add, negative to subtract)."""
    execute_query(
        "UPDATE inventory SET quantity = MAX(0, quantity + ?), updated_at=CURRENT_TIMESTAMP WHERE id=?",
        (quantity_delta, inv_id)
    )


def delete(inv_id):
    """Delete inventory item."""
    execute_query("DELETE FROM inventory WHERE id = ?", (inv_id,))


def get_low_stock():
    """Get items where quantity <= reorder_level."""
    return execute_query(
        "SELECT * FROM inventory WHERE quantity <= reorder_level ORDER BY quantity ASC",
        fetch_all=True
    )
