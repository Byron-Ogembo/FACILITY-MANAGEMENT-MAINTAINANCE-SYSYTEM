// Simple SPA Router
const App = {
    state: {
        user: null
    },
    
    init() {
        this.root = document.getElementById('app');
        
        // Listen to navigation events
        window.addEventListener('popstate', this.router.bind(this));
        
        // Handle clicks on internal links
        document.body.addEventListener('click', e => {
            if (e.target.matches('[data-link]')) {
                e.preventDefault();
                this.navigate(e.target.getAttribute('href'));
            }
        });
        
        // Check local storage for session
        const storedUser = localStorage.getItem('cmms_user');
        if (storedUser) {
            this.state.user = JSON.parse(storedUser);
        }
        
        this.router();
    },
    
    navigate(url) {
        history.pushState(null, null, url);
        this.router();
    },
    
    async router() {
        const path = window.location.pathname;
        
        // Not logged in and not on login page or landing
        if (!this.state.user && path !== '/login' && path !== '/') {
            this.navigate('/');
            return;
        }
        
        // Logged in but on login page or landing
        if (this.state.user && (path === '/login' || path === '/')) {
            this.navigate('/dashboard');
            return;
        }
        
        this.root.innerHTML = '<div style="display:flex; height:100vh; align-items:center; justify-content:center;">Loading...</div>';
        
        switch (path) {
            case '/':
                await this.renderLanding();
                break;
            case '/login':
                await this.renderLogin();
                break;
            case '/dashboard':
                await this.renderDashboard();
                break;
            case '/equipment':
                await this.renderEquipment();
                break;
            case '/work-orders':
                await this.renderWorkOrders();
                break;
            case '/inventory':
                await this.renderInventory();
                break;
            case '/reports':
                await this.renderReports();
                break;
            case '/contacts':
                await this.renderContacts();
                break;
            default:
                this.root.innerHTML = '<div class="login-container"><h2>404 - Page Not Found</h2></div>';
        }
    },
    
    // SVG Icons
    icons: {
        dashboard: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 3h7v9H3z M14 3h7v5h-7z M14 12h7v9h-7z M3 16h7v5H3z"/></svg>',
        equipment: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>',
        workOrders: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>',
        inventory: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>',
        reports: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>',
        contacts: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
    },
    
    renderLayout(contentHTML) {
        return `
            <div class="layout">
                <nav class="sidebar">
                    <div class="brand">TINDI CMMS</div>
                    <ul class="nav-links">
                        <li><a href="/dashboard" data-link class="${location.pathname === '/dashboard' ? 'active' : ''}">
                            <span style="margin-right: 12px; display: flex; align-items: center;">${this.icons.dashboard}</span> Dashboard
                        </a></li>
                        <li><a href="/equipment" data-link class="${location.pathname === '/equipment' ? 'active' : ''}">
                            <span style="margin-right: 12px; display: flex; align-items: center;">${this.icons.equipment}</span> Equipment
                        </a></li>
                        <li><a href="/work-orders" data-link class="${location.pathname === '/work-orders' ? 'active' : ''}">
                            <span style="margin-right: 12px; display: flex; align-items: center;">${this.icons.workOrders}</span> Work Orders
                        </a></li>
                        <li><a href="/inventory" data-link class="${location.pathname === '/inventory' ? 'active' : ''}">
                            <span style="margin-right: 12px; display: flex; align-items: center;">${this.icons.inventory}</span> Inventory
                        </a></li>
                        <li><a href="/reports" data-link class="${location.pathname === '/reports' ? 'active' : ''}">
                            <span style="margin-right: 12px; display: flex; align-items: center;">${this.icons.reports}</span> Reports
                        </a></li>
                        <li><a href="/contacts" data-link class="${location.pathname === '/contacts' ? 'active' : ''}">
                            <span style="margin-right: 12px; display: flex; align-items: center;">${this.icons.contacts}</span> Contact List
                        </a></li>
                    </ul>
                    <div class="sidebar-footer">
                        <div class="user-info">${this.state.user.name}</div>
                        <div class="user-role">${this.state.user.role}</div>
                        <button onclick="window.App.logout()" class="btn btn-secondary btn-sm btn-block">Sign Out</button>
                    </div>
                </nav>
                <main class="main-content">
                    ${contentHTML}
                </main>
                <div id="modal-container"></div>
            </div>
        `;
    },
    
    async api(endpoint, method = 'GET', data = null) {
        const options = { method, headers: {} };
        if (data) {
            options.headers['Content-Type'] = 'application/json';
            options.body = JSON.stringify(data);
        }
        try {
            const res = await fetch('/api' + endpoint, options);
            if (!res.ok) {
                if(res.status === 401) return {success: false, error: "Unauthorized"};
                throw new Error('API Error status ' + res.status);
            }
            return await res.json();
        } catch (err) {
            console.error(err);
            return null;
        }
    },
    
    async renderLanding() {
        this.root.innerHTML = `
            <div class="landing-page">
                <nav class="landing-nav glass-panel">
                    <div class="landing-brand">
                        <svg width="36" height="36" viewBox="0 0 24 24" fill="none" class="brand-logo"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" stroke="url(#paint0_linear)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><defs><linearGradient id="paint0_linear" x1="2" y1="2" x2="22" y2="22" gradientUnits="userSpaceOnUse"><stop stop-color="#f85149"/><stop offset="1" stop-color="#d29922"/></linearGradient></defs></svg>
                        <div class="brand-text">
                            <strong>NEXUS CMMS</strong>
                            <span>A CASE OF THE COCA-COLA COMPANY</span>
                        </div>
                    </div>
                    <ul class="landing-links">
                        <li><a href="#">System Features</a></li>
                        <li><a href="#">Equipment Management</a></li>
                        <li><a href="#">Reports & Analytics</a></li>
                        <li><a href="#">Case Study</a></li>
                    </ul>
                    <a href="/login" data-link class="btn btn-primary">See Live Demo</a>
                </nav>
                
                <header class="landing-hero" style="background-image: linear-gradient(135deg, rgba(13, 17, 23, 0.97) 0%, rgba(22, 27, 34, 0.9) 50%, rgba(59, 130, 246, 0.08) 100%), radial-gradient(ellipse at 70% 50%, rgba(59, 130, 246, 0.15) 0%, transparent 50%);">
                    <div class="hero-content">
                        <div class="badge badge-success hero-badge">
                            <span style="font-size:14px; margin-right:4px;">✓</span> Coca-Cola Company Implementation
                        </div>
                        <h1 class="hero-title">Maximize Equipment<br>Reliability &amp; Minimize<br>Downtime</h1>
                        <p class="hero-subtitle">Transform your factory maintenance operations with an intelligent management system designed to improve planning, tracking, and control of all maintenance activities.</p>
                        <div class="hero-actions">
                            <a href="/login" data-link class="btn btn-primary" style="padding: 14px 28px; font-size: 1.1rem;">Request a Demo &rarr;</a>
                            <button class="btn btn-glass" style="padding: 14px 28px; font-size: 1.1rem; display:flex; align-items:center; gap:8px;">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="white"><path d="M8 5v14l11-7z"/></svg>
                                View Case Study
                            </button>
                        </div>
                        <div class="hero-features">
                            <div class="feature-item"><span class="check">✓</span> Reduce downtime by 40%</div>
                            <div class="feature-item"><span class="check">✓</span> Cut maintenance costs by 25%</div>
                            <div class="feature-item"><span class="check">✓</span> Real-time monitoring</div>
                        </div>
                    </div>
                </header>
            </div>
        `;
    },

    async renderLogin() {
        this.root.innerHTML = `
            <div class="login-container">
                <div class="login-card glass-panel">
                    <h2>TINDI.</h2>
                    <p class="subtitle">Facility Maintenance Management</p>
                    <form id="login-form">
                        <div class="form-group">
                            <label>Email ID</label>
                            <input type="email" id="email" required placeholder="admin@cmms.com">
                        </div>
                        <div class="form-group">
                            <label>Password</label>
                            <input type="password" id="password" required placeholder="admin123">
                        </div>
                        <div id="login-error" style="color:var(--danger); margin-bottom:15px; font-size:0.9rem; display:none;"></div>
                        <button type="submit" class="btn btn-primary btn-block">Access System</button>
                    </form>
                </div>
            </div>
        `;
        
        document.getElementById('login-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            const btn = e.target.querySelector('button');
            const ogText = btn.innerHTML;
            btn.innerHTML = 'Authenticating...';
            btn.disabled = true;
            
            const res = await this.api('/login', 'POST', { email, password });
            
            if (res && res.success) {
                this.state.user = res.user;
                localStorage.setItem('cmms_user', JSON.stringify(res.user));
                this.navigate('/dashboard');
            } else {
                btn.innerHTML = ogText;
                btn.disabled = false;
                const errDiv = document.getElementById('login-error');
                errDiv.style.display = 'block';
                errDiv.textContent = res ? res.error : 'Network Error';
            }
        });
    },
    
    logout() {
        this.state.user = null;
        localStorage.removeItem('cmms_user');
        this.navigate('/login');
    },
    
    async renderDashboard() {
        const stats = await this.api('/dashboard/stats');
        
        const content = `
            <header class="page-header">
                <h1>Dashboard Overview</h1>
            </header>
            <div class="stats-grid">
                <div class="stat-card glass-panel">
                    <div class="stat-label">Total Equipment</div>
                    <div class="stat-value">${stats ? stats.total_equipment : 0}</div>
                </div>
                <div class="stat-card glass-panel">
                    <div class="stat-label">Pending Work Orders</div>
                    <div class="stat-value">${stats ? stats.pending_work_orders : 0}</div>
                </div>
                <div class="stat-card glass-panel">
                    <div class="stat-label">Completed Tasks</div>
                    <div class="stat-value">${stats ? stats.completed_work_orders : 0}</div>
                </div>
                <div class="stat-card glass-panel">
                    <div class="stat-label">Platform Status</div>
                    <div class="stat-value text-success">${stats ? stats.system_status : 'Offline'}</div>
                </div>
            </div>
            <div class="dashboard-content">
                <div class="glass-panel">
                    <h3 style="margin-bottom: 20px;">System Diagnostics</h3>
                    <p style="color: var(--text-secondary)">All systems operating normally. Database connected.</p>
                </div>
            </div>
        `;
        
        this.root.innerHTML = this.renderLayout(content);
    },
    
    async renderEquipment() {
        const equipment = await this.api('/equipment') || [];
        
        const tableRows = equipment.map(eq => `
            <tr>
                <td>#${eq.id.toString().padStart(4, '0')}</td>
                <td style="font-weight: 500">${eq.name}</td>
                <td><span class="badge ${eq.status === 'Active' ? 'badge-success' : 'badge-warning'}">${eq.status || 'Active'}</span></td>
                <td>${eq.location || '-'}</td>
                <td>${eq.category || '-'}</td>
                <td style="white-space: nowrap;">
                    <button class="btn btn-sm btn-secondary" onclick="window.App.openEquipmentModal(${eq.id})">Edit</button>
                    <button class="btn btn-sm btn-secondary" onclick="window.App.deleteEquipment(${eq.id})" style="margin-left: 6px; border-color: var(--danger); color: var(--danger);">Delete</button>
                </td>
            </tr>
        `).join('');
        
        const content = `
            <header class="page-header">
                <h1>Equipment Registry</h1>
                <button class="btn btn-primary" onclick="window.App.openEquipmentModal()">Register Equipment</button>
            </header>
            <div class="glass-panel" style="padding: 0; overflow: hidden">
                <div class="table-container">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Registry ID</th>
                                <th>Asset Name</th>
                                <th>Status</th>
                                <th>Location</th>
                                <th>Category</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${tableRows.length ? tableRows : '<tr><td colspan="6" style="text-align: center; padding: 40px; color: var(--text-secondary)">No assets registered in the system.</td></tr>'}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
        
        this.root.innerHTML = this.renderLayout(content);
    },
    
    async deleteEquipment(id) {
        if (!confirm('Are you sure you want to delete this equipment?')) return;
        const res = await this.api('/equipment/' + id, 'DELETE');
        if (res && res.success) {
            this.renderEquipment();
        } else {
            alert(res?.error || 'Failed to delete');
        }
    },
    
    async openEquipmentModal(editId) {
        let eq = null;
        if (editId) {
            eq = await this.api('/equipment/' + editId);
            if (eq && eq.error) eq = null;
        }
        const modal = `
            <div class="modal-backdrop" onclick="if(event.target===this) window.App.closeModal()">
                <div class="modal glass-panel">
                    <h2>${eq ? 'Edit Equipment' : 'Register New Equipment'}</h2>
                    <form id="eq-form" style="margin-top: 20px;">
                        <div class="form-group">
                            <label>Asset Name</label>
                            <input type="text" id="eq-name" required value="${eq ? (eq.name || '').replace(/"/g, '&quot;') : ''}">
                        </div>
                        <div class="form-group">
                            <label>Category</label>
                            <input type="text" id="eq-cat" required value="${eq ? (eq.category || '').replace(/"/g, '&quot;') : ''}">
                        </div>
                        <div class="form-group">
                            <label>Location</label>
                            <input type="text" id="eq-loc" required value="${eq ? (eq.location || '').replace(/"/g, '&quot;') : ''}">
                        </div>
                        <div class="form-group">
                            <label>Status</label>
                            <select id="eq-status" class="form-select">
                                <option value="Active" ${eq && eq.status === 'Active' ? 'selected' : ''}>Active</option>
                                <option value="Inactive" ${eq && eq.status === 'Inactive' ? 'selected' : ''}>Inactive</option>
                            </select>
                        </div>
                        <div style="display: flex; gap: 10px; margin-top: 30px;">
                            <button type="submit" class="btn btn-primary">${eq ? 'Update' : 'Save'} Asset</button>
                            <button type="button" class="btn btn-secondary" onclick="window.App.closeModal()">Cancel</button>
                        </div>
                    </form>
                </div>
            </div>
        `;
        document.getElementById('modal-container').innerHTML = modal;
        
        document.getElementById('eq-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const data = {
                name: document.getElementById('eq-name').value,
                category: document.getElementById('eq-cat').value,
                location: document.getElementById('eq-loc').value,
                status: document.getElementById('eq-status').value || 'Active'
            };
            if (eq) {
                const res = await this.api('/equipment/' + eq.id, 'PUT', data);
                if (res && res.success) {
                    this.closeModal();
                    this.renderEquipment();
                } else {
                    alert(res?.error || 'Error updating equipment');
                }
            } else {
                const res = await this.api('/equipment', 'POST', data);
                if (res && res.success) {
                    this.closeModal();
                    this.renderEquipment();
                } else {
                    alert('Error creating equipment');
                }
            }
        });
    },
    
    async renderWorkOrders() {
        const wos = await this.api('/work_orders') || [];
        
        const getBadgeClass = (s) => s === 'completed' ? 'badge-success' : (s === 'in_progress' ? 'badge-warning' : 'badge-danger');
        
        const tableRows = wos.map(wo => `
            <tr>
                <td>WO-${wo.id.toString().padStart(4, '0')}</td>
                <td style="font-weight: 500">${wo.equipment_name || 'Unassigned'}</td>
                <td>${wo.description || '-'}</td>
                <td><span class="badge ${getBadgeClass(wo.status || 'pending')}">${(wo.status || 'pending').replace('_', ' ')}</span></td>
                <td>${wo.date_created || '-'}</td>
                <td style="white-space: nowrap;">
                    ${wo.status !== 'completed' ? `<button class="btn btn-sm btn-primary" onclick="window.App.completeWorkOrder(${wo.id})">Complete</button> ` : ''}
                </td>
            </tr>
        `).join('');
        
        const content = `
            <header class="page-header">
                <h1>Maintenance Tasks</h1>
                <button class="btn btn-primary" onclick="window.App.openWorkOrderModal()">New Work Order</button>
            </header>
            <div class="glass-panel" style="padding: 0; overflow: hidden">
                <div class="table-container">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Order ID</th>
                                <th>Subject Asset</th>
                                <th>Task Description</th>
                                <th>Status</th>
                                <th>Issue Date</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${tableRows.length ? tableRows : '<tr><td colspan="6" style="text-align: center; padding: 40px; color: var(--text-secondary)">No active work orders.</td></tr>'}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
        
        this.root.innerHTML = this.renderLayout(content);
    },
    
    async completeWorkOrder(id) {
        const res = await this.api('/work_orders/' + id, 'PUT', { status: 'completed' });
        if (res && res.success) {
            this.renderWorkOrders();
        } else {
            alert(res?.error || 'Failed to complete work order');
        }
    },
    
    async openWorkOrderModal() {
        const equipment = await this.api('/equipment') || [];
        const users = await this.api('/users') || [];
        
        const eqOptions = equipment.map(e => `<option value="${e.id}">${e.name} (${e.location})</option>`).join('');
        const userOptions = users.map(u => `<option value="${u.id}">${u.name}</option>`).join('');
        
        const modal = `
            <div class="modal-backdrop" onclick="if(event.target===this) window.App.closeModal()">
                <div class="modal glass-panel">
                    <h2>Create Work Order</h2>
                    <form id="wo-form" style="margin-top: 20px;">
                        <div class="form-group">
                            <label>Equipment</label>
                            <select id="wo-eq" required class="form-select">
                                <option value="">Select Equipment...</option>
                                ${eqOptions}
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Assigned To</label>
                            <select id="wo-user" required class="form-select">
                                <option value="">Select Technician...</option>
                                ${userOptions}
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Description</label>
                            <textarea id="wo-desc" required rows="3" class="form-textarea"></textarea>
                        </div>
                        <div style="display: flex; gap: 10px; margin-top: 30px;">
                            <button type="submit" class="btn btn-primary">Create Order</button>
                            <button type="button" class="btn btn-secondary" onclick="window.App.closeModal()">Cancel</button>
                        </div>
                    </form>
                </div>
            </div>
        `;
        document.getElementById('modal-container').innerHTML = modal;
        
        document.getElementById('wo-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const data = {
                equipment_id: document.getElementById('wo-eq').value,
                assigned_to: document.getElementById('wo-user').value,
                description: document.getElementById('wo-desc').value,
                status: 'pending'
            };
            const res = await this.api('/work_orders', 'POST', data);
            if(res && res.success) {
                this.closeModal();
                this.renderWorkOrders();
            } else {
                alert('Error creating work order');
            }
        });
    },
    
    async renderInventory() {
        const parts = await this.api('/inventory') || [];
        
        const tableRows = parts.map(p => `
            <tr>
                <td>P-${p.id.toString().padStart(4, '0')}</td>
                <td style="font-weight: 500">${p.part_name}</td>
                <td>${p.quantity} Units</td>
                <td>${p.reorder_level} Units</td>
                <td>
                    ${p.quantity <= p.reorder_level 
                        ? '<span class="badge badge-danger">Low Stock Alert</span>' 
                        : '<span class="badge badge-success">Optimal</span>'}
                </td>
                <td style="white-space: nowrap;">
                    <button class="btn btn-sm btn-secondary" onclick="window.App.openInventoryModal(${p.id})">Edit</button>
                    <button class="btn btn-sm btn-secondary" onclick="window.App.deleteInventory(${p.id})" style="margin-left: 6px; border-color: var(--danger); color: var(--danger);">Delete</button>
                </td>
            </tr>
        `).join('');
        
        const content = `
            <header class="page-header">
                <h1>Parts Inventory</h1>
                <button class="btn btn-primary" onclick="window.App.openInventoryModal()">Add New Part</button>
            </header>
            <div class="glass-panel" style="padding: 0; overflow: hidden">
                <div class="table-container">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Part ID</th>
                                <th>Nomenclature</th>
                                <th>Stock Quantity</th>
                                <th>Restock Threshold</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${tableRows.length ? tableRows : '<tr><td colspan="6" style="text-align: center; padding: 40px; color: var(--text-secondary)">Inventory ledger is empty.</td></tr>'}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
        
        this.root.innerHTML = this.renderLayout(content);
    },
    
    async deleteInventory(id) {
        if (!confirm('Are you sure you want to delete this part?')) return;
        const res = await this.api('/inventory/' + id, 'DELETE');
        if (res && res.success) {
            this.renderInventory();
        } else {
            alert(res?.error || 'Failed to delete');
        }
    },
    
    async openInventoryModal(editId) {
        let part = null;
        if (editId) {
            part = await this.api('/inventory/' + editId);
            if (part && part.error) part = null;
        }
        const modal = `
            <div class="modal-backdrop" onclick="if(event.target===this) window.App.closeModal()">
                <div class="modal glass-panel">
                    <h2>${part ? 'Edit Part' : 'Add Inventory Part'}</h2>
                    <form id="inv-form" style="margin-top: 20px;">
                        <div class="form-group">
                            <label>Part Nomenclature</label>
                            <input type="text" id="inv-name" required value="${part ? (part.part_name || '').replace(/"/g, '&quot;') : ''}">
                        </div>
                        <div class="form-group">
                            <label>${part ? 'Quantity' : 'Initial Quantity'}</label>
                            <input type="number" id="inv-qty" required min="0" value="${part ? (part.quantity || 0) : 0}">
                        </div>
                        <div class="form-group">
                            <label>Reorder Threshold</label>
                            <input type="number" id="inv-reorder" required min="0" value="${part ? (part.reorder_level || 5) : 5}">
                        </div>
                        <div style="display: flex; gap: 10px; margin-top: 30px;">
                            <button type="submit" class="btn btn-primary">${part ? 'Update' : 'Save'} Part</button>
                            <button type="button" class="btn btn-secondary" onclick="window.App.closeModal()">Cancel</button>
                        </div>
                    </form>
                </div>
            </div>
        `;
        document.getElementById('modal-container').innerHTML = modal;
        
        document.getElementById('inv-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const data = {
                part_name: document.getElementById('inv-name').value,
                quantity: parseInt(document.getElementById('inv-qty').value) || 0,
                reorder_level: parseInt(document.getElementById('inv-reorder').value) || 0
            };
            if (part) {
                const res = await this.api('/inventory/' + part.id, 'PUT', data);
                if (res && res.success) {
                    this.closeModal();
                    this.renderInventory();
                } else {
                    alert(res?.error || 'Error updating part');
                }
            } else {
                const res = await this.api('/inventory', 'POST', data);
                if (res && res.success) {
                    this.closeModal();
                    this.renderInventory();
                } else {
                    alert('Error adding part');
                }
            }
        });
    },

    async renderReports() {
        // Fetch data for reports calculation
        const equipment = await this.api('/equipment') || [];
        const wos = await this.api('/work_orders') || [];
        
        // Calculate some basic mock metrics based on data
        let totalDowntimeTasks = wos.length;
        let completedWos = wos.filter(w => w.status === 'completed').length;
        let completionRate = totalDowntimeTasks ? Math.round((completedWos / totalDowntimeTasks) * 100) : 100;

        const content = `
            <header class="page-header">
                <h1>Analytics & Reports</h1>
            </header>
            
            <div class="stats-grid">
                <div class="stat-card glass-panel">
                    <div class="stat-label">Overall Equip. Eval (OEE)</div>
                    <div class="stat-value text-success">94.2%</div>
                </div>
                <div class="stat-card glass-panel">
                    <div class="stat-label">Task Completion Rate</div>
                    <div class="stat-value">${completionRate}%</div>
                </div>
                <div class="stat-card glass-panel">
                    <div class="stat-label">Mean Time to Repair (MTTR)</div>
                    <div class="stat-value">2.4 <span style="font-size: 1rem; color: var(--text-secondary)">hrs</span></div>
                </div>
                <div class="stat-card glass-panel">
                    <div class="stat-label">Mean Time Between Failures</div>
                    <div class="stat-value">124 <span style="font-size: 1rem; color: var(--text-secondary)">days</span></div>
                </div>
            </div>

            <div class="glass-panel" style="margin-top: 40px;">
                <h3 style="margin-bottom: 20px;">Downtime by Equipment Category</h3>
                <div style="height: 200px; display: flex; align-items: flex-end; gap: 20px; padding: 20px 0; border-bottom: 1px solid var(--panel-border)">
                    <!-- CSS Bar Chart mock -->
                    <div style="flex: 1; background: var(--accent-gradient); height: 80%; border-radius: 4px 4px 0 0; position: relative;">
                        <span style="position: absolute; bottom: -25px; width: 100%; text-align: center; font-size: 0.8rem; color: var(--text-secondary)">Line 1</span>
                    </div>
                    <div style="flex: 1; background: var(--warning); height: 40%; border-radius: 4px 4px 0 0; position: relative;">
                        <span style="position: absolute; bottom: -25px; width: 100%; text-align: center; font-size: 0.8rem; color: var(--text-secondary)">Packaging</span>
                    </div>
                    <div style="flex: 1; background: var(--success); height: 20%; border-radius: 4px 4px 0 0; position: relative;">
                        <span style="position: absolute; bottom: -25px; width: 100%; text-align: center; font-size: 0.8rem; color: var(--text-secondary)">Conveyors</span>
                    </div>
                    <div style="flex: 1; background: #8b5cf6; height: 60%; border-radius: 4px 4px 0 0; position: relative;">
                        <span style="position: absolute; bottom: -25px; width: 100%; text-align: center; font-size: 0.8rem; color: var(--text-secondary)">Motors</span>
                    </div>
                </div>
            </div>
        `;
        
        this.root.innerHTML = this.renderLayout(content);
    },

    async renderContacts() {
        const contacts = await this.api('/contacts') || [];
        
        const tableRows = contacts.map(c => `
            <tr>
                <td>C-${c.id.toString().padStart(4, '0')}</td>
                <td style="font-weight: 500">${c.name}</td>
                <td>${c.email}</td>
                <td>${c.organization || '-'}</td>
                <td><span class="badge badge-success">Active</span></td>
                <td style="white-space: nowrap;">
                    <button class="btn btn-sm btn-secondary" onclick="window.App.deleteContact(${c.id})" style="border-color: var(--danger); color: var(--danger);">Delete</button>
                </td>
            </tr>
        `).join('');
        
        const content = `
            <header class="page-header">
                <h1>Notification Contacts</h1>
                <button class="btn btn-primary" onclick="window.App.openContactModal()">Add New Contact</button>
            </header>
            <div class="glass-panel" style="padding: 0; overflow: hidden">
                <div class="table-container">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Contact ID</th>
                                <th>Name</th>
                                <th>Email Address</th>
                                <th>Organization</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${tableRows.length ? tableRows : '<tr><td colspan="6" style="text-align: center; padding: 40px; color: var(--text-secondary)">No external contacts registered.</td></tr>'}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
        
        this.root.innerHTML = this.renderLayout(content);
    },

    async openContactModal() {
        const modal = `
            <div class="modal-backdrop" onclick="if(event.target===this) window.App.closeModal()">
                <div class="modal glass-panel">
                    <h2>Add Notification Contact</h2>
                    <form id="contact-form" style="margin-top: 20px;">
                        <div class="form-group">
                            <label>Full Name</label>
                            <input type="text" id="contact-name" required placeholder="e.g. John Doe">
                        </div>
                        <div class="form-group">
                            <label>Email Address</label>
                            <input type="email" id="contact-email" required placeholder="manager@example.com">
                        </div>
                        <div class="form-group">
                            <label>Organization / Role</label>
                            <input type="text" id="contact-org" placeholder="e.g. Plant Manager">
                        </div>
                        <div style="display: flex; gap: 10px; margin-top: 30px;">
                            <button type="submit" class="btn btn-primary">Save Contact</button>
                            <button type="button" class="btn btn-secondary" onclick="window.App.closeModal()">Cancel</button>
                        </div>
                    </form>
                </div>
            </div>
        `;
        document.getElementById('modal-container').innerHTML = modal;
        
        document.getElementById('contact-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const data = {
                name: document.getElementById('contact-name').value,
                email: document.getElementById('contact-email').value,
                organization: document.getElementById('contact-org').value
            };
            const res = await this.api('/contacts', 'POST', data);
            if (res && res.success) {
                this.closeModal();
                this.renderContacts();
            } else {
                alert(res?.error || 'Error saving contact');
            }
        });
    },

    async deleteContact(id) {
        if (!confirm('Are you sure you want to remove this contact?')) return;
        const res = await this.api('/contacts/' + id, 'DELETE');
        if (res && res.success) {
            this.renderContacts();
        } else {
            alert('Error deleting contact');
        }
    },

    closeModal() {
        const container = document.getElementById('modal-container');
        if (container) container.innerHTML = '';
    }
};

window.App = App;
document.addEventListener('DOMContentLoaded', () => App.init());
