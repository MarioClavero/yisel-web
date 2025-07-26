#!/usr/bin/env python3
"""
Yisel Web - Healthcare Documentation Automation Tool
Web-based version of Yisel BOT by Mario Clavero
"""

from flask import Flask, render_template, request, jsonify, session, send_from_directory
from flask_socketio import SocketIO, emit
import os
import json
import datetime
import threading
import time
import uuid
from cryptography.fernet import Fernet
import sqlite3
import psutil
import requests
import base64
from PIL import Image, ImageDraw
from io import BytesIO

# Import our custom modules
from automation_engine import AutomationEngine
from notification_system import NotificationManager, SystemMonitor, TaskNotificationHandler, AlertSystem, DEFAULT_ALERT_RULES

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'yisel-web-secret-key-change-in-production')
socketio = SocketIO(app, cors_allowed_origins="*")

# Global variables
automation_engine = AutomationEngine()
notification_manager = None
system_monitor = None
task_notification_handler = None
alert_system = None
current_patients = []
scheduled_tasks = {}
task_monitor = None

# Configuration
DEBUGGING_PORT = os.environ.get('DEBUGGING_PORT', '9222')
LOW_BATTERY_THRESHOLD = int(os.environ.get('LOW_BATTERY_THRESHOLD', '20'))
IPHONE_USER_AGENT = "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"

# Language strings
LANGUAGES = {
    "en": {
        "welcome": "Welcome to Yisel BOT",
        "author": "by Mario Clavero",
        "select_account": "Select Account:",
        "manage_accounts": "Manage Accounts",
        "launch_login": "Launch & Login",
        "fetch_patients": "Fetch Patients",
        "status_connected": "Detection Status: Connected to Kinnser ✔",
        "status_disconnected": "Detection Status: Disconnected ❌",
        "force_reconnect": "Force Re-connect",
        "auto_reopen_on": "Auto Re-Open: ON",
        "auto_reopen_off": "Auto Re-Open: OFF",
        "minimize_tray": "Minimize to Background",
        "translate_button": "Español",
        "theme_button_dark": "Dark Mode",
        "theme_button_light": "Light Mode",
        "dashboard": "Dashboard",
        "patients": "Patients",
        "tasks": "Tasks",
        "settings": "Settings"
    },
    "es": {
        "welcome": "Bienvenido a Yisel BOT",
        "author": "por Mario Clavero",
        "select_account": "Seleccionar Cuenta:",
        "manage_accounts": "Gestionar Cuentas",
        "launch_login": "Iniciar & Conectar",
        "fetch_patients": "Obtener Pacientes",
        "status_connected": "Estado de Detección: Conectado a Kinnser ✔",
        "status_disconnected": "Estado de Detección: Desconectado ❌",
        "force_reconnect": "Forzar Reconexión",
        "auto_reopen_on": "Auto Re-Abrir: ACTIVADO",
        "auto_reopen_off": "Auto Re-Abrir: DESACTIVADO",
        "minimize_tray": "Minimizar al Fondo",
        "translate_button": "English",
        "theme_button_dark": "Modo Oscuro",
        "theme_button_light": "Modo Claro",
        "dashboard": "Panel",
        "patients": "Pacientes",
        "tasks": "Tareas",
        "settings": "Configuración"
    }
}

class DatabaseManager:
    def __init__(self, db_path=None):
        # Use Railway-compatible database path
        if db_path is None:
            if os.environ.get('RAILWAY_ENVIRONMENT'):
                # Railway environment - use /tmp for writable storage
                self.db_path = "/tmp/yisel_web.db"
            else:
                # Local environment
                self.db_path = "yisel_web.db"
        else:
            self.db_path = db_path
        
        try:
            self.init_database()
        except Exception as e:
            print(f"Database initialization error: {e}")
            # Fallback to in-memory database if file creation fails
            self.db_path = ":memory:"
            self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Accounts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nickname TEXT UNIQUE NOT NULL,
                username TEXT NOT NULL,
                password_encrypted TEXT NOT NULL,
                notification_topic TEXT,
                signature_data TEXT,
                enable_notifications BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Patients table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_key TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                location TEXT,
                visits_data TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Scheduled tasks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scheduled_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT UNIQUE NOT NULL,
                patient_key TEXT NOT NULL,
                task_type TEXT NOT NULL,
                run_datetime TEXT NOT NULL,
                status TEXT DEFAULT 'scheduled',
                task_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)

# Initialize database
db = DatabaseManager()

