# app/routes/work_order_routes.py - Work order management
"""Work orders with priority, assignment, maintenance notes."""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.routes.auth_routes import login_required, role_required
from app.models.work_order import get_all, get_by_id, create, update, update_status, delete, add_maintenance_record
from app.models.equipment import get_all as get_equipment
from app.models.user import get_technicians
from app.utils.validators import sanitize_string
from app.models.audit_log import log as audit_log
from app.models.notification import create as create_notification

work_order_bp = Blueprint('work_order', __name__)


@work_order_bp.route('')
@login_required
@role_required('Admin', 'Maintenance Manager', 'Technician')
def list_work_orders():
    if session.get('user_role') == 'Technician':
        wos = get_all(assigned_to_user_id=session['user_id'])
    else:
        wos = get_all()
    can_create = session.get('user_role') in ['Admin', 'Maintenance Manager']
    return render_template('work_orders/list.html', work_orders=wos, can_create=can_create)


@work_order_bp.route('/add', methods=['GET', 'POST'])
@login_required
@role_required('Admin', 'Maintenance Manager')
def add():
    if request.method == 'POST':
        equipment_id = request.form.get('equipment_id') or None
        if equipment_id:
            equipment_id = int(equipment_id) if str(equipment_id).isdigit() else None
        assigned_to = request.form.get('assigned_to') or None
        if assigned_to:
            assigned_to = int(assigned_to) if str(assigned_to).isdigit() else None
        title = sanitize_string(request.form.get('title'), 200)
        description = sanitize_string(request.form.get('description'), 1000)
        priority = request.form.get('priority', 'medium')
        if priority not in ['low', 'medium', 'high', 'critical']:
            priority = 'medium'
        if not title:
            flash('Title is required.', 'danger')
            return redirect(url_for('work_order.add'))
        wo_id = create(equipment_id, assigned_to, title, description, priority, 'pending', session.get('user_id'))
        if not assigned_to:
            from app.services.assignment_service import assign_technician
            auto_assigned = assign_technician(wo_id)
            if auto_assigned:
                assigned_to = auto_assigned
                flash('Technician automatically assigned based on workload.', 'info')
        
        if assigned_to:
            create_notification(assigned_to, 'New Work Order', f'You were assigned: {title}', 'info')
            
            # Send Email Asynchronously
            from app.models.user import get_by_id as get_user
            user_data = get_user(assigned_to)
            if user_data and user_data.get('email'):
                from app.services.notification_service import send_assignment_email
                import threading
                threading.Thread(target=send_assignment_email, args=(user_data['email'], {'title': title, 'priority': priority})).start()
                
        from app.services.notification_service import emit_realtime_notification
        emit_realtime_notification(broadcast=True, title='New Work Order Alert', message=f'A new work order was created: {title}', n_type='warning')
        
        audit_log(session['user_id'], 'CREATE', 'work_order', wo_id, new_value=title)
        flash('Work order created successfully.', 'success')
        return redirect(url_for('work_order.list_work_orders'))
    equipment = get_equipment()
    technicians = get_technicians()
    return render_template('work_orders/form.html', work_order=None, equipment=equipment, technicians=technicians)


@work_order_bp.route('/<int:wo_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('Admin', 'Maintenance Manager', 'Technician')
def edit(wo_id):
    wo = get_by_id(wo_id)
    if not wo:
        flash('Work order not found.', 'danger')
        return redirect(url_for('work_order.list_work_orders'))
    if session.get('user_role') == 'Technician' and wo.get('assigned_to') != session.get('user_id'):
        flash('Access denied. You can only edit work orders assigned to you.', 'danger')
        return redirect(url_for('work_order.list_work_orders'))
    if request.method == 'POST':
        equipment_id = request.form.get('equipment_id') or None
        if equipment_id:
            equipment_id = int(equipment_id) if str(equipment_id).isdigit() else None
        assigned_to = request.form.get('assigned_to') or None
        if assigned_to:
            assigned_to = int(assigned_to) if str(assigned_to).isdigit() else None
        title = sanitize_string(request.form.get('title'), 200)
        description = sanitize_string(request.form.get('description'), 1000)
        priority = request.form.get('priority', 'medium')
        status = request.form.get('status', wo['status'])
        notes = sanitize_string(request.form.get('maintenance_notes'), 2000)
        if title:
            update(wo_id, equipment_id, assigned_to, title, description, priority, status, notes)
            audit_log(session['user_id'], 'UPDATE', 'work_order', wo_id, new_value=title)
            flash('Work order updated.', 'success')
        return redirect(url_for('work_order.list_work_orders'))
    equipment = get_equipment()
    technicians = get_technicians()
    return render_template('work_orders/form.html', work_order=wo, equipment=equipment, technicians=technicians)


@work_order_bp.route('/<int:wo_id>/complete', methods=['POST'])
@login_required
@role_required('Admin', 'Maintenance Manager', 'Technician')
def complete(wo_id):
    wo = get_by_id(wo_id)
    if not wo:
        flash('Work order not found.', 'danger')
        return redirect(url_for('work_order.list_work_orders'))
    if session.get('user_role') == 'Technician' and wo.get('assigned_to') != session.get('user_id'):
        flash('Access denied.', 'danger')
        return redirect(url_for('work_order.list_work_orders'))
    notes = sanitize_string(request.form.get('maintenance_notes', ''), 2000)
    update_status(wo_id, 'completed', notes)
    audit_log(session['user_id'], 'COMPLETE', 'work_order', wo_id)
    flash('Work order marked as completed.', 'success')
    return redirect(url_for('work_order.list_work_orders'))


@work_order_bp.route('/<int:wo_id>/status', methods=['POST'])
@login_required
@role_required('Admin', 'Maintenance Manager', 'Technician')
def change_status(wo_id):
    wo = get_by_id(wo_id)
    if wo and session.get('user_role') == 'Technician' and wo.get('assigned_to') != session.get('user_id'):
        flash('Access denied.', 'danger')
        return redirect(url_for('work_order.list_work_orders'))
    status = request.form.get('status', '')
    if status not in ['pending', 'in_progress', 'completed', 'cancelled']:
        flash('Invalid status.', 'danger')
        return redirect(url_for('work_order.list_work_orders'))
    update_status(wo_id, status)
    flash(f'Status updated to {status}.', 'success')
    return redirect(url_for('work_order.list_work_orders'))


@work_order_bp.route('/<int:wo_id>/delete', methods=['POST'])
@login_required
@role_required('Admin', 'Maintenance Manager')
def delete_work_order(wo_id):
    wo = get_by_id(wo_id)
    if not wo:
        flash('Work order not found.', 'danger')
        return redirect(url_for('work_order.list_work_orders'))
    audit_log(session['user_id'], 'DELETE', 'work_order', wo_id, old_value=wo['title'])
    delete(wo_id)
    flash('Work order deleted.', 'success')
    return redirect(url_for('work_order.list_work_orders'))
