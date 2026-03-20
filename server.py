import http.server
import socketserver
import json
import os
import urllib.parse
from database import init_db, execute_query

PORT = 8000

class CMMSRequestHandler(http.server.SimpleHTTPRequestHandler):
    
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        if path.startswith('/api/'):
            self.handle_api_get(path)
            return
        # Fallback for SPA routing - serve index.html for routes that don't match static files
        static_extensions = ('.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg', '.woff', '.woff2')
        path_clean = path.split('?')[0].strip('/')
        is_static = path.startswith(('/css/', '/js/', '/assets/')) or any(path.endswith(ext) for ext in static_extensions)
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), path_clean) if path_clean else None
        if path == '/' or path == '' or (not is_static and (not path_clean or not os.path.isfile(file_path))):
            self.path = '/index.html'
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        if path.startswith('/api/'):
            self.handle_api_post(path)
        else:
            self.send_error(404, "Not Found")
            
    def do_PUT(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        if path.startswith('/api/'):
            self.handle_api_put(path)
        else:
            self.send_error(404, "Not Found")
            
    def do_DELETE(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        if path.startswith('/api/'):
            self.handle_api_delete(path)
        else:
            self.send_error(404, "Not Found")

    def _get_payload(self):
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length > 0:
            body = self.rfile.read(content_length)
            return json.loads(body)
        return {}

    def _send_json_response(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    # --- API Handlers ---
    def handle_api_get(self, path):
        try:
            parts = path.split('/')
            if path == '/api/equipment':
                data = execute_query("SELECT * FROM equipment", fetch_all=True)
                self._send_json_response(data)
            elif len(parts) == 4 and parts[1] == 'api' and parts[2] == 'equipment':
                row = execute_query("SELECT * FROM equipment WHERE id=?", (parts[3],), fetch_one=True)
                self._send_json_response(row if row else {"error": "Not found"})
            elif path == '/api/work_orders':
                data = execute_query("SELECT w.*, e.name as equipment_name, u.name as assigned_user FROM work_orders w LEFT JOIN equipment e ON w.equipment_id = e.id LEFT JOIN users u ON w.assigned_to = u.id", fetch_all=True)
                self._send_json_response(data)
            elif path == '/api/inventory':
                data = execute_query("SELECT * FROM inventory", fetch_all=True)
                self._send_json_response(data)
            elif len(parts) == 4 and parts[1] == 'api' and parts[2] == 'inventory':
                row = execute_query("SELECT * FROM inventory WHERE id=?", (parts[3],), fetch_one=True)
                self._send_json_response(row if row else {"error": "Not found"})
            elif path == '/api/users':
                data = execute_query("SELECT id, name, email, role FROM users", fetch_all=True)
                self._send_json_response(data)
            elif path == '/api/dashboard/stats':
                eq_count = execute_query("SELECT COUNT(*) as count FROM equipment", fetch_one=True)['count']
                wo_pending = execute_query("SELECT COUNT(*) as count FROM work_orders WHERE status='pending'", fetch_one=True)['count']
                wo_completed = execute_query("SELECT COUNT(*) as count FROM work_orders WHERE status='completed'", fetch_one=True)['count']
                stats = {
                    "total_equipment": eq_count, 
                    "pending_work_orders": wo_pending,
                    "completed_work_orders": wo_completed,
                    "system_status": "Operational"
                }
                self._send_json_response(stats)
            else:
                self.send_error(404, "API Endpoint Not Found")
        except Exception as e:
            self._send_json_response({"error": str(e)}, status=500)

    def handle_api_post(self, path):
        payload = self._get_payload()
        try:
            if path == '/api/login':
                email = payload.get('email')
                password = payload.get('password')
                user = execute_query("SELECT id, name, email, role FROM users WHERE email=? AND password=?", (email, password), fetch_one=True)
                if user:
                    self._send_json_response({"success": True, "user": user})
                else:
                    self._send_json_response({"success": False, "error": "Invalid credentials"}, status=401)
            elif path == '/api/equipment':
                new_id = execute_query("INSERT INTO equipment (name, category, status, location) VALUES (?, ?, ?, ?)", 
                                       (payload.get('name'), payload.get('category'), payload.get('status', 'Active'), payload.get('location')))
                self._send_json_response({"success": True, "id": new_id})
            elif path == '/api/inventory':
                new_id = execute_query("INSERT INTO inventory (part_name, quantity, reorder_level) VALUES (?, ?, ?)", 
                                       (payload.get('part_name'), payload.get('quantity', 0), payload.get('reorder_level', 0)))
                self._send_json_response({"success": True, "id": new_id})
            elif path == '/api/work_orders':
                new_id = execute_query("INSERT INTO work_orders (equipment_id, assigned_to, status, description, date_created) VALUES (?, ?, ?, ?, date('now'))", 
                                       (payload.get('equipment_id'), payload.get('assigned_to'), payload.get('status', 'pending'), payload.get('description')))
                self._send_json_response({"success": True, "id": new_id})
            else:
                self.send_error(404, "API Endpoint Not Found")
        except Exception as e:
            self._send_json_response({"error": str(e)}, status=500)
            
    def handle_api_put(self, path):
        payload = self._get_payload()
        parts = path.split('/')
        if len(parts) >= 4:
            resource = parts[2]
            res_id = parts[3]
            try:
                if resource == 'equipment':
                    row = execute_query("SELECT * FROM equipment WHERE id=?", (res_id,), fetch_one=True)
                    if not row:
                        self._send_json_response({"error": "Not found"}, status=404)
                        return
                    name = payload.get('name', row['name'])
                    category = payload.get('category', row['category'])
                    status = payload.get('status', row['status'])
                    location = payload.get('location', row['location'])
                    execute_query("UPDATE equipment SET name=?, category=?, status=?, location=? WHERE id=?",
                                  (name, category, status, location, res_id))
                    self._send_json_response({"success": True})
                elif resource == 'work_orders':
                    row = execute_query("SELECT * FROM work_orders WHERE id=?", (res_id,), fetch_one=True)
                    if not row:
                        self._send_json_response({"error": "Not found"}, status=404)
                        return
                    status = payload.get('status', row['status'])
                    description = payload.get('description', row['description'])
                    assigned_to = payload.get('assigned_to', row['assigned_to'])
                    date_completed = payload.get('date_completed', row['date_completed'])
                    if status == 'completed' and not date_completed:
                        from datetime import date
                        date_completed = str(date.today())
                    execute_query("UPDATE work_orders SET status=?, description=?, assigned_to=?, date_completed=? WHERE id=?",
                                  (status, description, assigned_to, date_completed, res_id))
                    self._send_json_response({"success": True})
                elif resource == 'inventory':
                    row = execute_query("SELECT * FROM inventory WHERE id=?", (res_id,), fetch_one=True)
                    if not row:
                        self._send_json_response({"error": "Not found"}, status=404)
                        return
                    part_name = payload.get('part_name', row['part_name'])
                    quantity = payload.get('quantity', row['quantity'])
                    reorder_level = payload.get('reorder_level', row['reorder_level'])
                    execute_query("UPDATE inventory SET part_name=?, quantity=?, reorder_level=? WHERE id=?",
                                  (part_name, quantity, reorder_level, res_id))
                    self._send_json_response({"success": True})
                else:
                    self.send_error(404, "API Endpoint Not Found")
            except Exception as e:
                self._send_json_response({"error": str(e)}, status=500)
        else:
            self.send_error(400, "Bad Request")

    def handle_api_delete(self, path):
        parts = path.split('/')
        if len(parts) >= 4:
            resource = parts[2]
            res_id = parts[3]
            try:
                valid_resources = ['equipment', 'work_orders', 'inventory', 'users', 'maintenance_schedule', 'maintenance_records']
                if resource in valid_resources:
                    execute_query(f"DELETE FROM {resource} WHERE id=?", (res_id,))
                    self._send_json_response({"success": True})
                else:
                    self.send_error(404, "API Endpoint Not Found")
            except Exception as e:
                self._send_json_response({"error": str(e)}, status=500)
        else:
            self.send_error(400, "Bad Request")

if __name__ == "__main__":
    init_db()
    # Ensure current working directory is where server.py lives so it serves the static files correctly
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    handler = CMMSRequestHandler
    # For SPA routing, any missing file routes should use index.html
    # so we also handle that in do_GET above.
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"Backend API Server started at http://localhost:{PORT}")
        httpd.serve_forever()
