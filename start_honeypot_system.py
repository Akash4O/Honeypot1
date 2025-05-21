#!/usr/bin/env python
"""
AI HoneyPot System Starter

This script provides a resilient way to start the complete honeypot system
including the backend API server, honeypots, and frontend dashboard.
"""

import os
import sys
import time
import signal
import subprocess
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("honeypot_starter")

# Configuration
BACKEND_PORT = 8000
FRONTEND_PORT = 3000
SSH_HONEYPOT_PORT = 2222
WEB_HONEYPOT_PORT = 8089  # Changed from 8080 to avoid conflicts

class HoneypotSystem:
    """Manages the entire honeypot system."""
    
    def __init__(self):
        """Initialize the honeypot system."""
        self.backend_process = None
        self.frontend_process = None
        self.running = False
        
        # Get project root directory
        self.project_root = os.path.dirname(os.path.abspath(__file__))
        
        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, sig, frame):
        """Handle termination signals."""
        logger.info(f"Received signal {sig}, shutting down...")
        self.stop()
        sys.exit(0)
    
    def start_backend(self):
        """Start the backend server."""
        logger.info("Starting backend server...")
        
        # Set up environment
        env = os.environ.copy()
        env['PYTHONPATH'] = self.project_root
        
        # Start the backend server
        self.backend_process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "server:app", "--host", "0.0.0.0", 
             "--port", str(BACKEND_PORT), "--log-level", "info"],
            cwd=self.project_root,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        
        # Give it a moment to start
        time.sleep(3)
        
        # Check if process is still running
        if self.backend_process.poll() is not None:
            stdout, _ = self.backend_process.communicate()
            logger.error(f"Backend server failed to start: {stdout.decode('utf-8')}")
            return False
        
        logger.info(f"Backend server started on http://localhost:{BACKEND_PORT}")
        return True
    
    def start_frontend(self):
        """Start the frontend server."""
        logger.info("Starting frontend server...")
        
        # Change to frontend directory
        frontend_dir = os.path.join(self.project_root, "frontend")
        if not os.path.exists(frontend_dir):
            logger.error(f"Frontend directory not found at {frontend_dir}")
            return False
        
        # Use the full path to npm.ps1 as specified in the memory
        npm_path = r"C:\Program Files\nodejs\npm.ps1"
        
        # Start the frontend server
        self.frontend_process = subprocess.Popen(
            ["powershell", "-ExecutionPolicy", "Bypass", "-File", npm_path, "start"],
            cwd=frontend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        
        # Wait for frontend to start
        logger.info("Waiting for frontend to initialize (15 seconds)...")
        time.sleep(15)
        
        # Check if process is still running
        if self.frontend_process.poll() is not None:
            stdout, _ = self.frontend_process.communicate()
            logger.error(f"Frontend server failed to start: {stdout.decode('utf-8')}")
            return False
        
        logger.info(f"Frontend server started on http://localhost:{FRONTEND_PORT}")
        return True
    
    def start(self):
        """Start the entire honeypot system."""
        print("=" * 70)
        print(f"AI HoneyPot System Startup - {datetime.now()}")
        print("=" * 70)
        
        # Make sure logs directory exists
        logs_dir = os.path.join(self.project_root, "logs")
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
            logger.info(f"Created logs directory at {logs_dir}")
        
        # Start backend
        if not self.start_backend():
            logger.error("Failed to start backend server")
            return False
        
        # Start frontend
        if not self.start_frontend():
            logger.warning("Failed to start frontend server")
            # Continue anyway - the backend is more important
        
        # Open browser
        logger.info("Opening dashboard in browser...")
        try:
            import webbrowser
            webbrowser.open(f"http://localhost:{FRONTEND_PORT}")
        except Exception as e:
            logger.warning(f"Failed to open browser: {e}")
        
        self.running = True
        
        print("\n" + "=" * 70)
        print(f"AI HoneyPot System is running")
        print(f"Backend API: http://localhost:{BACKEND_PORT}")
        print(f"Frontend Dashboard: http://localhost:{FRONTEND_PORT}")
        print(f"SSH Honeypot: localhost:{SSH_HONEYPOT_PORT}")
        print(f"Web Honeypot: http://localhost:{WEB_HONEYPOT_PORT}")
        print("=" * 70)
        print("Press Ctrl+C to stop all services")
        
        return True
    
    def stop(self):
        """Stop the entire honeypot system."""
        print("\n" + "=" * 70)
        print("Stopping AI HoneyPot System...")
        
        # Stop frontend
        if self.frontend_process:
            logger.info("Stopping frontend server...")
            try:
                self.frontend_process.terminate()
                self.frontend_process.wait(timeout=5)
            except Exception as e:
                logger.warning(f"Error stopping frontend: {e}")
                try:
                    self.frontend_process.kill()
                except:
                    pass
        
        # Stop backend
        if self.backend_process:
            logger.info("Stopping backend server...")
            try:
                self.backend_process.terminate()
                self.backend_process.wait(timeout=5)
            except Exception as e:
                logger.warning(f"Error stopping backend: {e}")
                try:
                    self.backend_process.kill()
                except:
                    pass
        
        self.running = False
        print("All services stopped")
        print("=" * 70)
    
    def run(self):
        """Run the honeypot system and keep it running."""
        if not self.start():
            logger.error("Failed to start honeypot system")
            return False
        
        try:
            # Keep the script running until Ctrl+C
            while self.running:
                time.sleep(1)
                
                # Check if processes are still running
                if self.backend_process and self.backend_process.poll() is not None:
                    logger.error("Backend server has terminated unexpectedly")
                    break
                
                if self.frontend_process and self.frontend_process.poll() is not None:
                    logger.warning("Frontend server has terminated")
                    # Don't exit, the backend is more important
        
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        finally:
            self.stop()
        
        return True

def main():
    """Main entry point."""
    honeypot_system = HoneypotSystem()
    honeypot_system.run()

if __name__ == "__main__":
    main()
