/**
 * Yisel Web - Main Application JavaScript
 * Healthcare Documentation Automation Tool
 * by Mario Clavero
 */

class YiselWebApp {
    constructor() {
        this.socket = null;
        this.currentLanguage = 'en';
        this.currentTheme = 'light';
        this.currentView = 'dashboard';
        this.accounts = [];
        this.patients = [];
        this.tasks = [];
        
        this.init();
    }
    
    init() {
        this.initializeSocket();
        this.setupEventListeners();
        this.loadSettings();
        this.showView('dashboard');
        this.loadDashboardData();
    }
    
    initializeSocket() {
        this.socket = io();
        
        this.socket.on('connect', () => {
            console.log('Connected to server');
            this.showNotification('Connected to Yisel server', 'success');
        });
        
        this.socket.on('disconnect', () => {
            console.log('Disconnected from server');
            this.showNotification('Disconnected from server', 'warning');
        });
        
        this.socket.on('browser_status', (data) => {
            this.updateBrowserStatus(data.connected);
        });
        
        this.socket.on('task_completed', (data) => {
            this.showNotification(`Task completed: ${data.type} for ${data.patient_name}`, 'success');
            this.refreshCurrentView();
        });
        
        this.socket.on('low_battery_warning', (data) => {
            this.showNotification(`Low battery warning: ${data.level}%`, 'warning');
        });
    }
    
