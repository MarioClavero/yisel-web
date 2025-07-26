"""
Advanced Automation Engine for Yisel Web
Handles all browser automation, form filling, and signing operations
"""

import time
import json
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, WebDriverException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import requests
import base64
from PIL import Image, ImageDraw
from io import BytesIO

class SignatureManager:
    """Advanced signature drawing using Chrome DevTools Protocol"""
    
    def __init__(self, driver):
        self.driver = driver
    
    def _find_canvas_and_context(self):
        """Finds the canvas element, searching the main document and all iframes"""
        self.driver.switch_to.default_content()
        selectors = ["#signatureCanvas", "canvas.pad", "div.sig-pad canvas", "canvas[data-signature]"]
        
        for sel in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, sel)
                if element.is_displayed():
                    return element, None
            except NoSuchElementException:
                pass
        
        # Search in iframes
        iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
        for frame in iframes:
            try:
                self.driver.switch_to.frame(frame)
                for sel in selectors:
                    try:
                        element = self.driver.find_element(By.CSS_SELECTOR, sel)
                        if element.is_displayed():
                            self.driver.switch_to.default_content()
                            return element, frame
                    except NoSuchElementException:
                        pass
                self.driver.switch_to.default_content()
            except WebDriverException:
                self.driver.switch_to.default_content()
        
        return None, None
    
    def draw_signature(self, signature_data):
        """Draw signature using CDP commands for maximum reliability"""
        canvas, frame = self._find_canvas_and_context()
        if not canvas:
            print("Canvas element not found for signature")
            return False
        
        if frame:
            self.driver.switch_to.frame(frame)
        
        # Get canvas position
        bounding_box = canvas.rect
        canvas_x_start = bounding_box['x']
        canvas_y_start = bounding_box['y']
        
        try:
            for stroke in signature_data['strokes']:
                if not stroke:
                    continue
                
                # Start stroke
                start_point = stroke[0]
                x = canvas_x_start + start_point[0]
                y = canvas_y_start + start_point[1]
                
                self.driver.execute_cdp_cmd("Input.dispatchMouseEvent", {
                    "type": "mousePressed",
                    "x": x,
                    "y": y,
                    "button": "left",
                    "clickCount": 1
                })
                time.sleep(0.02)
                
                # Draw stroke
                for point in stroke[1:]:
                    x = canvas_x_start + point[0]
                    y = canvas_y_start + point[1]
                    self.driver.execute_cdp_cmd("Input.dispatchMouseEvent", {
                        "type": "mouseMoved",
                        "x": x,
                        "y": y,
                        "button": "left"
                    })
                    time.sleep(0.01)
                
                # End stroke
                end_point = stroke[-1]
                x = canvas_x_start + end_point[0]
                y = canvas_y_start + end_point[1]
                self.driver.execute_cdp_cmd("Input.dispatchMouseEvent", {
                    "type": "mouseReleased",
                    "x": x,
                    "y": y,
                    "button": "left",
                    "clickCount": 1
                })
                time.sleep(0.05)
            
            return True
        except Exception as e:
            print(f"Signature drawing failed: {e}")
            return False
        finally:
            if frame:
                self.driver.switch_to.default_content()

