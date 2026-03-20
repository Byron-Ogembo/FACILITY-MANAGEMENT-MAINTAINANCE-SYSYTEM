# app/routes/inventory_routes.py - Inventory (spare parts) management
"""Inventory CRUD, low stock alerts, work order linking."""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.routes.auth_routes import login_required, role_required
from app.models.inventory import get_all, get_by_id, create, update, delete, get_low_stock
from app.utils.validators import sanitize_string, sanitize_int, sanitize_float
from app.models.audit_log import log as audit_log

inventory_bp = Blueprint('inventory', __name__)


@inventory_bp.route('')
@login_required
@role_required('Admin', 'Store Manager', 'Maintenance Manager')
def list_inventory():
    items = get_all()
    low = get_low_stock()
    can_manage = session.get('user_role') in ['Admin', 'Store Manager']
    return render_template('inventory/list.html', inventory=items, low_stock=low, can_manage=can_manage)


@inventory_bp.route('/add', methods=['GET', 'POST'])
@login_required
@role_required('Admin', 'Store Manager')
def add():
    if request.method == 'POST':
        part_name = sanitize_string(request.form.get('part_name'), 200)
        part_number = sanitize_string(request.form.get('part_number'), 100)
        quantity = sanitize_int(request.form.get('quantity'), 0, 0)
        reorder_level = sanitize_int(request.form.get('reorder_level'), 5, 0)
        unit = sanitize_string(request.form.get('unit', 'Units'), 20)
        location = sanitize_string(request.form.get('location'), 200)
        supplier = sanitize_string(request.form.get('supplier'), 200)
        unit_cost = sanitize_float(request.form.get('unit_cost', 0))
        if not part_name:
            flash('Part name is required.', 'danger')
            return redirect(url_for('inventory.add'))
        inv_id = create(part_name, part_number, quantity, reorder_level, unit, location, supplier, unit_cost)
        audit_log(session['user_id'], 'CREATE', 'inventory', inv_id, new_value=part_name)
        flash('Part added successfully.', 'success')
        return redirect(url_for('inventory.list_inventory'))
    return render_template('inventory/form.html', item=None)


@inventory_bp.route('/<int:inv_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('Admin', 'Store Manager')
def edit(inv_id):
    item = get_by_id(inv_id)
    if not item:
        flash('Part not found.', 'danger')
        return redirect(url_for('inventory.list_inventory'))
    if request.method == 'POST':
        part_name = sanitize_string(request.form.get('part_name'), 200)
        part_number = sanitize_string(request.form.get('part_number'), 100)
        quantity = sanitize_int(request.form.get('quantity'), 0, 0)
        reorder_level = sanitize_int(request.form.get('reorder_level'), 5, 0)
        unit = sanitize_string(request.form.get('unit', 'Units'), 20)
        location = sanitize_string(request.form.get('location'), 200)
        supplier = sanitize_string(request.form.get('supplier'), 200)
        unit_cost = sanitize_float(request.form.get('unit_cost', 0))
        if part_name:
            update(inv_id, part_name, part_number, quantity, reorder_level, unit, location, supplier, unit_cost)
            audit_log(session['user_id'], 'UPDATE', 'inventory', inv_id, new_value=part_name)
            flash('Part updated successfully.', 'success')
        return redirect(url_for('inventory.list_inventory'))
    return render_template('inventory/form.html', item=item)


@inventory_bp.route('/<int:inv_id>/delete', methods=['POST'])
@login_required
@role_required('Admin', 'Store Manager')
def delete_item(inv_id):
    item = get_by_id(inv_id)
    if not item:
        flash('Part not found.', 'danger')
        return redirect(url_for('inventory.list_inventory'))
    audit_log(session['user_id'], 'DELETE', 'inventory', inv_id, old_value=item['part_name'])
    delete(inv_id)
    flash('Part deleted.', 'success')
    return redirect(url_for('inventory.list_inventory'))
