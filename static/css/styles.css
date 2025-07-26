ho/* Yisel Web - Modern Healthcare Automation Interface */

:root {
    /* Light Theme Variables */
    --primary-bg: #F5F6FA;
    --secondary-bg: #FFFFFF;
    --card-bg: #F5F6FA;
    --accent-color: #AEE6FF;
    --accent-color-2: #7AC7E6;
    --text-color: #181A1B;
    --outline-color: #F5F6FA;
    --highlight-text-color: #181A1B;
    --subtitle-color: #181A1B;
    --border-color: #E1E5E9;
    --shadow-color: rgba(0, 0, 0, 0.1);
    --success-color: #28a745;
    --warning-color: #ffc107;
    --danger-color: #dc3545;
    --info-color: #17a2b8;
    
    /* Typography */
    --header-font: "Segoe UI", -apple-system, BlinkMacSystemFont, sans-serif;
    --body-font: "Segoe UI", -apple-system, BlinkMacSystemFont, sans-serif;
    
    /* Spacing */
    --border-radius: 8px;
    --padding: 16px;
    --margin: 16px;
    
    /* Transitions */
    --transition: all 0.3s ease;
}

/* Dark Theme Variables */
.dark-theme {
    --primary-bg: #1E1E1E;
    --secondary-bg: #2D2D2D;
    --card-bg: #1E1E1E;
    --accent-color: #0078D4;
    --accent-color-2: #106EBE;
    --text-color: #FFFFFF;
    --outline-color: #404040;
    --highlight-text-color: #FFFFFF;
    --subtitle-color: #CCCCCC;
    --border-color: #404040;
    --shadow-color: rgba(0, 0, 0, 0.3);
}

/* Reset and Base Styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: var(--body-font);
    background-color: var(--primary-bg);
    color: var(--text-color);
    line-height: 1.6;
    transition: var(--transition);
}

/* Header Styles */
.header {
    background-color: var(--secondary-bg);
    border-bottom: 1px solid var(--border-color);
    padding: var(--padding);
    box-shadow: 0 2px 4px var(--shadow-color);
}

.header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    max-width: 1200px;
    margin: 0 auto;
}

.logo-section {
    display: flex;
    align-items: center;
    gap: var(--margin);
}

.logo-icon {
    font-size: 2.5rem;
    color: var(--accent-color);
}

.logo-text h1 {
    font-size: 1.8rem;
    font-weight: bold;
    color: var(--text-color);
    margin-bottom: 0.25rem;
}

.logo-text p {
    font-size: 0.9rem;
    color: var(--subtitle-color);
    font-style: italic;
}

.header-controls {
    display: flex;
    align-items: center;
    gap: var(--margin);
}

.control-btn {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    background-color: var(--accent-color);
    color: var(--text-color);
    border: none;
    border-radius: var(--border-radius);
    cursor: pointer;
    transition: var(--transition);
    font-size: 0.9rem;
    font-weight: 500;
}

.control-btn:hover {
    background-color: var(--accent-color-2);
    transform: translateY(-1px);
}

.connection-status {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    background-color: var(--card-bg);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    font-size: 0.9rem;
}

.status-indicator {
    font-size: 0.8rem;
}

.status-indicator.connected {
    color: var(--success-color);
}

.status-indicator.disconnected {
    color: var(--danger-color);
}

/* Navigation Styles */
.navigation {
    background-color: var(--secondary-bg);
    border-bottom: 1px solid var(--border-color);
    padding: 0 var(--padding);
}

.nav-content {
    display: flex;
    max-width: 1200px;
    margin: 0 auto;
    gap: 2px;
}

.nav-btn {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 1rem 1.5rem;
    background: none;
    border: none;
    color: var(--text-color);
    cursor: pointer;
    transition: var(--transition);
    border-radius: var(--border-radius) var(--border-radius) 0 0;
    position: relative;
    font-size: 0.95rem;
}

.nav-btn:hover {
    background-color: var(--card-bg);
}

.nav-btn.active {
    background-color: var(--accent-color);
    color: var(--highlight-text-color);
}

.nav-btn.active::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 3px;
    background-color: var(--accent-color-2);
}

/* Main Content Styles */
.main-content {
    max-width: 1200px;
    margin: 0 auto;
    padding: var(--padding);
    min-height: calc(100vh - 200px);
}

.view {
    display: none;
    animation: fadeIn 0.3s ease-in-out;
}