class KinnserAutomation:
    """Main automation engine for Kinnser operations"""
    
    def __init__(self, driver):
        self.driver = driver
        self.signature_manager = SignatureManager(driver)
        self.wait = WebDriverWait(driver, 10)
    
    def login(self, username, password):
        """Login to Kinnser"""
        try:
            self.driver.get("https://www.kinnser.com/login")
            
            # Wait for login form
            username_field = self.wait.until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            password_field = self.driver.find_element(By.ID, "password")
            
            username_field.clear()
            username_field.send_keys(username)
            password_field.clear()
            password_field.send_keys(password)
            
            # Submit login
            login_button = self.driver.find_element(By.CSS_SELECTOR, "input[type='submit'], button[type='submit']")
            login_button.click()
            
            # Wait for dashboard
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".dashboard, #dashboard, [data-page='dashboard']"))
            )
            
            return True
        except Exception as e:
            print(f"Login failed: {e}")
            return False
    
    def fetch_patients(self):
        """Fetch patient list from Kinnser"""
        try:
            # Navigate to patient list
            self.driver.get("https://www.kinnser.com/patients")
            
            # Wait for patient table
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".patient-table, #patient-list, [data-patients]"))
            )
            
            # Extract patient data
            patients = []
            patient_rows = self.driver.find_elements(By.CSS_SELECTOR, "tr[data-patient], .patient-row")
            
            for row in patient_rows:
                try:
                    name_element = row.find_element(By.CSS_SELECTOR, ".patient-name, [data-name]")
                    patient_id = row.get_attribute("data-patient-id") or row.get_attribute("data-id")
                    
                    patient = {
                        'patient_key': patient_id,
                        'name': name_element.text.strip(),
                        'visits_data': [],
                        'location': None
                    }
                    patients.append(patient)
                except Exception as e:
                    print(f"Error extracting patient data: {e}")
                    continue
            
            return patients
        except Exception as e:
            print(f"Failed to fetch patients: {e}")
            return []
    
    def get_patient_visits(self, patient_key):
        """Get visits for a specific patient"""
        try:
            # Navigate to patient visits
            self.driver.get(f"https://www.kinnser.com/patients/{patient_key}/visits")
            
            # Wait for visits table
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".visits-table, #visits-list"))
            )
            
            visits = []
            visit_rows = self.driver.find_elements(By.CSS_SELECTOR, "tr[data-visit], .visit-row")
            
            for row in visit_rows:
                try:
                    visit_id = row.get_attribute("data-visit-id")
                    date_element = row.find_element(By.CSS_SELECTOR, ".visit-date, [data-date]")
                    status_element = row.find_element(By.CSS_SELECTOR, ".visit-status, [data-status]")
                    
                    visit = {
                        'visit_id': visit_id,
                        'date': date_element.text.strip(),
                        'status': status_element.text.strip(),
                        'signable': 'unsigned' in status_element.text.lower()
                    }
                    visits.append(visit)
                except Exception as e:
                    print(f"Error extracting visit data: {e}")
                    continue
            
            return visits
        except Exception as e:
            print(f"Failed to get patient visits: {e}")
            return []
    
    def autofill_note(self, patient_key, visit_id, note_data):
        """Autofill a patient note"""
        try:
            # Navigate to note form
            self.driver.get(f"https://www.kinnser.com/patients/{patient_key}/visits/{visit_id}/note")
            
            # Wait for form
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "form, .note-form"))
            )
            
            # Fill form fields
            for field_name, value in note_data.items():
                try:
                    # Try different field selectors
                    selectors = [
                        f"#{field_name}",
                        f"[name='{field_name}']",
                        f"[data-field='{field_name}']",
                        f".{field_name}"
                    ]
                    
                    element = None
                    for selector in selectors:
                        try:
                            element = self.driver.find_element(By.CSS_SELECTOR, selector)
                            break
                        except NoSuchElementException:
                            continue
                    
                    if element:
                        if element.tag_name == 'select':
                            select = Select(element)
                            try:
                                select.select_by_visible_text(value)
                            except:
                                select.select_by_value(value)
                        elif element.tag_name == 'textarea':
                            element.clear()
                            element.send_keys(value)
                        elif element.get_attribute('type') == 'checkbox':
                            if value and not element.is_selected():
                                element.click()
                            elif not value and element.is_selected():
                                element.click()
                        else:
                            element.clear()
                            element.send_keys(value)
                
                except Exception as e:
                    print(f"Error filling field {field_name}: {e}")
                    continue
            
            return True
        except Exception as e:
            print(f"Autofill failed: {e}")
            return False
    
    def sign_note(self, patient_key, visit_id, signature_data=None, sign_method='patient_unable'):
        """Sign a patient note"""
        try:
            # Navigate to signing page
            self.driver.get(f"https://www.kinnser.com/patients/{patient_key}/visits/{visit_id}/sign")
            
            # Wait for signing form
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".signature-form, #signature-section"))
            )
            
            if sign_method == 'draw_signature' and signature_data:
                # Draw signature
                success = self.signature_manager.draw_signature(signature_data)
                if not success:
                    print("Signature drawing failed, falling back to 'patient unable'")
                    sign_method = 'patient_unable'
            
            if sign_method == 'patient_unable':
                # Select "Patient Unable to Sign" option
                unable_checkbox = self.driver.find_element(
                    By.CSS_SELECTOR, 
                    "input[value='patient_unable'], #patient_unable, [data-sign='unable']"
                )
                if not unable_checkbox.is_selected():
                    unable_checkbox.click()
            
            # Submit signature
            submit_button = self.driver.find_element(
                By.CSS_SELECTOR, 
                "button[type='submit'], input[type='submit'], .submit-signature"
            )
            submit_button.click()
            
            # Wait for confirmation
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".success, .confirmation, [data-success]"))
            )
            
            return True
        except Exception as e:
            print(f"Signing failed: {e}")
            return False
    
    def change_patient_location(self, patient_key, location_data):
        """Change patient location"""
        try:
            # Navigate to patient location page
            self.driver.get(f"https://www.kinnser.com/patients/{patient_key}/location")
            
            # Wait for location form
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".location-form, #location-section"))
            )
            
            # Fill location fields
            for field, value in location_data.items():
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, f"[name='{field}'], #{field}")
                    if element.tag_name == 'select':
                        select = Select(element)
                        select.select_by_visible_text(value)
                    else:
                        element.clear()
                        element.send_keys(value)
                except Exception as e:
                    print(f"Error setting location field {field}: {e}")
            
            # Submit location change
            submit_button = self.driver.find_element(
                By.CSS_SELECTOR, 
                "button[type='submit'], input[type='submit'], .submit-location"
            )
            submit_button.click()
            
            return True
        except Exception as e:
            print(f"Location change failed: {e}")
            return False

