import subprocess
import os
import sys
import time
import signal
import webbrowser
from datetime import datetime

def start_backend():
    """Start the backend server"""
    print("[+] Starting AI HoneyPot backend server...")
    # Create a modified environment that includes the project root in PYTHONPATH
    env = os.environ.copy()
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # On Windows, use a semicolon as the path separator
    if 'PYTHONPATH' in env:
        env['PYTHONPATH'] = f"{project_root};{env['PYTHONPATH']}"
    else:
        env['PYTHONPATH'] = project_root
    
    backend_process = subprocess.Popen([sys.executable, "server.py"], 
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE,
                                       env=env)
    time.sleep(2)  # Give the server time to start
    
    # Check if the process is still running
    if backend_process.poll() is None:
        print("[+] Backend server started successfully")
        return backend_process
    else:
        print("[!] Failed to start backend server")
        stdout, stderr = backend_process.communicate()
        print(f"Error: {stderr.decode('utf-8')}")
        return None

def start_frontend():
    """Start the frontend development server"""
    print("[+] Starting AI HoneyPot frontend...")
    os.chdir("frontend")
    npm_path = r"C:\Program Files\nodejs\npm.ps1"
    # Use PowerShell to execute the npm.ps1 script
    frontend_process = subprocess.Popen(["powershell", "-ExecutionPolicy", "Bypass", "-File", npm_path, "start"], 
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
    os.chdir("..")
    
    # Give the server time to start
    time.sleep(5)
    
    # Check if the process is still running
    if frontend_process.poll() is None:
        print("[+] Frontend server started successfully")
        return frontend_process
    else:
        print("[!] Failed to start frontend server")
        stdout, stderr = frontend_process.communicate()
        print(f"Error: {stderr.decode('utf-8')}")
        return None

def main():
    """Main function to start the entire system"""
    print("=" * 50)
    print(f"AI HoneyPot System Startup - {datetime.now()}")
    print("=" * 50)
    
    try:
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
        webbrowser.open("http://localhost:3000")
        
        print("\n[+] AI HoneyPot System is running")
        print("[+] Backend API: http://localhost:8000")
        print("[+] Frontend Dashboard: http://localhost:3000")
        print("[+] Press Ctrl+C to stop all services")
        
        # Keep the script running until Ctrl+C
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n[+] Stopping AI HoneyPot System...")
        
        # Stop the processes
        if 'frontend_process' in locals() and frontend_process:
            frontend_process.terminate()
            
        if 'backend_process' in locals() and backend_process:
            backend_process.terminate()
            
        print("[+] All services stopped")

if __name__ == "__main__":
    main()