.view.active {
    display: block;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.view-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
    padding-bottom: 1rem;
    border-bottom: 2px solid var(--border-color);
}

.view-header h2 {
    font-size: 2rem;
    color: var(--text-color);
    font-weight: 600;
}

.header-actions {
    display: flex;
    gap: 1rem;
}

/* Button Styles */
.action-btn {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem 1.5rem;
    background-color: var(--card-bg);
    color: var(--text-color);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    cursor: pointer;
    transition: var(--transition);
    font-size: 0.95rem;
    font-weight: 500;
    text-decoration: none;
}

.action-btn:hover {
    background-color: var(--accent-color);
    transform: translateY(-1px);
    box-shadow: 0 4px 8px var(--shadow-color);
}

.action-btn.primary {
    background-color: var(--accent-color);
    color: var(--highlight-text-color);
}

.action-btn.primary:hover {
    background-color: var(--accent-color-2);
}

.action-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
}

/* Dashboard Styles */
.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
}

.stat-card {
    background-color: var(--secondary-bg);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    padding: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    transition: var(--transition);
    box-shadow: 0 2px 4px var(--shadow-color);
}

.stat-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px var(--shadow-color);
}

.stat-icon {
    font-size: 2.5rem;
    color: var(--accent-color);
    width: 60px;
    text-align: center;
}

.stat-content h3 {
    font-size: 2rem;
    font-weight: bold;
    color: var(--text-color);
    margin-bottom: 0.25rem;
}

.stat-content p {
    color: var(--subtitle-color);
    font-size: 0.9rem;
}

.dashboard-content {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: 2rem;
}

.dashboard-section {
    background-color: var(--secondary-bg);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    padding: 1.5rem;
    box-shadow: 0 2px 4px var(--shadow-color);
}

.dashboard-section h3 {
    margin-bottom: 1rem;
    color: var(--text-color);
    font-size: 1.2rem;
}

.browser-controls {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.browser-controls .action-btn {
    justify-content: center;
}

.browser-status {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem;
    background-color: var(--card-bg);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    font-size: 0.9rem;
}

.quick-actions {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 1rem;
}

/* Form Styles */
.form-group {
    margin-bottom: 1rem;
}

.form-group label {
    display: block;
    margin-bottom: 0.5rem;
    color: var(--text-color);
    font-weight: 500;
}

.form-group input,
.form-group select,
.form-group textarea {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    background-color: var(--secondary-bg);
    color: var(--text-color);
    font-size: 0.95rem;
    transition: var(--transition);
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
    outline: none;
    border-color: var(--accent-color);
    box-shadow: 0 0 0 3px rgba(174, 230, 255, 0.1);
}

.form-actions {
    display: flex;
    gap: 1rem;
    margin-top: 1.5rem;
}

/* Account Management */
.accounts-container {
    display: grid;
    gap: 2rem;
}

.account-form {
    background-color: var(--secondary-bg);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    padding: 1.5rem;
    box-shadow: 0 2px 4px var(--shadow-color);
}

.account-form h3 {
    margin-bottom: 1rem;
    color: var(--text-color);
}

.accounts-list {
    display: grid;
    gap: 1rem;
}

.account-item {
    background-color: var(--secondary-bg);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    padding: 1rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    transition: var(--transition);
}

.account-item:hover {
    box-shadow: 0 2px 8px var(--shadow-color);
}

.account-info h4 {
    color: var(--text-color);
    margin-bottom: 0.25rem;
}

.account-info p {
    color: var(--subtitle-color);
    font-size: 0.9rem;
}

.account-actions {
    display: flex;
    gap: 0.5rem;
}

.account-actions .action-btn {
    padding: 0.5rem 1rem;
    font-size: 0.85rem;
}

/* Patient and Task Lists */
.patients-list,
.tasks-list {
    display: grid;
    gap: 1rem;
}

.patient-item,
.task-item {
    background-color: var(--secondary-bg);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    padding: 1rem;
    transition: var(--transition);
    cursor: pointer;
}

.patient-item:hover,
.task-item:hover {
    box-shadow: 0 2px 8px var(--shadow-color);
    transform: translateY(-1px);
}

.patient-info h4,
.task-info h4 {
    color: var(--text-color);
    margin-bottom: 0.5rem;
}

.patient-info p,
.task-info p {
    color: var(--subtitle-color);
    font-size: 0.9rem;
    margin-bottom: 0.25rem;
}

.task-status {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 500;
    text-transform: uppercase;
}

.task-status.scheduled {
    background-color: var(--info-color);
    color: white;
}

.task-status.completed {
    background-color: var(--success-color);
    color: white;
}

.task-status.failed {
    background-color: var(--danger-color);
    color: white;
}

/* Settings */
.settings-container {
    display: grid;
    gap: 2rem;
}

.settings-section {
    background-color: var(--secondary-bg);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    padding: 1.5rem;
    box-shadow: 0 2px 4px var(--shadow-color);
}

.settings-section h3 {
    margin-bottom: 1rem;
    color: var(--text-color);
}

.setting-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem 0;
    border-bottom: 1px solid var(--border-color);
}

