# app/routes/equipment_routes.py - Equipment (asset) management
"""Equipment CRUD, history, QR codes."""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_file
from app.routes.auth_routes import login_required, role_required
from app.models.equipment import get_all, get_by_id, create, update, delete, add_history, get_history
from app.utils.validators import sanitize_string, sanitize_int
from app.models.audit_log import log as audit_log
import io
import qrcode

equipment_bp = Blueprint('equipment', __name__)


@equipment_bp.route('')
@login_required
@role_required('Admin', 'Maintenance Manager', 'Technician')
def list_equipment():
    equipment = get_all()
    can_manage = session.get('user_role') in ['Admin', 'Maintenance Manager']
    return render_template('equipment/list.html', equipment=equipment, can_manage=can_manage)


@equipment_bp.route('/add', methods=['GET', 'POST'])
@login_required
@role_required('Admin', 'Maintenance Manager')
def add():
    if request.method == 'POST':
        name = sanitize_string(request.form.get('name'), 200)
        category = sanitize_string(request.form.get('category'), 100)
        location = sanitize_string(request.form.get('location'), 200)
        status = request.form.get('status', 'active')
        serial = sanitize_string(request.form.get('serial_number'), 100)
        notes = sanitize_string(request.form.get('notes'), 500)
        if not name or not category:
            flash('Name and category are required.', 'danger')
            return redirect(url_for('equipment.add'))
        if status not in ['active', 'faulty', 'under_maintenance', 'inactive']:
            status = 'active'
        eq_id = create(name, category, location, status, serial, notes)
        add_history(eq_id, 'CREATED', f'Equipment {name} added', session.get('user_id'))
        audit_log(session['user_id'], 'CREATE', 'equipment', eq_id, new_value=name)
        flash('Equipment added successfully.', 'success')
        return redirect(url_for('equipment.list_equipment'))
    return render_template('equipment/form.html', equipment=None)


@equipment_bp.route('/<int:eq_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('Admin', 'Maintenance Manager')
def edit(eq_id):
    eq = get_by_id(eq_id)
    if not eq:
        flash('Equipment not found.', 'danger')
        return redirect(url_for('equipment.list_equipment'))
    if request.method == 'POST':
        name = sanitize_string(request.form.get('name'), 200)
        category = sanitize_string(request.form.get('category'), 100)
        location = sanitize_string(request.form.get('location'), 200)
        status = request.form.get('status', 'active')
        serial = sanitize_string(request.form.get('serial_number'), 100)
        notes = sanitize_string(request.form.get('notes'), 500)
        if not name or not category:
            flash('Name and category are required.', 'danger')
            return redirect(url_for('equipment.edit', eq_id=eq_id))
        if status not in ['active', 'faulty', 'under_maintenance', 'inactive']:
            status = 'active'
        update(eq_id, name, category, location, status, serial, notes)
        add_history(eq_id, 'UPDATED', f'Equipment updated', session.get('user_id'))
        audit_log(session['user_id'], 'UPDATE', 'equipment', eq_id, old_value=eq['name'], new_value=name)
        flash('Equipment updated successfully.', 'success')
        return redirect(url_for('equipment.list_equipment'))
    return render_template('equipment/form.html', equipment=eq)


@equipment_bp.route('/<int:eq_id>/delete', methods=['POST'])
@login_required
@role_required('Admin', 'Maintenance Manager')
def delete_equipment(eq_id):
    eq = get_by_id(eq_id)
    if not eq:
        flash('Equipment not found.', 'danger')
        return redirect(url_for('equipment.list_equipment'))
    audit_log(session['user_id'], 'DELETE', 'equipment', eq_id, old_value=eq['name'])
    delete(eq_id)
    flash('Equipment deleted.', 'success')
    return redirect(url_for('equipment.list_equipment'))


@equipment_bp.route('/<int:eq_id>/history')
@login_required
def history(eq_id):
    eq = get_by_id(eq_id)
    if not eq:
        flash('Equipment not found.', 'danger')
        return redirect(url_for('equipment.list_equipment'))
    history_list = get_history(eq_id)
    return render_template('equipment/history.html', equipment=eq, history=history_list)


@equipment_bp.route('/<int:eq_id>/qr')
@login_required
def qr_code(eq_id):
    """Generate QR code for equipment (free, no API)."""
    eq = get_by_id(eq_id)
    if not eq:
        return "Not found", 404
    # QR content: equipment ID and name for scanning
    content = f"CMMS-EQ-{eq_id}|{eq['name']}|{eq.get('location','')}"
    qr = qrcode.QRCode(version=1, box_size=8, border=4)
    qr.add_data(content)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return send_file(buf, mimetype='image/png', as_attachment=False, download_name=f'equipment-{eq_id}-qr.png')
