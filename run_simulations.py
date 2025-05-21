#!/usr/bin/env python
"""
Honeypot Attack Simulation Runner

This script runs both SSH and Web attack simulations against the honeypots.
"""

import subprocess
import time
import sys
import os
from datetime import datetime

def main():
    """Run the honeypot attack simulations."""
    print("=" * 70)
    print(f"Honeypot Attack Simulation Runner - {datetime.now()}")
    print("=" * 70)
    
    print("First, make sure the honeypot system is running (python start.py)")
    print("Waiting 10 seconds for honeypots to fully initialize...")
    time.sleep(10)
    
    print("\nRunning SSH Attack Simulation:")
    ssh_simulator = subprocess.Popen(
        [sys.executable, "attack_simulators/ssh_attack_simulator.py", "--ip", "127.0.0.1", "--port", "2222"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Let it run for a bit
    time.sleep(30)
    
    print("\nRunning Web Attack Simulation:")
    web_simulator = subprocess.Popen(
        [sys.executable, "attack_simulators/web_attack_simulator.py", "--url", "http://127.0.0.1:8089"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Let it run for a bit
    time.sleep(30)
    
    print("\nSimulations completed! Check the dashboard for alerts.")
    print("If no alerts appear, check logs in the 'logs' directory.")
    
if __name__ == "__main__":
    main()