.setting-item:last-child {
    border-bottom: none;
}

.setting-item label {
    color: var(--text-color);
    font-weight: 500;
}

.toggle-btn {
    padding: 0.5rem 1rem;
    background-color: var(--card-bg);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    cursor: pointer;
    transition: var(--transition);
    font-weight: 500;
}

.toggle-btn.active {
    background-color: var(--success-color);
    color: white;
    border-color: var(--success-color);
}

/* Notifications */
.notifications-container {
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 1000;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.notification {
    background-color: var(--secondary-bg);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    padding: 1rem;
    box-shadow: 0 4px 12px var(--shadow-color);
    max-width: 300px;
    animation: slideIn 0.3s ease-out;
}

.notification.success {
    border-left: 4px solid var(--success-color);
}

.notification.warning {
    border-left: 4px solid var(--warning-color);
}

.notification.error {
    border-left: 4px solid var(--danger-color);
}

.notification.info {
    border-left: 4px solid var(--info-color);
}

@keyframes slideIn {
    from { transform: translateX(100%); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
}

/* Loading Overlay */
.loading-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 9999;
}

.loading-spinner {
    background-color: var(--secondary-bg);
    border-radius: var(--border-radius);
    padding: 2rem;
    text-align: center;
    box-shadow: 0 4px 20px var(--shadow-color);
}

.loading-spinner i {
    font-size: 2rem;
    color: var(--accent-color);
    margin-bottom: 1rem;
}

.loading-spinner p {
    color: var(--text-color);
    font-size: 1.1rem;
}

/* Modal Styles */
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 9998;
}

.modal {
    background-color: var(--secondary-bg);
    border-radius: var(--border-radius);
    box-shadow: 0 4px 20px var(--shadow-color);
    max-width: 90vw;
    max-height: 90vh;
    overflow: hidden;
    animation: modalIn 0.3s ease-out;
}

@keyframes modalIn {
    from { transform: scale(0.9); opacity: 0; }
    to { transform: scale(1); opacity: 1; }
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 1.5rem;
    border-bottom: 1px solid var(--border-color);
}

.modal-header h3 {
    color: var(--text-color);
    margin: 0;
}

.modal-close {
    background: none;
    border: none;
    font-size: 1.5rem;
    color: var(--text-color);
    cursor: pointer;
    padding: 0;
    width: 30px;
    height: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    transition: var(--transition);
}

.modal-close:hover {
    background-color: var(--card-bg);
}

.modal-body {
    padding: 1.5rem;
    max-height: 70vh;
    overflow-y: auto;
}

/* Responsive Design */
@media (max-width: 768px) {
    .header-content {
        flex-direction: column;
        gap: 1rem;
    }
    
    .nav-content {
        flex-wrap: wrap;
        justify-content: center;
    }
    
    .nav-btn {
        padding: 0.75rem 1rem;
        font-size: 0.9rem;
    }
    
    .stats-grid {
        grid-template-columns: 1fr;
    }
    
    .dashboard-content {
        grid-template-columns: 1fr;
    }
    
    .quick-actions {
        grid-template-columns: 1fr;
    }
    
    .form-actions {
        flex-direction: column;
    }
    
    .account-item {
        flex-direction: column;
        align-items: flex-start;
        gap: 1rem;
    }
    
    .setting-item {
        flex-direction: column;
        align-items: flex-start;
        gap: 0.5rem;
    }
}

@media (max-width: 480px) {
    .main-content {
        padding: 0.5rem;
    }
    
    .view-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 1rem;
    }
    
    .header-actions {
        width: 100%;
        justify-content: flex-start;
    }
    
    .notifications-container {
        left: 10px;
        right: 10px;
        top: 10px;
    }
    
    .notification {
        max-width: none;
    }
}
