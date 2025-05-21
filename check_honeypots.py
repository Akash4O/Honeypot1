#!/usr/bin/env python
"""
Honeypot Status Checker

This utility checks if the honeypots are running and accessible.
"""

import requests
import socket
import sys
import time

def check_web_honeypot(host="localhost", port=8080):
    """Check if the web honeypot is running."""
    try:
        # Try to connect to the web honeypot
        url = f"http://{host}:{port}"
        response = requests.get(url, timeout=5)
        
        # If we get here, the connection succeeded
        print(f"✅ Web honeypot is running on {url}")
        print(f"   Status code: {response.status_code}")
        print(f"   Response size: {len(response.text)} bytes")
        return True
    except requests.RequestException as e:
        print(f"❌ Web honeypot is not accessible on {url}")
        print(f"   Error: {str(e)}")
        return False

def check_ssh_honeypot(host="localhost", port=2222):
    """Check if the SSH honeypot is running."""
    try:
        # Try to connect to the SSH honeypot
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect((host, port))
        
        # Wait for banner
        banner = s.recv(1024).decode('utf-8', errors='ignore')
        s.close()
        
        # If we get here, the connection succeeded
        print(f"✅ SSH honeypot is running on {host}:{port}")
        print(f"   Banner: {banner.strip()}")
        return True
    except socket.error as e:
        print(f"❌ SSH honeypot is not accessible on {host}:{port}")
        print(f"   Error: {str(e)}")
        return False

def main():
    """Main function to check honeypot status."""
    print("=" * 60)
    print("Honeypot Status Checker")
    print("=" * 60)
    
    # Give the honeypots time to start if they were just launched
    print("Waiting 5 seconds for honeypots to initialize...")
    time.sleep(5)
    
    # Check SSH honeypot
    ssh_status = check_ssh_honeypot()
    print()
    
    # Check Web honeypot
    web_status = check_web_honeypot()
    
    print("\n" + "=" * 60)
    if ssh_status and web_status:
        print("✅ All honeypots are running correctly!")
    else:
        print("⚠️ Some honeypots are not running properly.")
        print("Please check the server logs for more details.")

if __name__ == "__main__":
    main()
