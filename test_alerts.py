#!/usr/bin/env python
"""
Direct Alert Testing Script

This script bypasses the honeypot and directly injects test alerts into the backend server
to diagnose issues with the alert system.
"""

import requests
import json
import time
from datetime import datetime

# Configuration
SERVER_URL = "http://localhost:8000"
HONEYPOT_ID = "test-honeypot-1"

def send_direct_alert():
    """Send a direct alert to the server API endpoint."""
    
    # Create a test alert with obvious data for easy identification
    alert_data = {
        "timestamp": datetime.now().isoformat(),
        "data": {
            "source_ip": "192.168.1.100",
            "attack_type": "TEST_ALERT_DIRECT",
            "details": {
                "message": "This is a direct test alert",
                "test_id": int(time.time()),
                "simulator": "diagnostic"
            }
        }
    }
    
    # Print what we're about to send
    print(f"\nSending direct test alert to: {SERVER_URL}/honeypot/{HONEYPOT_ID}/alert")
    print(f"Alert data: {json.dumps(alert_data, indent=2)}")
    
    try:
        # Send the alert to the server
        response = requests.post(
            f"{SERVER_URL}/honeypot/{HONEYPOT_ID}/alert",
            json=alert_data,
            timeout=10
        )
        
        # Check the response
        if response.status_code == 200:
            print(f"\n✅ SUCCESS: Alert sent successfully! Status code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            return True
        else:
            print(f"\n❌ ERROR: Failed to send alert. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"\n❌ ERROR: Exception while sending alert: {str(e)}")
        return False

def check_alerts():
    """Check if our alert was stored by querying the alerts endpoint."""
    
    print(f"\nChecking alerts at: {SERVER_URL}/alerts")
    
    try:
        response = requests.get(f"{SERVER_URL}/alerts", timeout=10)
        
        if response.status_code == 200:
            alerts = response.json()
            print(f"Retrieved {len(alerts)} alerts from server")
            
            # Check for our test alert
            found = False
            for alert in alerts:
                data = alert.get("data", {})
                attack_type = data.get("attack_type", "")
                
                if attack_type == "TEST_ALERT_DIRECT":
                    found = True
                    print(f"\n✅ SUCCESS: Found our test alert in the server!")
                    print(f"Alert: {json.dumps(alert, indent=2)}")
                    break
            
            if not found:
                print(f"\n❌ ERROR: Our test alert was not found in the {len(alerts)} alerts returned by the server.")
                print("This suggests the alert was not properly stored or there's an issue with the alerts endpoint.")
                
                # If there are other alerts, print the first one as an example
                if alerts:
                    print(f"\nExample of alert found on server: {json.dumps(alerts[0], indent=2)}")
        else:
            print(f"\n❌ ERROR: Failed to get alerts. Status code: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"\n❌ ERROR: Exception while checking alerts: {str(e)}")

def main():
    """Main function to run the direct alert test."""
    print("=" * 80)
    print(f"Direct Alert Testing Script - {datetime.now()}")
    print("=" * 80)
    print("This script bypasses the honeypot and sends alerts directly to the server")
    print("It will help diagnose issues with alert storage and retrieval")
    print("=" * 80)
    
    # Send the test alert
    if send_direct_alert():
        # Wait a moment for the server to process the alert
        print("\nWaiting 3 seconds for the server to process the alert...")
        time.sleep(3)
        
        # Check if our alert was stored
        check_alerts()
    
    print("\n" + "=" * 80)
    print("Direct alert testing completed")
    print("=" * 80)

if __name__ == "__main__":
    main()