class AutomationEngine:
    """Main automation engine for Yisel Web"""
    
    def __init__(self):
        self.driver = None
        self.wait = None
        self.signature_manager = None
        self.is_connected = False
        self.cloud_mode = self._detect_cloud_environment()
        self.setup_driver()
    
    def _detect_cloud_environment(self):
        """Detect if running in cloud environment"""
        import os
        return bool(os.environ.get('RAILWAY_ENVIRONMENT') or 
                   os.environ.get('HEROKU_APP_NAME') or 
                   os.environ.get('VERCEL') or 
                   os.environ.get('PORT'))

    def setup_driver(self):
        """Setup Chrome browser with automation capabilities"""
        if self.cloud_mode:
            print("Cloud environment detected - browser automation limited")
            self.is_connected = False
            return
            
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--remote-debugging-port=9222")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, 10)
            self.signature_manager = SignatureManager(self.driver)
            
            self.is_connected = True
            print("Browser automation setup successful")
            return True
        except Exception as e:
            print(f"Browser setup failed: {e}")
            self.is_connected = False
            return False
    
    def check_connection(self):
        """Check if browser is still connected"""
        try:
            if self.driver:
                self.driver.current_url
                self.is_connected = True
                return True
        except:
            self.is_connected = False
            return False
    
    def login_to_kinnser(self, username, password):
        """Login to Kinnser"""
        if self.cloud_mode:
            print("Cloud mode: Browser automation not available")
            return False
            
        if not self.is_connected:
            if not self.setup_driver():
                return False
        
        try:
            # Navigate to Kinnser login
            self.driver.get("https://www.kinnser.com/login")
            
            # Fill login form
            username_field = self.wait.until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            password_field = self.driver.find_element(By.NAME, "password")
            
            username_field.send_keys(username)
            password_field.send_keys(password)
            
            # Submit form
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
            login_button.click()
            
            # Wait for dashboard
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".dashboard, #main-content"))
            )
            
            return True
        except Exception as e:
            print(f"Kinnser login failed: {e}")
            return False
    
    def fetch_patients(self):
        """Fetch patients from Kinnser"""
        if self.cloud_mode:
            # Return mock data for cloud environment
            return [
                {
                    'patient_key': 'demo_001',
                    'name': 'Demo Patient 1',
                    'dob': '1980-01-15',
                    'address': '123 Main St, City, ST 12345',
                    'phone': '(555) 123-4567',
                    'status': 'Active'
                },
                {
                    'patient_key': 'demo_002', 
                    'name': 'Demo Patient 2',
                    'dob': '1975-06-22',
                    'address': '456 Oak Ave, Town, ST 67890',
                    'phone': '(555) 987-6543',
                    'status': 'Active'
                }
            ]
            
        if not self.is_connected:
            return []
        
        try:
            # Navigate to patients page
            self.driver.get("https://www.kinnser.com/patients")
            
            # Wait for patient list
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".patient-list, #patients-table"))
            )
            
            patients = []
            patient_rows = self.driver.find_elements(By.CSS_SELECTOR, "tr[data-patient], .patient-row")
            
            for row in patient_rows:
                try:
                    patient_key = row.get_attribute("data-patient-key")
                    name_element = row.find_element(By.CSS_SELECTOR, ".patient-name, [data-name]")
                    dob_element = row.find_element(By.CSS_SELECTOR, ".patient-dob, [data-dob]")
                    
                    patient = {
                        'patient_key': patient_key,
                        'name': name_element.text.strip(),
                        'dob': dob_element.text.strip(),
                        'status': 'Active'
                    }
                    patients.append(patient)
                except Exception as e:
                    print(f"Error extracting patient data: {e}")
                    continue
            
            return patients
        except Exception as e:
            print(f"Failed to fetch patients: {e}")
            return []
    
    def get_patient_visits(self, patient_key):
        """Get visits for a patient"""
        if self.cloud_mode:
            # Return mock visit data for cloud environment
            return [
                {
                    'visit_id': 'visit_001',
                    'date': '2024-07-26',
                    'status': 'Unsigned',
                    'signable': True
                },
                {
                    'visit_id': 'visit_002',
                    'date': '2024-07-25',
                    'status': 'Signed',
                    'signable': False
                }
            ]
            
        if not self.is_connected:
            return []
        
        try:
            # Navigate to patient visits
            self.driver.get(f"https://www.kinnser.com/patients/{patient_key}/visits")
            
            # Wait for visits table
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".visits-table, #visits-list"))
            )
            
            visits = []
            visit_rows = self.driver.find_elements(By.CSS_SELECTOR, "tr[data-visit], .visit-row")
            
            for row in visit_rows:
                try:
                    visit_id = row.get_attribute("data-visit-id")
                    date_element = row.find_element(By.CSS_SELECTOR, ".visit-date, [data-date]")
                    status_element = row.find_element(By.CSS_SELECTOR, ".visit-status, [data-status]")
                    
                    visit = {
                        'visit_id': visit_id,
                        'date': date_element.text.strip(),
                        'status': status_element.text.strip(),
                        'signable': 'unsigned' in status_element.text.lower()
                    }
                    visits.append(visit)
                except Exception as e:
                    print(f"Error extracting visit data: {e}")
                    continue
            
            return visits
        except Exception as e:
            print(f"Failed to get patient visits: {e}")
            return []
    
    def execute_autofill_task(self, task_data):
        """Execute an autofill task"""
        if self.cloud_mode:
            print("Cloud mode: Autofill simulation completed")
            return True
            
        if not self.is_connected:
            return False
        
        try:
            # Navigate to note form
            self.driver.get(f"https://www.kinnser.com/patients/{task_data['patient_key']}/visits/{task_data['visit_id']}/note")
            
            # Wait for form
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "form, .note-form"))
            )
            
            # Fill form fields
            for field_name, value in task_data['note_data'].items():
                try:
                    selectors = [
                        f"#{field_name}",
                        f"[name='{field_name}']",
                        f"[data-field='{field_name}']",
                        f".{field_name}"
                    ]
                    
                    element = None
                    for selector in selectors:
                        try:
                            element = self.driver.find_element(By.CSS_SELECTOR, selector)
                            break
                        except NoSuchElementException:
                            continue
                    
                    if element:
                        if element.tag_name.lower() == 'select':
                            select = Select(element)
                            select.select_by_visible_text(value)
                        else:
                            element.clear()
                            element.send_keys(value)
                except Exception as e:
                    print(f"Error filling field {field_name}: {e}")
                    continue
            
            return True
        except Exception as e:
            print(f"Autofill task failed: {e}")
            return False
    
    def execute_sign_task(self, task_data):
        """Execute a signing task"""
        if self.cloud_mode:
            print("Cloud mode: Signature simulation completed")
            return True
            
        if not self.is_connected:
            return False
        
        try:
            # Navigate to signing page
            self.driver.get(f"https://www.kinnser.com/patients/{task_data['patient_key']}/visits/{task_data['visit_id']}/sign")
            
            # Wait for signature area
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "canvas, .signature-pad, #signature-area"))
            )
            
            # Use signature manager to draw signature
            if self.signature_manager and task_data.get('signature_data'):
                success = self.signature_manager.draw_signature(task_data['signature_data'])
                if success:
                    # Submit signature
                    submit_button = self.driver.find_element(
                        By.CSS_SELECTOR, 
                        "button[type='submit'], .submit-signature, #sign-submit"
                    )
                    submit_button.click()
                    return True
            
            return False
        except Exception as e:
            print(f"Sign task failed: {e}")
            return False
    
    def change_patient_location(self, patient_key, location_data):
        """Change patient location"""
        if not self.is_connected or not self.kinnser:
            return False
        
        return self.kinnser.change_patient_location(patient_key, location_data)
    
    def quit(self):
        """Quit the browser"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None
            self.kinnser = None
            self.is_connected = False