# Initialize notification and monitoring systems
def init_systems():
    global notification_manager, system_monitor, task_notification_handler, alert_system
    
    notification_manager = NotificationManager(socketio)
    system_monitor = SystemMonitor(notification_manager, automation_engine)
    task_notification_handler = TaskNotificationHandler(notification_manager)
    alert_system = AlertSystem(notification_manager)
    
    # Add default alert rules
    for rule in DEFAULT_ALERT_RULES:
        alert_system.add_alert_rule(rule)
    
    # Start monitoring
    system_monitor.start_monitoring()

# Initialize systems
init_systems()

# Remove old BrowserManager class - now using AutomationEngine

class TaskScheduler:
    def __init__(self):
        self.running = True
        self.thread = threading.Thread(target=self.run_scheduler)
        self.thread.daemon = True
        self.thread.start()
    
    def run_scheduler(self):
        """Main scheduler loop"""
        while self.running:
            try:
                self.check_scheduled_tasks()
                time.sleep(30)  # Check every 30 seconds
            except Exception as e:
                print(f"Scheduler error: {e}")
                time.sleep(60)
    
    def check_scheduled_tasks(self):
        """Check for tasks that need to be executed"""
        conn = db.get_connection()
        cursor = conn.cursor()
        
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        
        cursor.execute('''
            SELECT * FROM scheduled_tasks 
            WHERE status = 'scheduled' AND run_datetime <= ?
        ''', (current_time,))
        
        tasks = cursor.fetchall()
        
        for task in tasks:
            try:
                self.execute_task(task)
                # Mark as completed
                cursor.execute('''
                    UPDATE scheduled_tasks SET status = 'completed' WHERE id = ?
                ''', (task[0],))
                conn.commit()
            except Exception as e:
                print(f"Task execution error: {e}")
                cursor.execute('''
                    UPDATE scheduled_tasks SET status = 'failed' WHERE id = ?
                ''', (task[0],))
                conn.commit()
        
        conn.close()
    
    def execute_task(self, task):
        """Execute a scheduled task"""
        task_type = task[3]  # task_type column
        task_data = json.loads(task[6]) if task[6] else {}
        
        if task_type == 'sign':
            self.execute_sign_task(task_data)
        elif task_type == 'autofill':
            self.execute_autofill_task(task_data)
        
        # Emit task completion to connected clients
        socketio.emit('task_completed', {
            'task_id': task[1],
            'type': task_type,
            'status': 'completed'
        })
    
    def execute_sign_task(self, task_data):
        """Execute a sign task"""
        # Implementation for signing task
        pass
    
    def execute_autofill_task(self, task_data):
        """Execute an autofill task"""
        # Implementation for autofill task
        pass
    
    def stop(self):
        """Stop the scheduler"""
        self.running = False

task_scheduler = TaskScheduler()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/accounts', methods=['GET'])
def get_accounts():
    """Get all accounts"""
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, nickname, username, notification_topic, enable_notifications FROM accounts')
    accounts = cursor.fetchall()
    conn.close()
    
    return jsonify([{
        'id': acc[0],
        'nickname': acc[1],
        'username': acc[2],
        'notification_topic': acc[3],
        'enable_notifications': bool(acc[4])
    } for acc in accounts])

@app.route('/api/accounts', methods=['POST'])
def add_account():
    """Add a new account"""
    data = request.json
    
    # Encrypt password
    key = Fernet.generate_key()
    cipher_suite = Fernet(key)
    encrypted_password = cipher_suite.encrypt(data['password'].encode())
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO accounts (nickname, username, password_encrypted, notification_topic, 
                                signature_data, enable_notifications)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            data['nickname'],
            data['username'],
            base64.b64encode(key + encrypted_password).decode(),
            data.get('notification_topic', ''),
            data.get('signature_data', ''),
            data.get('enable_notifications', False)
        ))
        conn.commit()
        return jsonify({'success': True})
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'error': 'Account nickname already exists'})
    finally:
        conn.close()

@app.route('/api/browser/status')
def browser_status():
    """Get browser connection status"""
    return jsonify({
        'connected': automation_engine.is_connected,
        'status': 'Connected to Kinnser ✔' if automation_engine.is_connected else 'Disconnected ❌'
    })

@app.route('/api/browser/connect', methods=['POST'])
def connect_browser():
    """Connect to browser"""
    success = automation_engine.setup_browser()
    return jsonify({'success': success, 'connected': automation_engine.is_connected})

@app.route('/api/patients')
def get_patients():
    """Get all patients"""
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM patients ORDER BY name')
    patients = cursor.fetchall()
    conn.close()
    
    return jsonify([{
        'id': p[0],
        'patient_key': p[1],
        'name': p[2],
        'location': p[3],
        'visits_data': json.loads(p[4]) if p[4] else [],
        'last_updated': p[5]
    } for p in patients])

