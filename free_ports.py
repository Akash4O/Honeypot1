#!/usr/bin/env python
"""
Port Cleanup Utility

This script identifies and terminates processes using specific ports
to ensure they're available for the honeypot system.
"""

import os
import subprocess
import time
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("port_cleanup")

# Ports used by the honeypot system
PORTS = [8000, 3000, 8089, 2222]

def find_process_by_port(port):
    """Find process ID using specified port."""
    try:
        # Using netstat to find processes using the port
        output = subprocess.check_output(
            f"netstat -ano | findstr :{port}", 
            shell=True
        ).decode()
        
        for line in output.split('\n'):
            if line.strip():
                parts = line.strip().split()
                if len(parts) >= 5:
                    pid = parts[4]
                    return pid
        return None
    except subprocess.CalledProcessError:
        # No process found using this port
        return None

def kill_process(pid):
    """Kill a process by its ID."""
    try:
        result = subprocess.run(
            f"taskkill /F /PID {pid}", 
            shell=True, 
            capture_output=True, 
            text=True
        )
        if result.returncode == 0:
            logger.info(f"Process {pid} terminated successfully")
            return True
        else:
            logger.error(f"Failed to terminate process {pid}: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"Error terminating process {pid}: {str(e)}")
        return False

def main():
    """Main function."""
    print("=" * 70)
    print(f"Port Cleanup Utility - {datetime.now()}")
    print("=" * 70)
    print("This utility will identify and terminate processes using ports required by the honeypot system")
    print(f"Ports to free: {PORTS}")
    print("=" * 70)
    
    for port in PORTS:
        pid = find_process_by_port(port)
        if pid:
            print(f"Port {port} is in use by process {pid}")
            if kill_process(pid):
                print(f"✅ Successfully freed port {port}")
            else:
                print(f"❌ Failed to free port {port}")
        else:
            print(f"✅ Port {port} is already available")
    
    print("\n" + "=" * 70)
    print("Port cleanup complete")
    print("Now you can run the honeypot system")
    print("=" * 70)

if __name__ == "__main__":
    main()
