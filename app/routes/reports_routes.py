# app/routes/reports_routes.py - Reports, analytics, MTTR, MTBF, export
"""Reports, analytics, MTTR/MTBF calculation, PDF/CSV export."""
from flask import Blueprint, render_template, request, send_file, Response
from app.routes.auth_routes import login_required, role_required
from database.db import execute_query
from io import BytesIO, StringIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime

reports_bp = Blueprint('reports', __name__)


def _mttr():
    """Mean Time To Repair - average hours from work order creation to completion."""
    rows = execute_query(
        """SELECT date_created, date_completed FROM work_orders
           WHERE status='completed' AND date_completed IS NOT NULL AND date_created IS NOT NULL""",
        fetch_all=True
    )
    if not rows:
        return 0
    total_hours = 0
    count = 0
    for r in rows:
        try:
            dc = datetime.strptime(r['date_created'][:10], '%Y-%m-%d')
            dco = datetime.strptime(r['date_completed'][:10], '%Y-%m-%d')
            delta = (dco - dc).total_seconds() / 3600
            total_hours += delta
            count += 1
        except Exception:
            pass
    return round(total_hours / count, 2) if count else 0


def _mtbf():
    """Mean Time Between Failures - simplified: days between completed work orders per equipment."""
    rows = execute_query(
        """SELECT equipment_id, date_completed FROM work_orders
           WHERE status='completed' AND equipment_id IS NOT NULL AND date_completed IS NOT NULL
           ORDER BY equipment_id, date_completed""",
        fetch_all=True
    )
    if len(rows) < 2:
        return 0
    gaps = []
    prev_eq = None
    prev_date = None
    for r in rows:
        try:
            d = datetime.strptime(r['date_completed'][:10], '%Y-%m-%d')
            if prev_eq == r['equipment_id'] and prev_date:
                gaps.append((d - prev_date).days)
            prev_eq = r['equipment_id']
            prev_date = d
        except Exception:
            pass
    return round(sum(gaps) / len(gaps), 1) if gaps else 0


@reports_bp.route('')
@login_required
@role_required('Admin', 'Maintenance Manager')
def index():
    """Reports dashboard with key metrics."""
    total_equipment = execute_query("SELECT COUNT(*) as c FROM equipment", fetch_one=True)['c']
    total_wo = execute_query("SELECT COUNT(*) as c FROM work_orders", fetch_one=True)['c']
    completed_wo = execute_query("SELECT COUNT(*) as c FROM work_orders WHERE status='completed'", fetch_one=True)['c']
    mttr = _mttr()
    mtbf = _mtbf()
    downtime_by_cat = execute_query(
        """SELECT e.category, COUNT(w.id) as count FROM work_orders w
           JOIN equipment e ON w.equipment_id = e.id
           WHERE w.status='completed' GROUP BY e.category""",
        fetch_all=True
    )
    wo_by_priority = execute_query(
        "SELECT priority, COUNT(*) as count FROM work_orders GROUP BY priority",
        fetch_all=True
    )
    return render_template('reports/index.html',
        total_equipment=total_equipment,
        total_work_orders=total_wo,
        completed_work_orders=completed_wo,
        mttr=mttr,
        mtbf=mtbf,
        downtime_by_cat=downtime_by_cat,
        wo_by_priority=wo_by_priority
    )


@reports_bp.route('/export/csv')
@login_required
@role_required('Admin', 'Maintenance Manager')
def export_csv():
    """Export work orders to CSV."""
    report_type = request.args.get('type', 'work_orders')
    if report_type == 'work_orders':
        rows = execute_query(
            """SELECT w.id, w.title, w.status, w.priority, w.date_created, w.date_completed,
                      e.name as equipment_name, u.name as assigned_to
               FROM work_orders w LEFT JOIN equipment e ON w.equipment_id = e.id
               LEFT JOIN users u ON w.assigned_to = u.id ORDER BY w.date_created DESC""",
            fetch_all=True
        )
    elif report_type == 'equipment':
        rows = execute_query("SELECT * FROM equipment ORDER BY name", fetch_all=True)
    elif report_type == 'inventory':
        rows = execute_query("SELECT * FROM inventory ORDER BY part_name", fetch_all=True)
    else:
        rows = []
    if not rows:
        return "No data", 404
    keys = list(rows[0].keys())
    output = StringIO()
    output.write(','.join(keys) + '\n')
    for r in rows:
        line = ','.join(str(r.get(k, '')).replace(',', ';').replace('"', "'") for k in keys)
        output.write(line + '\n')
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=cmms_{report_type}_{datetime.now().strftime("%Y%m%d")}.csv'}
    )


@reports_bp.route('/export/pdf')
@login_required
@role_required('Admin', 'Maintenance Manager')
def export_pdf():
    """Export maintenance report to PDF."""
    report_type = request.args.get('type', 'summary')
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    elements.append(Paragraph("TINDI CMMS - Maintenance Report", styles['Title']))
    elements.append(Paragraph(datetime.now().strftime("%Y-%m-%d %H:%M"), styles['Normal']))
    elements.append(Spacer(1, 20))
    if report_type == 'summary':
        mttr = _mttr()
        mtbf = _mtbf()
        data = [
            ['Metric', 'Value'],
            ['MTTR (hours)', str(mttr)],
            ['MTBF (days)', str(mtbf)],
            ['Total Equipment', str(execute_query("SELECT COUNT(*) as c FROM equipment", fetch_one=True)['c'])],
            ['Pending Work Orders', str(execute_query("SELECT COUNT(*) as c FROM work_orders WHERE status IN ('pending','in_progress')", fetch_one=True)['c'])],
        ]
    else:
        rows = execute_query(
            """SELECT w.id, w.title, w.status, w.priority, w.date_created, e.name as equipment
               FROM work_orders w LEFT JOIN equipment e ON w.equipment_id = e.id
               ORDER BY w.date_created DESC LIMIT 50""",
            fetch_all=True
        )
        data = [['ID', 'Title', 'Status', 'Priority', 'Date', 'Equipment']]
        for r in rows:
            data.append([str(r.get('id','')), str(r.get('title','')), str(r.get('status','')), str(r.get('priority','')), str(r.get('date_created','')), str(r.get('equipment',''))])
    t = Table(data)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(t)
    doc.build(elements)
    buffer.seek(0)
    return send_file(buffer, mimetype='application/pdf', as_attachment=True, download_name=f'cmms_report_{datetime.now().strftime("%Y%m%d")}.pdf')
