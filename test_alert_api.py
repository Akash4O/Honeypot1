#!/usr/bin/env python
"""
Alert API Test Tool

This utility tests the alert flow from honeypots to the server and dashboard.
"""

import requests
import json
import time
import sys
from datetime import datetime

def test_create_alert():
    """Test creating a test alert directly via the API."""
    print("\nTesting alert creation API...")
    
    # Create a test alert
    test_alert = {
        "timestamp": datetime.now().isoformat(),
        "data": {
            "source_ip": "192.168.1.100",
            "attack_type": "Test Attack",
            "details": {
                "method": "TEST",
                "path": "/diagnostic-test",
                "headers": {
                    "User-Agent": "AlertTestTool/1.0"
                }
            }
        }
    }
    
    try:
        print("Sending test alert to server...")
        # Use the test honeypot ID for this test
        response = requests.post(
            "http://localhost:8000/honeypot/test-honeypot-1/alert",
            json=test_alert,
            timeout=5
        )
        
        if response.status_code == 200:
            print(f"✅ Test alert successfully created (status {response.status_code})")
            try:
                alert_response = response.json()
                print(f"✅ Received valid response: {json.dumps(alert_response, indent=2)}")
                print("\nAnalysis details:")
                if "analysis" in alert_response:
                    analysis = alert_response["analysis"]
                    print(f"  Threat level: {analysis.get('threat_level_label')}")
                    print(f"  Attack type: {analysis.get('attack_type')}")
                    if "recommendations" in analysis:
                        print(f"  Recommendations: {analysis['recommendations']}")
                else:
                    print("  No analysis data in response")
            except json.JSONDecodeError:
                print(f"❌ Invalid JSON response: {response.text[:200]}")
        else:
            print(f"❌ Failed to create alert. Status: {response.status_code}")
            print(f"Response: {response.text}")
    except requests.exceptions.ConnectionError:
        print(f"❌ Could not connect to server at http://localhost:8000")
        print("  Make sure the server is running (python start.py)")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_get_alerts():
    """Test getting alerts from the API."""
    print("\nTesting get alerts API...")
    
    try:
        response = requests.get("http://localhost:8000/alerts", timeout=5)
        
        if response.status_code == 200:
            print(f"✅ Successfully retrieved alerts (status {response.status_code})")
            try:
                alerts = response.json()
                if isinstance(alerts, list):
                    print(f"✅ Received {len(alerts)} alerts")
                    if alerts:
                        print("\nLatest alert:")
                        latest = alerts[-1]
                        print(f"  Honeypot: {latest.get('honeypot_id')}")
                        print(f"  Timestamp: {latest.get('timestamp')}")
                        print(f"  Source IP: {latest.get('data', {}).get('source_ip')}")
                        print(f"  Attack type: {latest.get('data', {}).get('attack_type')}")
                    else:
                        print("❌ No alerts found - this is the likely cause of your empty dashboard")
                else:
                    print(f"❌ Expected a list but got {type(alerts)}")
                    print(f"Response: {json.dumps(alerts)[:200]}")
            except json.JSONDecodeError:
                print(f"❌ Invalid JSON response: {response.text[:200]}")
        else:
            print(f"❌ Failed to get alerts. Status: {response.status_code}")
            print(f"Response: {response.text}")
    except requests.exceptions.ConnectionError:
        print(f"❌ Could not connect to server at http://localhost:8000")
        print("  Make sure the server is running (python start.py)")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_alert_flow():
    """Perform an end-to-end test of the alert flow."""
    print("\n" + "="*70)
    print("TESTING ALERT FLOW FROM CREATION TO RETRIEVAL")
    print("="*70)
    
    # First, get the current alert count
    try:
        before_response = requests.get("http://localhost:8000/alerts", timeout=5)
        before_count = 0
        if before_response.status_code == 200:
            before_alerts = before_response.json()
            if isinstance(before_alerts, list):
                before_count = len(before_alerts)
                print(f"Current alert count: {before_count}")
    except Exception:
        print("Failed to get current alert count, continuing with test...")
    
    # Create a new alert with unique marker
    test_id = f"test-{int(time.time())}"
    test_alert = {
        "timestamp": datetime.now().isoformat(),
        "data": {
            "source_ip": "10.0.0.99",
            "attack_type": f"Flow Test {test_id}",
            "details": {
                "test_id": test_id,
                "method": "TEST",
                "path": "/flow-test"
            }
        }
    }
    
    print(f"\nCreating test alert with ID: {test_id}")
    try:
        create_response = requests.post(
            "http://localhost:8000/honeypot/flow-test-honeypot/alert",
            json=test_alert,
            timeout=5
        )
        
        if create_response.status_code != 200:
            print(f"❌ Failed to create alert. Status: {create_response.status_code}")
            return
        
        print("✅ Test alert created successfully")
        
        # Give the server a moment to process
        print("Waiting 2 seconds for server processing...")
        time.sleep(2)
        
        # Now check if our alert appears in the list
        after_response = requests.get("http://localhost:8000/alerts", timeout=5)
        if after_response.status_code != 200:
            print(f"❌ Failed to retrieve alerts. Status: {after_response.status_code}")
            return
        
        after_alerts = after_response.json()
        if not isinstance(after_alerts, list):
            print(f"❌ Expected a list of alerts but got {type(after_alerts)}")
            return
        
        after_count = len(after_alerts)
        print(f"Updated alert count: {after_count}")
        
        if after_count <= before_count:
            print("❌ Alert count did not increase after creating test alert")
            print("  This suggests the alert was not properly saved")
        else:
            print(f"✅ Alert count increased ({before_count} → {after_count})")
        
        # Look for our specific test alert
        found = False
        for alert in after_alerts:
            if alert.get('data', {}).get('attack_type') == f"Flow Test {test_id}":
                found = True
                print("✅ Found our test alert in the alerts list!")
                print("\nAlert details:")
                print(f"  Honeypot: {alert.get('honeypot_id')}")
                print(f"  Timestamp: {alert.get('timestamp')}")
                print(f"  Analysis: {json.dumps(alert.get('analysis', {}), indent=2)[:200]}...")
                break
        
        if not found:
            print("❌ Could not find our test alert in the alerts list")
            print("  This suggests an issue with alert storage or retrieval")
            
    except Exception as e:
        print(f"❌ Error during flow test: {str(e)}")
    
    print("\n" + "="*70)
    print("TEST COMPLETED")
    print("="*70)
    print("\nIf all tests passed, your alerts should appear in the dashboard.")
    print("If tests failed, check the error messages above for troubleshooting.")

def main():
    print("=" * 70)
    print(f"AI Honeypot Alert System Test - {datetime.now()}")
    print("=" * 70)
    print("This tool tests different parts of the alert system.")
    print("Use this to diagnose issues with alerts not appearing.")
    
    # Test getting alerts
    test_get_alerts()
    
    # Test creating an alert
    test_create_alert()
    
    # Test the entire alert flow
    test_alert_flow()
    
    print("\n" + "=" * 70)
    print("NEXT STEPS:")
    print("1. If all tests passed but still no alerts in dashboard, restart the frontend server")
    print("2. If alert creation failed, check server logs and honeypot configuration")
    print("3. If alert retrieval failed, the frontend may be connecting to the wrong URL")
    print("4. Run the attack simulators AFTER confirming the alert system works")
    print("=" * 70)

if __name__ == "__main__":
    main()
