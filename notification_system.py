"""
Notification System for Yisel Web
Handles real-time notifications, alerts, and communication
"""

import requests
import json
import datetime
import threading
import time
from flask_socketio import emit

class NotificationManager:
    """Manages notifications and alerts"""
    
    def __init__(self, socketio):
        self.socketio = socketio
        self.notification_topics = {}
        self.active_notifications = []
    
    def add_notification_topic(self, user_id, topic):
        """Add a notification topic for a user"""
        self.notification_topics[user_id] = topic
    
    def send_notification(self, user_id, title, message, notification_type='info'):
        """Send a notification to a specific user"""
        notification = {
            'id': f"notif_{int(time.time())}",
            'title': title,
            'message': message,
            'type': notification_type,
            'timestamp': datetime.datetime.now().isoformat(),
            'user_id': user_id
        }
        
        # Store notification
        self.active_notifications.append(notification)
        
        # Send via WebSocket
        self.socketio.emit('notification', notification, room=user_id)
        
        # Send via ntfy.sh if configured
        if user_id in self.notification_topics:
            self.send_ntfy_notification(self.notification_topics[user_id], title, message)
        
        return notification
    
    def send_ntfy_notification(self, topic, title, message):
        """Send notification via ntfy.sh"""
        try:
            url = f"https://ntfy.sh/{topic}"
            headers = {
                'Title': title,
                'Priority': 'default',
                'Tags': 'medical,yisel'
            }
            
            response = requests.post(url, data=message, headers=headers, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Failed to send ntfy notification: {e}")
            return False
    
    def broadcast_notification(self, title, message, notification_type='info'):
        """Broadcast notification to all connected users"""
        notification = {
            'id': f"broadcast_{int(time.time())}",
            'title': title,
            'message': message,
            'type': notification_type,
            'timestamp': datetime.datetime.now().isoformat(),
            'broadcast': True
        }
        
        self.active_notifications.append(notification)
        self.socketio.emit('notification', notification, broadcast=True)
        
        return notification
    
    def get_notifications(self, user_id=None, limit=50):
        """Get recent notifications"""
        if user_id:
            notifications = [n for n in self.active_notifications 
                           if n.get('user_id') == user_id or n.get('broadcast')]
        else:
            notifications = self.active_notifications
        
        return sorted(notifications, key=lambda x: x['timestamp'], reverse=True)[:limit]
    
    def clear_notifications(self, user_id=None):
        """Clear notifications"""
        if user_id:
            self.active_notifications = [n for n in self.active_notifications 
                                       if n.get('user_id') != user_id and not n.get('broadcast')]
        else:
            self.active_notifications = []

class SystemMonitor:
    """Monitors system status and sends alerts"""
    
    def __init__(self, notification_manager, automation_engine):
        self.notification_manager = notification_manager
        self.automation_engine = automation_engine
        self.monitoring = False
        self.monitor_thread = None
    
    def start_monitoring(self):
        """Start system monitoring"""
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop system monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                # Check browser connection
                self._check_browser_connection()
                
                # Check battery level
                self._check_battery_level()
                
                # Check system resources
                self._check_system_resources()
                
                time.sleep(60)  # Check every minute
            except Exception as e:
                print(f"Monitor error: {e}")
                time.sleep(60)
    
    def _check_browser_connection(self):
        """Check browser connection status"""
        try:
            is_connected = self.automation_engine.check_connection()
            
            # Store previous state to detect changes
            if not hasattr(self, '_prev_browser_state'):
                self._prev_browser_state = is_connected
                return
            
            if self._prev_browser_state != is_connected:
                if is_connected:
                    self.notification_manager.broadcast_notification(
                        "Browser Connected",
                        "Browser connection has been re-established",
                        "success"
                    )
                else:
                    self.notification_manager.broadcast_notification(
                        "Browser Disconnected",
                        "Browser connection lost. Attempting to reconnect...",
                        "warning"
                    )
                
                self._prev_browser_state = is_connected
        except Exception as e:
            print(f"Browser check error: {e}")
    
    def _check_battery_level(self):
        """Check system battery level"""
        try:
            import psutil
            battery = psutil.sensors_battery()
            
            if battery and battery.percent < 20:
                if not hasattr(self, '_battery_warning_sent') or not self._battery_warning_sent:
                    self.notification_manager.broadcast_notification(
                        "Low Battery Warning",
                        f"System battery is at {battery.percent}%. Please connect to power.",
                        "warning"
                    )
                    self._battery_warning_sent = True
            else:
                self._battery_warning_sent = False
        except Exception as e:
            print(f"Battery check error: {e}")
    
    def _check_system_resources(self):
        """Check system resource usage"""
        try:
            import psutil
            
            # Check memory usage
            memory = psutil.virtual_memory()
            if memory.percent > 90:
                self.notification_manager.broadcast_notification(
                    "High Memory Usage",
                    f"System memory usage is at {memory.percent}%",
                    "warning"
                )
            
            # Check CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > 95:
                self.notification_manager.broadcast_notification(
                    "High CPU Usage",
                    f"System CPU usage is at {cpu_percent}%",
                    "warning"
                )
        except Exception as e:
            print(f"Resource check error: {e}")

class TaskNotificationHandler:
    """Handles task-related notifications"""
    
    def __init__(self, notification_manager):
        self.notification_manager = notification_manager
    
    def notify_task_scheduled(self, user_id, task_data):
        """Notify when a task is scheduled"""
        self.notification_manager.send_notification(
            user_id,
            "Task Scheduled",
            f"Task scheduled for {task_data.get('patient_name', 'patient')} at {task_data.get('run_datetime')}",
            "info"
        )
    
    def notify_task_started(self, user_id, task_data):
        """Notify when a task starts"""
        self.notification_manager.send_notification(
            user_id,
            "Task Started",
            f"Executing {task_data.get('task_type')} for {task_data.get('patient_name', 'patient')}",
            "info"
        )
    
    def notify_task_completed(self, user_id, task_data):
        """Notify when a task completes"""
        self.notification_manager.send_notification(
            user_id,
            "Task Completed",
            f"Successfully completed {task_data.get('task_type')} for {task_data.get('patient_name', 'patient')}",
            "success"
        )
    
    def notify_task_failed(self, user_id, task_data, error_message):
        """Notify when a task fails"""
        self.notification_manager.send_notification(
            user_id,
            "Task Failed",
            f"Failed to complete {task_data.get('task_type')} for {task_data.get('patient_name', 'patient')}: {error_message}",
            "error"
        )
    
    def notify_batch_complete(self, user_id, completed_count, total_count):
        """Notify when a batch of tasks completes"""
        self.notification_manager.send_notification(
            user_id,
            "Batch Processing Complete",
            f"Completed {completed_count} of {total_count} scheduled tasks",
            "success" if completed_count == total_count else "warning"
        )

class AlertSystem:
    """Advanced alert system for critical events"""
    
    def __init__(self, notification_manager):
        self.notification_manager = notification_manager
        self.alert_rules = []
    
    def add_alert_rule(self, rule):
        """Add an alert rule"""
        self.alert_rules.append(rule)
    
    def check_alerts(self, event_data):
        """Check if any alert rules are triggered"""
        for rule in self.alert_rules:
            try:
                if self._evaluate_rule(rule, event_data):
                    self._trigger_alert(rule, event_data)
            except Exception as e:
                print(f"Alert rule evaluation error: {e}")
    
    def _evaluate_rule(self, rule, event_data):
        """Evaluate if an alert rule matches the event"""
        conditions = rule.get('conditions', {})
        
        for key, expected_value in conditions.items():
            if key not in event_data:
                return False
            
            actual_value = event_data[key]
            
            if isinstance(expected_value, dict):
                # Handle complex conditions
                if 'gt' in expected_value and actual_value <= expected_value['gt']:
                    return False
                if 'lt' in expected_value and actual_value >= expected_value['lt']:
                    return False
                if 'eq' in expected_value and actual_value != expected_value['eq']:
                    return False
            else:
                # Simple equality check
                if actual_value != expected_value:
                    return False
        
        return True
    
    def _trigger_alert(self, rule, event_data):
        """Trigger an alert"""
        alert_config = rule.get('alert', {})
        
        self.notification_manager.broadcast_notification(
            alert_config.get('title', 'System Alert'),
            alert_config.get('message', 'Alert condition triggered'),
            alert_config.get('type', 'warning')
        )
        
        # Execute any custom actions
        actions = rule.get('actions', [])
        for action in actions:
            try:
                self._execute_action(action, event_data)
            except Exception as e:
                print(f"Alert action execution error: {e}")
    
    def _execute_action(self, action, event_data):
        """Execute a custom alert action"""
        action_type = action.get('type')
        
        if action_type == 'email':
            # Send email notification
            pass
        elif action_type == 'webhook':
            # Send webhook
            url = action.get('url')
            if url:
                requests.post(url, json=event_data, timeout=10)
        elif action_type == 'log':
            # Log to file
            log_message = f"ALERT: {action.get('message', 'Alert triggered')} - {event_data}"
            print(log_message)

# Default alert rules
DEFAULT_ALERT_RULES = [
    {
        'name': 'High Task Failure Rate',
        'conditions': {
            'task_failure_rate': {'gt': 0.5},
            'time_window': 'last_hour'
        },
        'alert': {
            'title': 'High Task Failure Rate',
            'message': 'More than 50% of tasks have failed in the last hour',
            'type': 'error'
        },
        'actions': [
            {'type': 'log', 'message': 'High task failure rate detected'}
        ]
    },
    {
        'name': 'Browser Connection Lost',
        'conditions': {
            'browser_connected': {'eq': False},
            'duration': {'gt': 300}  # 5 minutes
        },
        'alert': {
            'title': 'Extended Browser Disconnection',
            'message': 'Browser has been disconnected for more than 5 minutes',
            'type': 'error'
        }
    },
    {
        'name': 'System Resource Critical',
        'conditions': {
            'memory_usage': {'gt': 95},
            'cpu_usage': {'gt': 95}
        },
        'alert': {
            'title': 'Critical System Resources',
            'message': 'System resources are critically low',
            'type': 'error'
        }
    }
]