@app.route('/api/tasks')
def get_tasks():
    """Get all scheduled tasks"""
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT st.*, p.name as patient_name 
        FROM scheduled_tasks st 
        LEFT JOIN patients p ON st.patient_key = p.patient_key 
        ORDER BY st.run_datetime
    ''')
    tasks = cursor.fetchall()
    conn.close()
    
    return jsonify([{
        'id': t[0],
        'task_id': t[1],
        'patient_key': t[2],
        'patient_name': t[8] if len(t) > 8 else 'Unknown',
        'task_type': t[3],
        'run_datetime': t[4],
        'status': t[5],
        'task_data': json.loads(t[6]) if t[6] else {},
        'created_at': t[7]
    } for t in tasks])

@app.route('/api/dashboard/stats')
def get_dashboard_stats():
    """Get dashboard statistics"""
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # Count tasks for today
    today = datetime.date.today().strftime('%Y-%m-%d')
    cursor.execute('''
        SELECT COUNT(*) FROM scheduled_tasks 
        WHERE date(run_datetime) = ? AND status = 'scheduled'
    ''', (today,))
    tasks_today = cursor.fetchone()[0]
    
    # Count tasks for this week
    week_start = (datetime.date.today() - datetime.timedelta(days=datetime.date.today().weekday())).strftime('%Y-%m-%d')
    cursor.execute('''
        SELECT COUNT(*) FROM scheduled_tasks 
        WHERE date(run_datetime) >= ? AND status = 'scheduled'
    ''', (week_start,))
    tasks_week = cursor.fetchone()[0]
    
    # Count total patients
    cursor.execute('SELECT COUNT(*) FROM patients')
    total_patients = cursor.fetchone()[0]
    
    # Count completed tasks
    cursor.execute('SELECT COUNT(*) FROM scheduled_tasks WHERE status = "completed"')
    completed_tasks = cursor.fetchone()[0]
    
    # Calculate success rate
    cursor.execute('SELECT COUNT(*) FROM scheduled_tasks WHERE status IN ("completed", "failed")')
    total_executed = cursor.fetchone()[0]
    success_rate = (completed_tasks / total_executed * 100) if total_executed > 0 else 100.0
    
    conn.close()
    
    return jsonify({
        'tasks_today': tasks_today,
        'tasks_week': tasks_week,
        'total_patients': total_patients,
        'completed_tasks': completed_tasks,
        'success_rate': round(success_rate, 1),
        'time_saved_hours': completed_tasks * 0.25,
        'browser_connected': automation_engine.is_connected
    })

# New advanced API endpoints
@app.route('/api/patients/fetch', methods=['POST'])
def fetch_patients():
    """Fetch patients from Kinnser"""
    try:
        if not automation_engine.is_connected:
            return jsonify({'success': False, 'error': 'Browser not connected'})
        
        # Get account credentials
        data = request.json
        account_id = data.get('account_id')
        
        if not account_id:
            return jsonify({'success': False, 'error': 'Account ID required'})
        
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT username, password_encrypted FROM accounts WHERE id = ?', (account_id,))
        account = cursor.fetchone()
        
        if not account:
            return jsonify({'success': False, 'error': 'Account not found'})
        
        # Decrypt password
        encrypted_data = base64.b64decode(account[1])
        key = encrypted_data[:44]  # Fernet key is 44 bytes when base64 encoded
        encrypted_password = encrypted_data[44:]
        cipher_suite = Fernet(key)
        password = cipher_suite.decrypt(encrypted_password).decode()
        
        # Login and fetch patients
        if automation_engine.login_to_kinnser(account[0], password):
            patients = automation_engine.fetch_patients()
            
            # Store patients in database
            for patient in patients:
                cursor.execute('''
                    INSERT OR REPLACE INTO patients (patient_key, name, location, visits_data, last_updated)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    patient['patient_key'],
                    patient['name'],
                    patient.get('location'),
                    json.dumps(patient.get('visits_data', [])),
                    datetime.datetime.now().isoformat()
                ))
            
            conn.commit()
            conn.close()
            
            notification_manager.broadcast_notification(
                'Patients Fetched',
                f'Successfully fetched {len(patients)} patients from Kinnser',
                'success'
            )
            
            return jsonify({'success': True, 'count': len(patients)})
        else:
            conn.close()
            return jsonify({'success': False, 'error': 'Login failed'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/patients/<patient_key>/visits')
def get_patient_visits(patient_key):
    """Get visits for a specific patient"""
    try:
        visits = automation_engine.get_patient_visits(patient_key)
        
        # Update patient visits in database
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE patients SET visits_data = ?, last_updated = ?
            WHERE patient_key = ?
        ''', (json.dumps(visits), datetime.datetime.now().isoformat(), patient_key))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'visits': visits})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/signature')
def signature_canvas():
    """Serve signature canvas page"""
    return render_template('signature_canvas.html')

@app.route('/api/signature/save', methods=['POST'])
def save_signature():
    """Save signature data"""
    try:
        data = request.json
        account_id = data.get('account_id')
        signature_data = data.get('signature_data')
        
        if not account_id or not signature_data:
            return jsonify({'success': False, 'error': 'Missing required data'})
        
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE accounts SET signature_data = ? WHERE id = ?
        ''', (json.dumps(signature_data), account_id))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/tasks/schedule', methods=['POST'])
def schedule_task():
    """Schedule a new task"""
    try:
        data = request.json
        task_id = str(uuid.uuid4())
        
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO scheduled_tasks (task_id, patient_key, task_type, run_datetime, task_data)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            task_id,
            data['patient_key'],
            data['task_type'],
            data['run_datetime'],
            json.dumps(data.get('task_data', {}))
        ))
        conn.commit()
        conn.close()
        
        # Send notification
        task_notification_handler.notify_task_scheduled('system', {
            'patient_name': data.get('patient_name', 'Unknown'),
            'task_type': data['task_type'],
            'run_datetime': data['run_datetime']
        })
        
        return jsonify({'success': True, 'task_id': task_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/tasks/<task_id>/cancel', methods=['POST'])
def cancel_task(task_id):
    """Cancel a scheduled task"""
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE scheduled_tasks SET status = 'cancelled' WHERE task_id = ?
        ''', (task_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/patients/<patient_key>/location', methods=['POST'])
def change_patient_location(patient_key):
    """Change patient location"""
    try:
        data = request.json
        location_data = data.get('location_data', {})
        
        success = automation_engine.change_patient_location(patient_key, location_data)
        
        if success:
            # Update in database
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE patients SET location = ? WHERE patient_key = ?
            ''', (json.dumps(location_data), patient_key))
            conn.commit()
            conn.close()
            
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Location change failed'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/tasks/execute', methods=['POST'])
def execute_task_now():
    """Execute a task immediately"""
    try:
        data = request.json
        task_type = data.get('task_type')
        task_data = data.get('task_data', {})
        
        if task_type == 'autofill':
            success = automation_engine.execute_autofill_task(task_data)
        elif task_type == 'sign':
            success = automation_engine.execute_sign_task(task_data)
        else:
            return jsonify({'success': False, 'error': 'Unknown task type'})
        
        if success:
            task_notification_handler.notify_task_completed('system', task_data)
            return jsonify({'success': True})
        else:
            task_notification_handler.notify_task_failed('system', task_data, 'Execution failed')
            return jsonify({'success': False, 'error': 'Task execution failed'})
    
    except Exception as e:
        task_notification_handler.notify_task_failed('system', data.get('task_data', {}), str(e))
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/notifications')
def get_notifications():
    """Get recent notifications"""
    notifications = notification_manager.get_notifications(limit=50)
    return jsonify({'notifications': notifications})

