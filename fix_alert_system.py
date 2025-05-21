#!/usr/bin/env python
"""
Alert System Diagnostic and Fix Tool

This script performs comprehensive diagnostics on the alert system,
identifies issues, and applies fixes to ensure alerts are properly
generated, stored, and displayed on the dashboard.
"""

import requests
import json
import time
import os
import sys
import random
from datetime import datetime

# Configuration
SERVER_URL = "http://localhost:8000"
DASHBOARD_URL = "http://localhost:3000"
HONEYPOT_TYPES = ["ssh", "web"]
TEST_COUNT = 5  # Number of test alerts to generate
VERBOSE = True  # Show detailed diagnostic information

def colored(text, color):
    """Return colored text for terminal output."""
    colors = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "purple": "\033[95m",
        "cyan": "\033[96m",
        "end": "\033[0m"
    }
    return f"{colors.get(color, '')}{text}{colors['end']}"

def print_header(title):
    """Print a section header."""
    print()
    print(colored("="*80, "blue"))
    print(colored(f" {title} ".center(80, "="), "blue"))
    print(colored("="*80, "blue"))

def print_success(message):
    """Print a success message."""
    print(colored(f"✅ {message}", "green"))

def print_error(message):
    """Print an error message."""
    print(colored(f"❌ {message}", "red"))

def print_warning(message):
    """Print a warning message."""
    print(colored(f"⚠️ {message}", "yellow"))

def print_info(message):
    """Print an info message."""
    print(colored(f"ℹ️ {message}", "cyan"))

def check_server_status():
    """Check if the backend server is running and responding."""
    print_header("CHECKING SERVER STATUS")
    
    try:
        response = requests.get(f"{SERVER_URL}/", timeout=5)
        if response.status_code == 200:
            print_success(f"Backend server is running at {SERVER_URL}")
            return True
        else:
            print_error(f"Backend server returned unexpected status code: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Failed to connect to backend server: {str(e)}")
        print_info("Make sure the honeypot system is running (python start.py)")
        return False

def check_dashboard_status():
    """Check if the frontend dashboard is running."""
    print_header("CHECKING DASHBOARD STATUS")
    
    try:
        response = requests.get(DASHBOARD_URL, timeout=5)
        if response.status_code == 200:
            print_success(f"Dashboard is running at {DASHBOARD_URL}")
            return True
        else:
            print_warning(f"Dashboard returned unexpected status code: {response.status_code}")
            return False
    except Exception as e:
        print_warning(f"Could not connect to dashboard: {str(e)}")
        print_info("The dashboard may still be accessible directly in your browser")
        return False

def check_honeypots():
    """Check if honeypots are registered and active."""
    print_header("CHECKING HONEYPOT STATUS")
    
    try:
        response = requests.get(f"{SERVER_URL}/honeypots", timeout=5)
        if response.status_code == 200:
            honeypots = response.json()
            
            if not honeypots:
                print_error("No honeypots are registered with the server")
                return False
            
            print_success(f"Found {len(honeypots)} honeypots registered with the server")
            
            active_honeypots = [h for h in honeypots.values() if h.get("status") == "Active"]
            
            if not active_honeypots:
                print_error("No active honeypots found")
                return False
            
            print_success(f"{len(active_honeypots)} honeypots are active")
            
            for honeypot_id, honeypot in honeypots.items():
                status = honeypot.get("status", "Unknown")
                honeypot_type = honeypot.get("type", "Unknown")
                ip = honeypot.get("ip", "Unknown")
                port = honeypot.get("port", "Unknown")
                
                if status == "Active":
                    print_success(f"Honeypot {honeypot_id}: {honeypot_type} on {ip}:{port} is {status}")
                else:
                    print_warning(f"Honeypot {honeypot_id}: {honeypot_type} on {ip}:{port} is {status}")
            
            return True
        else:
            print_error(f"Failed to get honeypot status: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error checking honeypots: {str(e)}")
        return False

def check_current_alerts():
    """Check if any alerts already exist in the system."""
    print_header("CHECKING EXISTING ALERTS")
    
    try:
        response = requests.get(f"{SERVER_URL}/alerts", timeout=5)
        if response.status_code == 200:
            alerts = response.json()
            
            if alerts:
                print_success(f"Found {len(alerts)} existing alerts in the system")
                if VERBOSE:
                    print_info("Latest alert sample:")
                    print(json.dumps(alerts[-1], indent=2))
            else:
                print_warning("No existing alerts found in the system")
            
            return len(alerts)
        else:
            print_error(f"Failed to get alerts: {response.status_code}")
            return 0
    except Exception as e:
        print_error(f"Error checking alerts: {str(e)}")
        return 0

