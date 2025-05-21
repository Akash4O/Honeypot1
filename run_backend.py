#!/usr/bin/env python
"""
Run backend server with debugging options
"""

import os
import sys
import logging
import uvicorn
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("backend_runner")

def main():
    """Run the backend server with debugging."""
    print("=" * 70)
    print(f"AI HoneyPot Backend Server - {datetime.now()}")
    print("=" * 70)
    
    # Ensure the logs directory exists
    if not os.path.exists('logs'):
        os.makedirs('logs')
        print(f"Created logs directory")
    
    # Add the project root to the Python path
    project_root = os.path.dirname(os.path.abspath(__file__))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
        print(f"Added {project_root} to Python path")
    
    print("Starting FastAPI server...")
    print("The server will keep running until you press Ctrl+C")
    print("Access the API at http://localhost:8000")
    print("=" * 70)
    
    # Run the server directly with uvicorn
    uvicorn.run(
        "server:app", 
        host="0.0.0.0", 
        port=8000, 
        log_level="debug",
        reload=False
    )

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error running server: {str(e)}")
