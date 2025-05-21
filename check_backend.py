#!/usr/bin/env python
"""
Backend Diagnostic Script

This script tests the backend server and honeypot functionality
to ensure alerts are being processed correctly.
"""

import os
import sys
import json
import time
import requests
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("backend_check")

# Constants
API_URL = "http://localhost:8000"
TEST_ALERT = {
    "honeypot_id": "test-honeypot",
    "timestamp": datetime.now().isoformat(),
    "data": {
        "source_ip": "192.168.1.100",
        "attack_type": "TEST",
        "attack_details": {
            "command": "echo test_attack",
            "username": "test_user",
            "password": "test_password"
        }
    }
}

def check_server_status():
    """Check if the backend server is running."""
    try:
        response = requests.get(f"{API_URL}/", timeout=5)
        if response.status_code == 200:
            logger.info(f"✅ Backend server is running: {response.json()}")
            return True
        else:
            logger.error(f"❌ Backend server returned unexpected status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Backend server is not responding: {str(e)}")
        return False

def check_honeypots():
    """Check if honeypots are configured."""
    try:
        response = requests.get(f"{API_URL}/honeypots", timeout=5)
        if response.status_code == 200:
            honeypots = response.json()
            logger.info(f"✅ Found {len(honeypots)} honeypots configured")
            for honeypot in honeypots:
                logger.info(f"  - {honeypot['id']}: {honeypot['type']} on port {honeypot['port']}")
            return True
        else:
            logger.error(f"❌ Failed to get honeypots: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Failed to get honeypots: {str(e)}")
        return False

def check_alerts():
    """Check if alerts API is working."""
    try:
        response = requests.get(f"{API_URL}/alerts", timeout=5)
        if response.status_code == 200:
            alerts = response.json()
            logger.info(f"✅ Found {len(alerts)} alerts in the system")
            return True
        else:
            logger.error(f"❌ Failed to get alerts: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Failed to get alerts: {str(e)}")
        return False

def send_test_alert():
    """Send a test alert to the API."""
    try:
        logger.info(f"Sending test alert to API: {json.dumps(TEST_ALERT, indent=2)}")
        response = requests.post(
            f"{API_URL}/honeypots/{TEST_ALERT['honeypot_id']}/alerts",
            json=TEST_ALERT,
            timeout=5
        )
        if response.status_code == 200:
            logger.info(f"✅ Test alert successfully sent and processed")
            return True
        else:
            logger.error(f"❌ Failed to send test alert: {response.status_code} - {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Failed to send test alert: {str(e)}")
        return False

def main():
    """Run backend diagnostics."""
    print("=" * 70)
    print(f"Backend Server Diagnostic - {datetime.now()}")
    print("=" * 70)
    
    # Check if server is running
    if not check_server_status():
        print("\n❌ CRITICAL ERROR: Backend server is not running")
        print("Please start the server with: python -m uvicorn server:app --host 0.0.0.0 --port 8000")
        return False
    
    # Check if honeypots are configured
    if not check_honeypots():
        print("\n⚠️ WARNING: Unable to verify honeypot configuration")
    
    # Check if alerts API is working
    if not check_alerts():
        print("\n⚠️ WARNING: Unable to verify alerts API")
    
    # Send a test alert
    if not send_test_alert():
        print("\n❌ CRITICAL ERROR: Failed to send test alert")
        print("This may indicate an issue with the alert processing system")
    else:
        # Verify the alert was recorded
        time.sleep(2)  # Wait for processing
        try:
            response = requests.get(f"{API_URL}/alerts", timeout=5)
            if response.status_code == 200:
                alerts = response.json()
                if any(a.get("honeypot_id") == TEST_ALERT["honeypot_id"] for a in alerts):
                    print("\n✅ SUCCESS: Test alert was properly recorded in the system")
                else:
                    print("\n❌ ERROR: Test alert was not found in the alerts list")
            else:
                print(f"\n❌ ERROR: Failed to verify test alert: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"\n❌ ERROR: Failed to verify test alert: {str(e)}")
    
    print("\n" + "=" * 70)
    print("Diagnostics complete")
    print("=" * 70)
    return True

if __name__ == "__main__":
    main()
