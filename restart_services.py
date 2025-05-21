#!/usr/bin/env python
"""
Restart honeypot services by ensuring ports are available
"""

import os
import sys
import subprocess
import time
import socket
from datetime import datetime

def check_port_in_use(port):
    """Check if a port is in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def kill_process_on_port(port):
    """Kill any process using the specified port."""
    try:
        # Use netstat to find the process ID using the port
        output = subprocess.check_output(
            f"netstat -ano | findstr :{port}", 
            shell=True
        ).decode()
        
        # Extract the PID from the output
        for line in output.split('\n'):
            if f":{port}" in line:
                parts = line.strip().split()
                if len(parts) >= 5:
                    pid = parts[4]
                    print(f"Found process {pid} using port {port}")
                    
                    # Kill the process
                    subprocess.run(f"taskkill /F /PID {pid}", shell=True)
                    print(f"Killed process {pid}")
                    return True
        
        return False
    except subprocess.CalledProcessError:
        # No process found
        return False

def ensure_port_available(port):
    """Ensure the specified port is available."""
    if check_port_in_use(port):
        print(f"Port {port} is in use. Attempting to free it...")
        if kill_process_on_port(port):
            print(f"Successfully freed port {port}")
        else:
            print(f"Failed to free port {port}")
            return False
        
        # Double-check the port is now available
        time.sleep(2)
        if check_port_in_use(port):
            print(f"Port {port} is still in use. Cannot proceed.")
            return False
    
    return True

def start_backend():
    """Start the backend server."""
    print("[+] Starting AI HoneyPot backend server...")
    
    # Create a modified environment that includes the project root in PYTHONPATH
    env = os.environ.copy()
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # On Windows, use a semicolon as the path separator
    if 'PYTHONPATH' in env:
        env['PYTHONPATH'] = f"{project_root};{env['PYTHONPATH']}"
    else:
        env['PYTHONPATH'] = project_root
    
    # Start the server as a background process
    backend_process = subprocess.Popen(
        [sys.executable, "server.py"], 
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env
    )
    
    # Give the server time to start
    time.sleep(5)
    
    # Check if the process is still running
    if backend_process.poll() is None:
        # Check if the server is responding
        if check_port_in_use(8000):
            print("[+] Backend server started successfully")
            return backend_process
        else:
            print("[!] Backend server started but is not responding on port 8000")
            backend_process.terminate()
            return None
    else:
        stdout, stderr = backend_process.communicate()
        print("[!] Failed to start backend server")
        print(f"Error: {stderr.decode('utf-8')}")
        return None

def start_frontend():
    """Start the frontend development server."""
    print("[+] Starting AI HoneyPot frontend...")
    os.chdir("frontend")
    
    # Use the full path to npm.ps1 as specified in the memory
    npm_path = r"C:\Program Files\nodejs\npm.ps1"
    
    # Use PowerShell to execute the npm.ps1 script with execution policy bypass
    frontend_process = subprocess.Popen(
        ["powershell", "-ExecutionPolicy", "Bypass", "-File", npm_path, "start"], 
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    os.chdir("..")
    
    # Give the server time to start
    time.sleep(15)
    
    # Check if the process is still running
    if frontend_process.poll() is None:
        # Check if the server is responding
        if check_port_in_use(3000):
            print("[+] Frontend server started successfully")
            return frontend_process
        else:
            print("[!] Frontend server started but is not responding on port 3000")
            return None
    else:
        stdout, stderr = frontend_process.communicate()
        print("[!] Failed to start frontend server")
        print(f"Error: {stderr.decode('utf-8')}")
        return None

def main():
    """Main function to restart services."""
    print("=" * 70)
    print(f"AI HoneyPot System Restart - {datetime.now()}")
    print("=" * 70)
    
    # Ensure logs directory exists
    if not os.path.exists('logs'):
        os.makedirs('logs')
        print("[+] Created logs directory")
    
    # Check and free required ports
    backend_port = 8000
    frontend_port = 3000
    ssh_honeypot_port = 2222
    web_honeypot_port = 8089
    
    ports_to_check = [backend_port, frontend_port, ssh_honeypot_port, web_honeypot_port]
    print("Checking if required ports are available...")
    
    all_ports_available = True
    for port in ports_to_check:
        if not ensure_port_available(port):
            all_ports_available = False
    
    if not all_ports_available:
        print("Failed to free all required ports. Cannot proceed.")
        return
    
    print("All required ports are available. Starting services...")
    
    # Start the backend server
    backend_process = start_backend()
    if not backend_process:
        return
    
    # Start the frontend server
    frontend_process = start_frontend()
    if not frontend_process:
        backend_process.terminate()
        return
    
    # Open the browser
    print("[+] Opening dashboard in browser...")
    import webbrowser
    webbrowser.open("http://localhost:3000")
    
    print("\n[+] AI HoneyPot System is running")
    print("[+] Backend API: http://localhost:8000")
    print("[+] Frontend Dashboard: http://localhost:3000")
    print("[+] Press Ctrl+C to stop all services")
    
    try:
        # Keep the script running until Ctrl+C
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if backend_process.poll() is not None:
                print("[!] Backend server process has terminated")
                break
                
            if frontend_process.poll() is not None:
                print("[!] Frontend server process has terminated")
                break
                
    except KeyboardInterrupt:
        print("\n[+] Stopping AI HoneyPot System...")
    finally:
        # Stop the processes
        if 'frontend_process' in locals() and frontend_process:
            frontend_process.terminate()
            
        if 'backend_process' in locals() and backend_process:
            backend_process.terminate()
            
        print("[+] All services stopped")

if __name__ == "__main__":
    main()