@app.route('/api/notifications/clear', methods=['POST'])
def clear_notifications():
    """Clear notifications"""
    notification_manager.clear_notifications()
    return jsonify({'success': True})

# WebSocket events
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('status', {'connected': True})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('browser_check')
def handle_browser_check():
    """Check browser status"""
    status = automation_engine.check_connection()
    emit('browser_status', {'connected': status})

# Background monitoring
def monitor_system():
    """Monitor system status and emit updates"""
    while True:
        try:
            # Check battery level
            battery = psutil.sensors_battery()
            if battery and battery.percent < LOW_BATTERY_THRESHOLD:
                socketio.emit('low_battery_warning', {'level': battery.percent})
            
            # Check browser connection
            browser_status = automation_engine.check_connection()
            socketio.emit('browser_status', {'connected': browser_status})
            
            time.sleep(60)  # Check every minute
        except Exception as e:
            print(f"Monitor error: {e}")
            time.sleep(60)

# Start background monitoring
monitor_thread = threading.Thread(target=monitor_system)
monitor_thread.daemon = True
monitor_thread.start()

if __name__ == '__main__':
    print("Starting Yisel Web Server...")
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    
    if debug:
        print(f"Access the application at: http://localhost:{port}")
    
    socketio.run(app, debug=debug, host='0.0.0.0', port=port)