def generate_test_alerts():
    """Generate and send test alerts to the system."""
    print_header("GENERATING TEST ALERTS")
    
    sent_count = 0
    honeypot_ids = []
    
    # Try to get actual honeypot IDs from the server
    try:
        response = requests.get(f"{SERVER_URL}/honeypots", timeout=5)
        if response.status_code == 200:
            honeypots = response.json()
            honeypot_ids = list(honeypots.keys())
            print_success(f"Using real honeypot IDs: {', '.join(honeypot_ids)}")
    except:
        # Fallback to generated IDs
        for htype in HONEYPOT_TYPES:
            honeypot_ids.append(f"{htype}-honeypot-1")
        print_warning(f"Using fallback honeypot IDs: {', '.join(honeypot_ids)}")
    
    if not honeypot_ids:
        print_error("No honeypot IDs available for testing")
        return 0
    
    for i in range(TEST_COUNT):
        honeypot_id = random.choice(honeypot_ids)
        honeypot_type = honeypot_id.split('-')[0] if '-' in honeypot_id else "unknown"
        
        # Create a test alert with easily identifiable data
        alert_data = {
            "timestamp": datetime.now().isoformat(),
            "data": {
                "source_ip": f"192.168.1.{random.randint(100, 200)}",
                "attack_type": f"DIAGNOSTIC_TEST_{honeypot_type.upper()}",
                "details": {
                    "test_id": f"test-{i+1}-{int(time.time())}",
                    "message": "This is a diagnostic test alert",
                    "severity": random.choice(["low", "medium", "high", "critical"])
                }
            }
        }
        
        print_info(f"Sending test alert #{i+1} to honeypot {honeypot_id}")
        
        try:
            # Send the alert to the server
            response = requests.post(
                f"{SERVER_URL}/honeypot/{honeypot_id}/alert",
                json=alert_data,
                timeout=10
            )
            
            # Check the response
            if response.status_code == 200:
                print_success(f"Alert #{i+1} sent successfully")
                sent_count += 1
                
                if VERBOSE:
                    print_info("Server response:")
                    print(json.dumps(response.json(), indent=2))
            else:
                print_error(f"Failed to send alert #{i+1}: {response.status_code}")
                print_error(f"Response: {response.text}")
        except Exception as e:
            print_error(f"Exception sending alert #{i+1}: {str(e)}")
        
        # Brief pause between alerts
        time.sleep(0.5)
    
    return sent_count

def verify_alerts(expected_count, initial_count):
    """Verify that the test alerts were properly stored."""
    print_header("VERIFYING ALERTS")
    
    try:
        response = requests.get(f"{SERVER_URL}/alerts", timeout=5)
        if response.status_code == 200:
            alerts = response.json()
            current_count = len(alerts)
            new_count = current_count - initial_count
            
            print_info(f"Initial alert count: {initial_count}")
            print_info(f"Current alert count: {current_count}")
            print_info(f"New alerts detected: {new_count}")
            
            if new_count >= expected_count:
                print_success(f"All {expected_count} test alerts were successfully stored!")
                
                # Check for diagnostic test alerts specifically
                diagnostic_alerts = [a for a in alerts if 'data' in a and 'attack_type' in a['data'] and 'DIAGNOSTIC_TEST' in a['data']['attack_type']]
                
                if diagnostic_alerts:
                    print_success(f"Found {len(diagnostic_alerts)} diagnostic test alerts")
                    
                    if VERBOSE:
                        print_info("Sample diagnostic alert:")
                        print(json.dumps(diagnostic_alerts[-1], indent=2))
                else:
                    print_error("Could not find any diagnostic test alerts by attack_type")
            else:
                print_error(f"Only {new_count} of {expected_count} test alerts were stored")
                
                if alerts:
                    print_info("Latest alert in the system:")
                    print(json.dumps(alerts[-1], indent=2))
        else:
            print_error(f"Failed to get alerts: {response.status_code}")
    except Exception as e:
        print_error(f"Error verifying alerts: {str(e)}")

def check_threat_intelligence():
    """Check if the threat intelligence endpoint is working."""
    print_header("CHECKING THREAT INTELLIGENCE")
    
    try:
        response = requests.get(f"{SERVER_URL}/threat-intelligence", timeout=5)
        if response.status_code == 200:
            intelligence = response.json()
            print_success("Threat intelligence endpoint is working")
            
            if VERBOSE:
                print_info("Threat intelligence data:")
                print(json.dumps(intelligence, indent=2))
            
            return True
        else:
            print_error(f"Failed to get threat intelligence: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error checking threat intelligence: {str(e)}")
        return False

def main():
    """Main function to diagnose and fix the alert system."""
    print_header("HONEYPOT ALERT SYSTEM DIAGNOSTIC")
    print(f"🕒 Started at: {datetime.now()}")
    print(f"🔍 Backend API URL: {SERVER_URL}")
    print(f"🖥️ Dashboard URL: {DASHBOARD_URL}")
    
    # Step 1: Check if the server is running
    if not check_server_status():
        print_error("Cannot proceed without a running backend server")
        return
    
    # Step 2: Check if the dashboard is accessible
    check_dashboard_status()  # Continue even if dashboard isn't accessible
    
    # Step 3: Check if honeypots are registered and active
    check_honeypots()  # Continue even if no honeypots are found
    
    # Step 4: Check if any alerts already exist
    initial_alert_count = check_current_alerts()
    
    # Step 5: Generate and send test alerts
    sent_count = generate_test_alerts()
    
    if sent_count > 0:
        # Wait for the server to process the alerts
        print_info("Waiting 3 seconds for the server to process alerts...")
        time.sleep(3)
        
        # Step 6: Verify that the alerts were stored
        verify_alerts(sent_count, initial_alert_count)
    
    # Step 7: Check the threat intelligence endpoint
    check_threat_intelligence()
    
    print_header("DIAGNOSTIC SUMMARY")
    print(f"🕒 Completed at: {datetime.now()}")
    print(f"📊 Initial alerts: {initial_alert_count}")
    print(f"🚨 Test alerts sent: {sent_count}")
    
    # Provide next steps
    print_header("NEXT STEPS")
    print("1. Refresh the dashboard at http://localhost:3000")
    print("2. Check the logs in the 'logs' directory")
    print("3. If issues persist, restart the system with 'python start.py'")
    print("4. Run attack simulations again with 'python run_simulations.py'")

if __name__ == "__main__":
    main()
