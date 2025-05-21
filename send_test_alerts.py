#!/usr/bin/env python
"""
Test Alert Generator

This script sends test alerts directly to the backend API
to verify that the alert system is working properly.
"""

import json
import time
import requests
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test_alerts")

# API endpoint
API_URL = "http://localhost:8000/honeypots/{honeypot_id}/alerts"

# Test alerts
TEST_ALERTS = [
    {
        "honeypot_id": "ssh-honeypot-1",
        "timestamp": datetime.now().isoformat(),
        "data": {
            "source_ip": "192.168.1.100",
            "attack_type": "SSH_BRUTE_FORCE",
            "attack_details": {
                "username": "admin",
                "password": "password123",
                "attempts": 5
            }
        }
    },
    {
        "honeypot_id": "ssh-honeypot-1",
        "timestamp": datetime.now().isoformat(),
        "data": {
            "source_ip": "192.168.1.101",
            "attack_type": "COMMAND_INJECTION",
            "attack_details": {
                "command": "cat /etc/passwd | grep root",
                "username": "root"
            }
        }
    },
    {
        "honeypot_id": "web-honeypot-1",
        "timestamp": datetime.now().isoformat(),
        "data": {
            "source_ip": "192.168.1.102",
            "attack_type": "SQL_INJECTION",
            "attack_details": {
                "url": "/login",
                "payload": "' OR 1=1 --",
                "parameter": "username"
            }
        }
    },
    {
        "honeypot_id": "web-honeypot-1",
        "timestamp": datetime.now().isoformat(),
        "data": {
            "source_ip": "192.168.1.103",
            "attack_type": "XSS",
            "attack_details": {
                "url": "/search",
                "payload": "<script>alert('XSS')</script>",
                "parameter": "q"
            }
        }
    },
    {
        "honeypot_id": "web-honeypot-1",
        "timestamp": datetime.now().isoformat(),
        "data": {
            "source_ip": "192.168.1.104",
            "attack_type": "PATH_TRAVERSAL",
            "attack_details": {
                "url": "/download",
                "payload": "../../../etc/passwd",
                "parameter": "file"
            }
        }
    }
]

def send_alert(alert):
    """Send a test alert to the API."""
    honeypot_id = alert.pop("honeypot_id")
    url = API_URL.format(honeypot_id=honeypot_id)
    
    try:
        logger.info(f"Sending test alert to {url}")
        response = requests.post(url, json=alert)
        
        if response.status_code == 200:
            logger.info(f"✅ Alert successfully sent to API: {honeypot_id}")
            logger.info(f"Response: {response.json()}")
            return True
        else:
            logger.error(f"❌ Failed to send alert: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
    except Exception as e:
        logger.error(f"❌ Error sending alert: {str(e)}")
        return False

def main():
    """Main function to send test alerts."""
    print("=" * 70)
    print(f"Test Alert Generator - {datetime.now()}")
    print("=" * 70)
    print(f"Sending {len(TEST_ALERTS)} test alerts to backend API")
    print(f"API URL: {API_URL}")
    print("=" * 70)
    
    success_count = 0
    
    for i, alert in enumerate(TEST_ALERTS, 1):
        print(f"\nSending Alert {i}/{len(TEST_ALERTS)}:")
        print(f"Honeypot: {alert['honeypot_id']}")
        print(f"Attack Type: {alert['data']['attack_type']}")
        
        if send_alert(alert.copy()):
            success_count += 1
        
        # Wait between alerts
        if i < len(TEST_ALERTS):
            time.sleep(1)
    
    print("\n" + "=" * 70)
    print(f"Completed sending test alerts")
    print(f"Success: {success_count}/{len(TEST_ALERTS)}")
    print("=" * 70)
    print("You should now see these alerts in the dashboard at http://localhost:3000")

if __name__ == "__main__":
    main()