    setupEventListeners() {
        // Navigation
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const view = e.currentTarget.dataset.view;
                this.showView(view);
            });
        });
        
        // Theme toggle
        document.getElementById('theme-toggle').addEventListener('click', () => {
            this.toggleTheme();
        });
        
        // Language toggle
        document.getElementById('language-toggle').addEventListener('click', () => {
            this.toggleLanguage();
        });
        
        // Dashboard actions
        document.getElementById('connect-browser').addEventListener('click', () => {
            this.connectBrowser();
        });
        
        document.getElementById('reconnect-browser').addEventListener('click', () => {
            this.reconnectBrowser();
        });
        
        document.getElementById('fetch-patients').addEventListener('click', () => {
            this.fetchPatients();
        });
        
        document.getElementById('view-tasks').addEventListener('click', () => {
            this.showView('tasks');
        });
        
        document.getElementById('manage-accounts').addEventListener('click', () => {
            this.showView('accounts');
        });
        
        // Account management
        document.getElementById('add-account').addEventListener('click', () => {
            this.showAccountForm();
        });
        
        document.getElementById('cancel-account').addEventListener('click', () => {
            this.hideAccountForm();
        });
        
        document.getElementById('account-form-element').addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveAccount();
        });
        
        // Refresh buttons
        document.getElementById('refresh-dashboard').addEventListener('click', () => {
            this.loadDashboardData();
        });
        
        document.getElementById('refresh-patients').addEventListener('click', () => {
            this.loadPatients();
        });
        
        document.getElementById('refresh-tasks').addEventListener('click', () => {
            this.loadTasks();
        });
        
        // Modal close
        document.querySelector('.modal-close').addEventListener('click', () => {
            this.hideModal();
        });
        
        document.getElementById('modal-overlay').addEventListener('click', (e) => {
            if (e.target === e.currentTarget) {
                this.hideModal();
            }
        });
        
        // Settings
        document.getElementById('theme-select').addEventListener('change', (e) => {
            this.setTheme(e.target.value);
        });
        
        document.getElementById('language-select').addEventListener('change', (e) => {
            this.setLanguage(e.target.value);
        });
    }
    
    showView(viewName) {
        // Hide all views
        document.querySelectorAll('.view').forEach(view => {
            view.classList.remove('active');
        });
        
        // Show selected view
        document.getElementById(`${viewName}-view`).classList.add('active');
        
        // Update navigation
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-view="${viewName}"]`).classList.add('active');
        
        this.currentView = viewName;
        
        // Load view-specific data
        switch (viewName) {
            case 'dashboard':
                this.loadDashboardData();
                break;
            case 'accounts':
                this.loadAccounts();
                break;
            case 'patients':
                this.loadPatients();
                break;
            case 'tasks':
                this.loadTasks();
                break;
        }
    }
    
    async loadDashboardData() {
        try {
            this.showLoading();
            
            // Load dashboard statistics
            const response = await fetch('/api/dashboard/stats');
            const stats = await response.json();
            
            // Update stat cards
            document.getElementById('tasks-today').textContent = stats.tasks_today;
            document.getElementById('tasks-week').textContent = stats.tasks_week;
            document.getElementById('total-patients').textContent = stats.total_patients;
            document.getElementById('success-rate').textContent = `${stats.success_rate}%`;
            
            // Check browser status
            this.checkBrowserStatus();
            
            this.hideLoading();
        } catch (error) {
            console.error('Failed to load dashboard data:', error);
            this.showNotification('Failed to load dashboard data', 'error');
            this.hideLoading();
        }
    }
    
    async checkBrowserStatus() {
        try {
            const response = await fetch('/api/browser/status');
            const data = await response.json();
            this.updateBrowserStatus(data.connected);
        } catch (error) {
            console.error('Failed to check browser status:', error);
        }
    }
    
    updateBrowserStatus(connected) {
        const statusElement = document.getElementById('browser-status');
        const indicator = statusElement.querySelector('.status-indicator');
        const text = statusElement.querySelector('span');
        
        if (connected) {
            indicator.classList.remove('disconnected');
            indicator.classList.add('connected');
            text.textContent = 'Connected to Kinnser ✔';
        } else {
            indicator.classList.remove('connected');
            indicator.classList.add('disconnected');
            text.textContent = 'Disconnected ❌';
        }
        
        // Update header status as well
        const headerStatus = document.getElementById('connection-status');
        const headerIndicator = headerStatus.querySelector('.status-indicator');
        const headerText = headerStatus.querySelector('span');
        
        if (connected) {
            headerIndicator.classList.remove('disconnected');
            headerIndicator.classList.add('connected');
            headerText.textContent = 'Detection Status: Connected to Kinnser ✔';
        } else {
            headerIndicator.classList.remove('connected');
            headerIndicator.classList.add('disconnected');
            headerText.textContent = 'Detection Status: Disconnected ❌';
        }
    }
    
    async connectBrowser() {
        try {
            this.showLoading();
            const response = await fetch('/api/browser/connect', {
                method: 'POST'
            });
            const data = await response.json();
            
            if (data.success) {
                this.showNotification('Browser connected successfully', 'success');
                this.updateBrowserStatus(true);
            } else {
                this.showNotification('Failed to connect browser', 'error');
            }
            
            this.hideLoading();
        } catch (error) {
            console.error('Failed to connect browser:', error);
            this.showNotification('Failed to connect browser', 'error');
            this.hideLoading();
        }
    }
    
    async reconnectBrowser() {
        this.showNotification('Reconnecting browser...', 'info');
        await this.connectBrowser();
    }
    
    async loadAccounts() {
        try {
            const response = await fetch('/api/accounts');
            this.accounts = await response.json();
            this.renderAccounts();
        } catch (error) {
            console.error('Failed to load accounts:', error);
            this.showNotification('Failed to load accounts', 'error');
        }
    }
    
    renderAccounts() {
        const container = document.getElementById('accounts-list');
        
        if (this.accounts.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-users fa-3x"></i>
                    <h3>No Accounts</h3>
                    <p>Add your first account to get started</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = this.accounts.map(account => `
            <div class="account-item">
                <div class="account-info">
                    <h4>${account.nickname}</h4>
                    <p>Username: ${account.username}</p>
                    <p>Notifications: ${account.enable_notifications ? 'Enabled' : 'Disabled'}</p>
                </div>
                <div class="account-actions">
                    <button class="action-btn" onclick="app.editAccount(${account.id})">
                        <i class="fas fa-edit"></i> Edit
                    </button>
                    <button class="action-btn" onclick="app.deleteAccount(${account.id})">
                        <i class="fas fa-trash"></i> Delete
                    </button>
                </div>
            </div>
        `).join('');
    }
    
    showAccountForm(account = null) {
        const form = document.getElementById('account-form');
        const title = document.getElementById('form-title');
        
        if (account) {
            title.textContent = 'Edit Account';
            document.getElementById('nickname').value = account.nickname;
            document.getElementById('username').value = account.username;
            document.getElementById('notification-topic').value = account.notification_topic || '';
            document.getElementById('enable-notifications').checked = account.enable_notifications;
        } else {
            title.textContent = 'Add New Account';
            document.getElementById('account-form-element').reset();
        }
        
        form.style.display = 'block';
    }
    
    hideAccountForm() {
        document.getElementById('account-form').style.display = 'none';
        document.getElementById('account-form-element').reset();
    }
    
    async saveAccount() {
        try {
            const formData = new FormData(document.getElementById('account-form-element'));
            const data = {
                nickname: formData.get('nickname'),
                username: formData.get('username'),
                password: formData.get('password'),
                notification_topic: formData.get('notification_topic'),
                enable_notifications: formData.has('enable_notifications')
            };
            
            const response = await fetch('/api/accounts', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showNotification('Account saved successfully', 'success');
                this.hideAccountForm();
                this.loadAccounts();
            } else {
                this.showNotification(result.error || 'Failed to save account', 'error');
            }
        } catch (error) {
            console.error('Failed to save account:', error);
            this.showNotification('Failed to save account', 'error');
        }
    }
    
    async loadPatients() {
        try {
            const response = await fetch('/api/patients');
            this.patients = await response.json();
            this.renderPatients();
        } catch (error) {
            console.error('Failed to load patients:', error);
            this.showNotification('Failed to load patients', 'error');
        }
    }
    
    renderPatients() {
        const container = document.getElementById('patients-list');
        
        if (this.patients.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-user-injured fa-3x"></i>
                    <h3>No Patients</h3>
                    <p>Fetch patients from Kinnser to get started</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = this.patients.map(patient => `
            <div class="patient-item" onclick="app.showPatientDetails('${patient.patient_key}')">
                <div class="patient-info">
                    <h4>${patient.name}</h4>
                    <p>Location: ${patient.location || 'Not set'}</p>
                    <p>Visits: ${patient.visits_data.length}</p>
                    <p>Last Updated: ${new Date(patient.last_updated).toLocaleDateString()}</p>
                </div>
            </div>
        `).join('');
    }
    
    async loadTasks() {
        try {
            const response = await fetch('/api/tasks');
            this.tasks = await response.json();
            this.renderTasks();
        } catch (error) {
            console.error('Failed to load tasks:', error);
            this.showNotification('Failed to load tasks', 'error');
        }
    }
    
    renderTasks() {
        const container = document.getElementById('tasks-list');
        
        if (this.tasks.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-tasks fa-3x"></i>
                    <h3>No Tasks</h3>
                    <p>No scheduled tasks found</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = this.tasks.map(task => `
            <div class="task-item">
                <div class="task-info">
                    <h4>${task.patient_name}</h4>
                    <p>Type: ${task.task_type}</p>
                    <p>Scheduled: ${new Date(task.run_datetime).toLocaleString()}</p>
                    <span class="task-status ${task.status}">${task.status}</span>
                </div>
            </div>
        `).join('');
    }
    
    async fetchPatients() {
        this.showNotification('Fetching patients from Kinnser...', 'info');
        // This would integrate with the actual patient fetching logic
        // For now, just show a placeholder message
        setTimeout(() => {
            this.showNotification('Patient fetching feature coming soon', 'info');
        }, 2000);
    }
    
    toggleTheme() {
        const newTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        this.setTheme(newTheme);
    }
    
    setTheme(theme) {
        this.currentTheme = theme;
        const body = document.getElementById('app-body');
        
        if (theme === 'dark') {
            body.classList.remove('light-theme');
            body.classList.add('dark-theme');
            document.getElementById('theme-text').textContent = 'Light Mode';
            document.querySelector('#theme-toggle i').className = 'fas fa-sun';
        } else {
            body.classList.remove('dark-theme');
            body.classList.add('light-theme');
            document.getElementById('theme-text').textContent = 'Dark Mode';
            document.querySelector('#theme-toggle i').className = 'fas fa-moon';
        }
        
        // Update settings select
        document.getElementById('theme-select').value = theme;
        
        // Save to localStorage
        localStorage.setItem('yisel-theme', theme);
    }
    
    toggleLanguage() {
        const newLanguage = this.currentLanguage === 'en' ? 'es' : 'en';
        this.setLanguage(newLanguage);
    }
    
    setLanguage(language) {
        this.currentLanguage = language;
        
        // Update language toggle button
        if (language === 'es') {
            document.getElementById('language-text').textContent = 'English';
        } else {
            document.getElementById('language-text').textContent = 'Español';
        }
        
        // Update all translatable elements
        this.updateLanguageStrings();
        
        // Update settings select
        document.getElementById('language-select').value = language;
        
        // Save to localStorage
        localStorage.setItem('yisel-language', language);
    }
    
    updateLanguageStrings() {
        const strings = this.getLanguageStrings();
        
        // Update header
        document.getElementById('welcome-text').textContent = strings.welcome;
        document.getElementById('author-text').textContent = strings.author;
        
        // Update navigation
        document.getElementById('nav-dashboard').textContent = strings.dashboard;
        document.getElementById('nav-accounts').textContent = 'Accounts'; // Add to language strings
        document.getElementById('nav-patients').textContent = strings.patients;
        document.getElementById('nav-tasks').textContent = strings.tasks;
        document.getElementById('nav-settings').textContent = strings.settings;
    }
    
    getLanguageStrings() {
        const languages = {
            en: {
                welcome: "Welcome to Yisel BOT",
                author: "by Mario Clavero",
                dashboard: "Dashboard",
                patients: "Patients",
                tasks: "Tasks",
                settings: "Settings"
            },
            es: {
                welcome: "Bienvenido a Yisel BOT",
                author: "por Mario Clavero",
                dashboard: "Panel",
                patients: "Pacientes",
                tasks: "Tareas",
                settings: "Configuración"
            }
        };
        
        return languages[this.currentLanguage] || languages.en;
    }
    
    loadSettings() {
        // Load theme
        const savedTheme = localStorage.getItem('yisel-theme') || 'light';
        this.setTheme(savedTheme);
        
        // Load language
        const savedLanguage = localStorage.getItem('yisel-language') || 'en';
        this.setLanguage(savedLanguage);
    }
    
    showNotification(message, type = 'info') {
        const container = document.getElementById('notifications');
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <p>${message}</p>
            </div>
        `;
        
        container.appendChild(notification);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);
        
        // Remove on click
        notification.addEventListener('click', () => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        });
    }
    
    showLoading() {
        document.getElementById('loading-overlay').style.display = 'flex';
    }
    
    hideLoading() {
        document.getElementById('loading-overlay').style.display = 'none';
    }
    
    showModal(title, content) {
        document.getElementById('modal-title').textContent = title;
        document.getElementById('modal-body').innerHTML = content;
        document.getElementById('modal-overlay').style.display = 'flex';
    }
    
    hideModal() {
        document.getElementById('modal-overlay').style.display = 'none';
    }
    
    refreshCurrentView() {
        this.showView(this.currentView);
    }
    
    // Placeholder methods for future implementation
    editAccount(id) {
        const account = this.accounts.find(acc => acc.id === id);
        if (account) {
            this.showAccountForm(account);
        }
    }
    
    deleteAccount(id) {
        if (confirm('Are you sure you want to delete this account?')) {
            // Implement delete functionality
            this.showNotification('Delete functionality coming soon', 'info');
        }
    }
    
    showPatientDetails(patientKey) {
        const patient = this.patients.find(p => p.patient_key === patientKey);
        if (patient) {
            this.showModal(`Patient Details - ${patient.name}`, `
                <div class="patient-details">
                    <p><strong>Name:</strong> ${patient.name}</p>
                    <p><strong>Location:</strong> ${patient.location || 'Not set'}</p>
                    <p><strong>Visits:</strong> ${patient.visits_data.length}</p>
                    <p><strong>Last Updated:</strong> ${new Date(patient.last_updated).toLocaleString()}</p>
                    <div class="patient-actions">
                        <button class="action-btn primary">Autofill Note</button>
                        <button class="action-btn">Schedule Sign</button>
                        <button class="action-btn">Change Location</button>
                    </div>
                </div>
            `);
        }
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new YiselWebApp();
});

// Add some utility CSS for empty states
const style = document.createElement('style');
style.textContent = `
    .empty-state {
        text-align: center;
        padding: 3rem;
        color: var(--subtitle-color);
    }
    
    .empty-state i {
        margin-bottom: 1rem;
        opacity: 0.5;
    }
    
    .empty-state h3 {
        margin-bottom: 0.5rem;
        color: var(--text-color);
    }
    
    .patient-details .patient-actions {
        margin-top: 1rem;
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
    }
    
    .notification-content {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
`;
document.head.appendChild(style);
