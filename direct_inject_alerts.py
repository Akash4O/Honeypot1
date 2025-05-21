#!/usr/bin/env python
"""
Direct Alert Injection

This script directly injects alerts into the backend server's alerts list
to demonstrate the alert display functionality.
"""

import requests
import json
import time
from datetime import datetime
import random
import os
import sys

# Generate some interesting random test alerts
def generate_alerts(count=10):
    alerts = []
    
    attack_types = [
        "SSH_BRUTE_FORCE", "COMMAND_INJECTION", "SQL_INJECTION", 
        "XSS_ATTACK", "PATH_TRAVERSAL", "ADMIN_LOGIN_ATTEMPT"
    ]
    
    source_ips = [
        "192.168.1.100", "10.0.0.25", "172.16.0.50", "45.33.20.15", 
        "23.94.17.212", "89.248.167.131", "5.188.206.18"
    ]
    
    honeypot_ids = ["ssh-honeypot-1", "web-honeypot-1"]
    
    threat_levels = ["Low", "Medium", "High", "Critical"]
    
    for i in range(count):
        honeypot_id = random.choice(honeypot_ids)
        attack_type = random.choice(attack_types)
        source_ip = random.choice(source_ips)
        threat_level = random.choice(range(4))  # 0-3
        threat_level_label = threat_levels[threat_level]
        
        # Create details based on attack type
        if "SSH" in attack_type:
            details = {
                "username": random.choice(["root", "admin", "user", "guest"]),
                "password": random.choice(["password123", "admin", "123456", "qwerty"]),
                "client_id": f"SSH-2.0-{random.choice(['OpenSSH', 'PuTTY', 'Metasploit'])}"
            }
        elif "SQL" in attack_type:
            details = {
                "url": "/login",
                "parameter": "username",
                "payload": random.choice(["' OR 1=1 --", "admin' --", "'; DROP TABLE users; --"])
            }
        elif "XSS" in attack_type:
            details = {
                "url": "/search",
                "parameter": "q",
                "payload": random.choice(["<script>alert('XSS')</script>", "<img src=x onerror=alert('XSS')>"])
            }
        elif "PATH" in attack_type:
            details = {
                "url": "/download",
                "parameter": "file",
                "payload": random.choice(["../../../etc/passwd", "../../../../etc/shadow"])
            }
        else:
            details = {
                "method": random.choice(["GET", "POST"]),
                "path": random.choice(["/admin", "/login", "/config", "/wp-admin"]),
                "headers": {
                    "User-Agent": random.choice([
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124",
                        "sqlmap/1.4.7",
                        "Nikto/2.1.6"
                    ])
                }
            }
        
        # Create alert
        alert = {
            "honeypot_id": honeypot_id,
            "timestamp": (datetime.now().replace(microsecond=0) - 
                         datetime.timedelta(minutes=random.randint(0, 60))).isoformat(),
            "data": {
                "source_ip": source_ip,
                "attack_type": attack_type,
                "details": details
            },
            "analysis": {
                "timestamp": datetime.now().isoformat(),
                "source_ip": source_ip,
                "honeypot_id": honeypot_id,
                "attack_type": attack_type,
                "threat_level": threat_level,
                "threat_level_label": threat_level_label,
                "attack_details": details,
                "is_known_attacker": random.choice([True, False]),
                "attack_count": random.randint(1, 20),
                "recommendations": [
                    "Update firewall rules to block this IP",
                    "Enable two-factor authentication",
                    "Update system with security patches"
                ]
            }
        }
        
        alerts.append(alert)
    
    return alerts

# Try to send the alert to the API
def send_alert_to_api(alert):
    """Try to send an alert to the API endpoint."""
    honeypot_id = alert["honeypot_id"]
    
    try:
        response = requests.post(
            f"http://localhost:8000/honeypot/{honeypot_id}/alert",
            json=alert,
            timeout=5
        )
        
        if response.status_code == 200:
            print(f"✅ Successfully sent alert to /honeypot/{honeypot_id}/alert")
            return True
        else:
            print(f"⚠️ Failed to send alert to API: {response.status_code}")
            return False
    except Exception as e:
        print(f"⚠️ Error sending alert to API: {str(e)}")
        return False

# Main function
def main():
    # Print banner
    print("="*80)
    print("DIRECT ALERT INJECTION TOOL".center(80))
    print("="*80)
    print(f"Started at: {datetime.now()}")
    print("="*80)
    
    # Generate alerts
    alert_count = 10
    print(f"Generating {alert_count} test alerts...")
    alerts = generate_alerts(alert_count)
    
    # Send alerts
    print(f"Sending alerts to backend API...")
    success_count = 0
    
    for i, alert in enumerate(alerts):
        print(f"Sending alert {i+1}/{len(alerts)}...")
        if send_alert_to_api(alert):
            success_count += 1
        time.sleep(0.5)  # Short delay between alerts
    
    # Summary
    print("="*80)
    print(f"Sent {success_count}/{alert_count} alerts successfully!")
    print("="*80)
    print("Next steps:")
    print("1. Check the dashboard at http://localhost:3000")
    print("2. If alerts don't appear, restart the system: python start.py")
    print("3. Run additional attack simulations: python run_simulations.py")
    print("="*80)

if __name__ == "__main__":
    main()
