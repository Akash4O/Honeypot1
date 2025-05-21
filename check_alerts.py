#!/usr/bin/env python
"""
Alert System Diagnostic Tool

This utility checks if the alert system is working properly and helps diagnose issues.
"""

import requests
import json
import os
import time
import sys
from datetime import datetime

def check_alert_api(base_url="http://localhost:8000"):
    """Check if the alerts API is accessible and returning data."""
    try:
        print(f"Testing alert API at {base_url}/alerts...")
        response = requests.get(f"{base_url}/alerts", timeout=5)
        
        # Check status code
        if response.status_code == 200:
            print(f"✅ Alert API is accessible. Status: {response.status_code}")
            
            # Try to parse the response as JSON
            try:
                data = response.json()
                print(f"✅ API returned valid JSON data")
                
                # Check if the data is an array (list)
                if isinstance(data, list):
                    print(f"✅ API returned an array with {len(data)} alerts")
                    
                    # Log alert details if any exist
                    if len(data) > 0:
                        print("\nMost recent alerts:")
                        for i, alert in enumerate(data[-5:], 1):  # Show last 5 alerts
                            print(f"  Alert {i}:")
                            print(f"    Honeypot: {alert.get('honeypot_id', 'Unknown')}")
                            print(f"    Timestamp: {alert.get('timestamp', 'Unknown')}")
                            print(f"    Source IP: {alert.get('data', {}).get('source_ip', 'Unknown')}")
                            print(f"    Attack Type: {alert.get('data', {}).get('attack_type', 'Unknown')}")
                            print()
                    else:
                        print("⚠️ No alerts have been recorded yet")
                else:
                    print(f"❌ API did not return an array as expected. Got: {type(data)}")
            except json.JSONDecodeError:
                print(f"❌ API response is not valid JSON")
                print(f"Response: {response.text[:200]}...")
        else:
            print(f"❌ Alert API returned error status: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
    except requests.exceptions.ConnectionError:
        print(f"❌ Could not connect to server at {base_url}")
        print("   Make sure the server is running (python start.py)")
    except requests.exceptions.Timeout:
        print(f"❌ Request to {base_url} timed out")
        print("   Server might be overloaded or unresponsive")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")

def check_log_files():
    """Check log files for relevant information about alerts and honeypots."""
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    
    if not os.path.exists(log_dir):
        print(f"❌ Log directory not found at {log_dir}")
        return
    
    print(f"\nChecking log files in {log_dir}...")
    
    log_files = [f for f in os.listdir(log_dir) if f.endswith('.log')]
    if not log_files:
        print("❌ No log files found")
        return
    
    print(f"✅ Found {len(log_files)} log files")
    
    # Check for honeypot activity in logs
    honeypot_active = False
    server_active = False
    alert_records = False
    
    for log_file in log_files:
        file_path = os.path.join(log_dir, log_file)
        print(f"\nExamining {log_file}...")
        
        try:
            with open(file_path, 'r') as f:
                log_content = f.read()
                
                # Check for key indicators in logs
                if "honeypot" in log_file.lower():
                    if "started" in log_content and "listening" in log_content:
                        honeypot_active = True
                        print(f"✅ Honeypot appears to be active")
                    
                    if "activity recorded" in log_content.lower():
                        print(f"✅ Detected attack activity in logs")
                    
                    if "alert sent to api" in log_content.lower():
                        alert_records = True
                        print(f"✅ Alerts are being sent to API")
                
                if "server" in log_file.lower():
                    if "starting honeypot server" in log_content.lower():
                        server_active = True
                        print(f"✅ Server has been started")
                    
                    if "new alert received" in log_content.lower():
                        alert_records = True
                        print(f"✅ Server is receiving alerts")
                
                # Extract the last few lines with alert information
                alert_lines = [line for line in log_content.splitlines() if "alert" in line.lower()]
                if alert_lines:
                    print(f"\nLast few alert-related log entries:")
                    for line in alert_lines[-5:]:  # Show last 5 alert-related log lines
                        print(f"  {line}")
        except Exception as e:
            print(f"❌ Error reading log file {log_file}: {str(e)}")
    
    if not honeypot_active:
        print("\n⚠️ No evidence found that honeypots are active")
    
    if not server_active:
        print("\n⚠️ No evidence found that the server is running")
    
    if not alert_records:
        print("\n⚠️ No evidence found of alerts being processed")

def simulate_test_alert():
    """Simulate a test alert to verify the alert system."""
    print("\nSimulating a test alert to verify the alert system...")
    
    try:
        test_alert = {
            "timestamp": datetime.now().isoformat(),
            "data": {
                "source_ip": "127.0.0.1",
                "attack_type": "Test Alert",
                "details": {
                    "method": "GET",
                    "path": "/diagnostic-test",
                    "headers": {
                        "User-Agent": "Diagnostic-Tool/1.0"
                    },
                    "time": datetime.now().isoformat()
                }
            }
        }
        
        response = requests.post(
            "http://localhost:8000/honeypot/test-honeypot-1/alert", 
            json=test_alert,
            timeout=5
        )
        
        if response.status_code == 200:
            print(f"✅ Test alert was successfully sent to the server")
            print(f"✅ Server responded with status code: {response.status_code}")
            try:
                result = response.json()
                print(f"✅ Server processed the alert and added analysis")
                if "analysis" in result:
                    print(f"   Threat level: {result['analysis'].get('threat_level_label', 'Unknown')}")
            except:
                print(f"⚠️ Server response could not be parsed as JSON")
        else:
            print(f"❌ Failed to send test alert. Status code: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
    except Exception as e:
        print(f"❌ Error simulating test alert: {str(e)}")

def main():
    """Main function to run diagnostic checks."""
    print("=" * 70)
    print(f"AI Honeypot Alert System Diagnostic - {datetime.now()}")
    print("=" * 70)
    
    # Check if alert API is working
    check_alert_api()
    
    # Check log files for relevant information
    check_log_files()
    
    # Simulate a test alert
    simulate_test_alert()
    
    print("\n" + "=" * 70)
    print("Diagnostic Completed. If issues persist, check that:")
    print("1. The honeypot backend server is running (python start.py)")
    print("2. Both SSH and Web honeypots are properly configured")
    print("3. Attack simulators are targeting the correct ports (SSH: 2222, Web: 8080)")
    print("4. The frontend dashboard is connected to the correct API URL")
    print("5. There are no network issues blocking connections to the server")
    print("=" * 70)

if __name__ == "__main__":
    main()
