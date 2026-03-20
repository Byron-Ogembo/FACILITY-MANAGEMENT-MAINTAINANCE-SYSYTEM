# TINDI CMMS - Factory Facility Equipment Maintenance Management System

**Coca-Cola Plant Case Study**

A complete, production-ready CMMS built with Flask, SQLite, Bootstrap, and Chart.js. Implements MVC architecture with clean, modular, and well-commented code.

## Tech Stack

- **Backend:** Python 3, Flask
- **Database:** SQLite (free, no setup required)
- **Frontend:** HTML, CSS, JavaScript, Bootstrap 5
- **Charts:** Chart.js
- **QR Codes:** qrcode (server-side)
- **PDF Export:** ReportLab

## Project Structure

```
byron22/
├── app/
│   ├── app.py              # Flask app factory
│   ├── models/             # Data models (MVC - Model)
│   ├── routes/             # Controllers (MVC - Controller)
│   └── utils/              # Security, validators
├── database/
│   ├── schema.sql          # Database schema
│   └── db.py               # Connection, queries
├── templates/              # Jinja2 templates (MVC - View)
├── static/                 # CSS, JS (optional)
├── instance/               # SQLite DB (auto-created)
├── config.py
├── run.py
├── seed_data.py
└── requirements.txt
```

## Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Initialize database and seed sample data:**
   ```bash
   python seed_data.py
   ```

3. **Run the application:**
   ```bash
   python run.py
   ```

4. **Open in browser:** http://localhost:5000

## Default Credentials (company-provided)

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@cmms.com | admin123 |
| Technician | john@cmms.com | tech123 |
| Maintenance Manager | maria@cmms.com | manager123 |
| Store Manager | steve@cmms.com | store123 |

**Staff Sign-In:** Employees use credentials provided by the company. Admin adds new staff via User Management.

## Core Features

### 1. Authentication & User Management
- **Staff sign-in** – Company-provided credentials (Admin creates users)
- Password hashing (Werkzeug pbkdf2:sha256)
- **Role-based access:** Admin (full), Maintenance Manager, Technician, Store Manager
- **Login activity** – Admin sees new/first-time logins
- Session management and logout
- Audit logging for security

### 2. Dashboard
- Overview stats: total equipment, active work orders, completed tasks, faulty equipment
- Chart.js: equipment by status, work orders by status
- Notifications: pending maintenance, low stock alerts

### 3. Equipment Management
- Add, edit, delete equipment
- Categories: bottling machines, conveyors, fillers, etc.
- Status: active, faulty, under maintenance, inactive
- Equipment history logs
- **QR code** for each equipment (free, no API)

### 4. Work Order Management
- Create work orders with title, description, priority
- Assign to technicians
- Priority: low, medium, high, critical
- Status: pending, in progress, completed, cancelled
- Maintenance notes and completion tracking

### 5. Preventive Maintenance
- Schedule recurring tasks (daily, weekly, monthly, etc.)
- Auto-generate work orders for due tasks
- Complete and reschedule next due date
- Reminder notifications on dashboard

### 6. Inventory Management
- Add/edit spare parts
- Track quantity and reorder level
- Low stock alerts
- Link parts to work orders (schema ready)

### 7. Reports & Analytics
- MTTR (Mean Time To Repair)
- MTBF (Mean Time Between Failures)
- Downtime by equipment category
- Work orders by priority
- **Export:** CSV (work orders, equipment, inventory), PDF summary

### 8. Security
- Input validation and sanitization
- Parameterized queries (SQL injection protection)
- Role-based access control
- Audit logs (Admin only)

### 9. Role-Based Access
- **Admin:** Full system, user management, login activity, audit logs
- **Maintenance Manager:** Equipment, work orders, preventive maintenance, inventory view, reports
- **Technician:** Equipment view, assigned work orders only (edit/complete)
- **Store Manager:** Inventory management, low stock alerts

## Database Schema

- `users` - authentication, roles
- `equipment` - assets with status, category, location
- `equipment_history` - change logs
- `work_orders` - maintenance tasks
- `maintenance_records` - per-WO details
- `work_order_parts` - parts used per WO
- `inventory` - spare parts
- `maintenance_schedule` - preventive tasks
- `notifications` - user alerts
- `audit_logs` - security audit trail

## License

Internal use / Case study. Coca-Cola Plant implementation.
