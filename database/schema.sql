-- schema.sql - TINDI CMMS Database Schema
-- Production-ready schema for Factory Facility Equipment Maintenance Management System
-- Coca-Cola Plant Case Study - SQLite

-- Enable foreign keys
PRAGMA foreign_keys = ON;

-- ==================== USERS ====================
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('Admin', 'Maintenance Manager', 'Technician', 'Store Manager')),
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- Add last_login if not exists (migration)
-- ALTER TABLE users ADD COLUMN last_login TIMESTAMP;

-- ==================== LOGIN ACTIVITY (track new/recent logins for Admin) ====================
CREATE TABLE IF NOT EXISTS login_activity (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    login_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address TEXT,
    is_first_login INTEGER DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_login_activity_user ON login_activity(user_id);
CREATE INDEX IF NOT EXISTS idx_login_activity_at ON login_activity(login_at);

-- ==================== EQUIPMENT ====================
CREATE TABLE IF NOT EXISTS equipment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    location TEXT,
    status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active', 'faulty', 'under_maintenance', 'inactive')),
    qr_code TEXT,
    serial_number TEXT,
    purchase_date TEXT,
    last_maintenance_date TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_equipment_status ON equipment(status);
CREATE INDEX IF NOT EXISTS idx_equipment_category ON equipment(category);
CREATE INDEX IF NOT EXISTS idx_equipment_location ON equipment(location);

-- ==================== EQUIPMENT HISTORY (LOGS) ====================
CREATE TABLE IF NOT EXISTS equipment_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    equipment_id INTEGER NOT NULL,
    action TEXT NOT NULL,
    description TEXT,
    performed_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (equipment_id) REFERENCES equipment(id) ON DELETE CASCADE,
    FOREIGN KEY (performed_by) REFERENCES users(id)
);
CREATE INDEX IF NOT EXISTS idx_equipment_history_equipment ON equipment_history(equipment_id);

-- ==================== WORK ORDERS ====================
CREATE TABLE IF NOT EXISTS work_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    equipment_id INTEGER,
    assigned_to INTEGER,
    title TEXT NOT NULL,
    description TEXT,
    priority TEXT NOT NULL DEFAULT 'medium' CHECK(priority IN ('low', 'medium', 'high', 'critical')),
    status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending', 'in_progress', 'completed', 'cancelled')),
    scheduled_date TEXT,
    date_created TEXT DEFAULT (date('now')),
    date_completed TEXT,
    maintenance_notes TEXT,
    created_by INTEGER,
    FOREIGN KEY (equipment_id) REFERENCES equipment(id) ON DELETE SET NULL,
    FOREIGN KEY (assigned_to) REFERENCES users(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);
CREATE INDEX IF NOT EXISTS idx_work_orders_status ON work_orders(status);
CREATE INDEX IF NOT EXISTS idx_work_orders_equipment ON work_orders(equipment_id);
CREATE INDEX IF NOT EXISTS idx_work_orders_assigned ON work_orders(assigned_to);
CREATE INDEX IF NOT EXISTS idx_work_orders_priority ON work_orders(priority);
CREATE INDEX IF NOT EXISTS idx_work_orders_scheduled ON work_orders(scheduled_date);

-- ==================== MAINTENANCE RECORDS (per work order) ====================
CREATE TABLE IF NOT EXISTS maintenance_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    work_order_id INTEGER NOT NULL,
    actions_taken TEXT,
    parts_used TEXT,
    completion_status TEXT,
    hours_spent REAL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (work_order_id) REFERENCES work_orders(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_maintenance_records_wo ON maintenance_records(work_order_id);

-- ==================== INVENTORY ====================
CREATE TABLE IF NOT EXISTS inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    part_name TEXT NOT NULL,
    part_number TEXT,
    quantity INTEGER DEFAULT 0 CHECK(quantity >= 0),
    reorder_level INTEGER DEFAULT 5,
    unit TEXT DEFAULT 'Units',
    location TEXT,
    supplier TEXT,
    unit_cost REAL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_inventory_part_name ON inventory(part_name);
CREATE INDEX IF NOT EXISTS idx_inventory_low_stock ON inventory(quantity);

-- ==================== WORK ORDER PARTS (link parts to work orders) ====================
CREATE TABLE IF NOT EXISTS work_order_parts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    work_order_id INTEGER NOT NULL,
    inventory_id INTEGER NOT NULL,
    quantity_used INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (work_order_id) REFERENCES work_orders(id) ON DELETE CASCADE,
    FOREIGN KEY (inventory_id) REFERENCES inventory(id) ON DELETE RESTRICT
);
CREATE INDEX IF NOT EXISTS idx_wo_parts_wo ON work_order_parts(work_order_id);
CREATE INDEX IF NOT EXISTS idx_wo_parts_inv ON work_order_parts(inventory_id);

-- ==================== PREVENTIVE MAINTENANCE SCHEDULE ====================
CREATE TABLE IF NOT EXISTS maintenance_schedule (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    equipment_id INTEGER NOT NULL,
    task_name TEXT NOT NULL,
    frequency TEXT NOT NULL CHECK(frequency IN ('daily', 'weekly', 'biweekly', 'monthly', 'quarterly', 'annually')),
    next_due_date TEXT NOT NULL,
    last_completed_date TEXT,
    assigned_to INTEGER,
    is_active INTEGER DEFAULT 1,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (equipment_id) REFERENCES equipment(id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_to) REFERENCES users(id)
);
CREATE INDEX IF NOT EXISTS idx_schedule_equipment ON maintenance_schedule(equipment_id);
CREATE INDEX IF NOT EXISTS idx_schedule_next_due ON maintenance_schedule(next_due_date);

-- ==================== NOTIFICATIONS ====================
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    message TEXT,
    type TEXT DEFAULT 'info',
    is_read INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id);

-- ==================== AUDIT LOGS ====================
CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT NOT NULL,
    entity_type TEXT,
    entity_id INTEGER,
    old_value TEXT,
    new_value TEXT,
    ip_address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_audit_created ON audit_logs(created_at);
