import abc
import logging
import time
import json
import asyncio
from datetime import datetime
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logging_config import setup_logger

logger = setup_logger("honeypot")

class BaseHoneypot(abc.ABC):
    """
    Abstract base class for all honeypot implementations.
    Provides common functionality and interface for specific honeypot types.
    """
    
    def __init__(self, honeypot_id, ip, port):
        """
        Initialize a new honeypot instance.
        
        Args:
            honeypot_id (str): Unique identifier for this honeypot
            ip (str): IP address for the honeypot to listen on
            port (int): Port for the honeypot to listen on
        """
        self.id = honeypot_id
        self.ip = ip
        self.port = port
        self.status = "Inactive"
        self.connections = 0
        self.last_activity = datetime.now().isoformat()
        self.attack_events = []
        self.running = False
        self.server = None
        
    @abc.abstractmethod
    async def start(self):
        """Start the honeypot service."""
        self.status = "Active"
        self.running = True
        logger.info(f"Honeypot {self.id} started on {self.ip}:{self.port}")
    
    @abc.abstractmethod
    async def stop(self):
        """Stop the honeypot service."""
        self.status = "Inactive"
        self.running = False
        logger.info(f"Honeypot {self.id} stopped")
    
    def get_status(self):
        """Get the current status of the honeypot."""
        return {
            "id": self.id,
            "type": self.__class__.__name__,
            "status": self.status,
            "ip": self.ip,
            "port": self.port,
            "connections": self.connections,
            "last_activity": self.last_activity
        }
    
    async def record_activity(self, source_ip, data, attack_type=None):
        """
        Record activity detected by the honeypot.
        
        Args:
            source_ip (str): Source IP of the connection
            data (dict): Data captured from the connection
            attack_type (str, optional): Type of attack if detected
        """
        self.connections += 1
        self.last_activity = datetime.now().isoformat()
        
        event = {
            "honeypot_id": self.id,
            "timestamp": self.last_activity,
            "data": {
                "source_ip": source_ip,
                "attack_type": attack_type or "Unknown",
                "details": data
            }
        }
        
        self.attack_events.append(event)
        logger.info(f"Activity recorded from {source_ip} on {self.id}")
        
        # Send this event to the central API
        await self._send_alert(event)
    
    async def _send_alert(self, event):
        """Send alert data to the central API."""
        try:
            # Use aiohttp to send the data to the central API endpoint
            import aiohttp
            
            # Construct the API endpoint URL
            api_url = f"http://localhost:8000/honeypot/{self.id}/alert"
            
            logger.info(f"Sending alert to API: {api_url}")
            
            # Ensure the event data is in the correct format
            if 'data' not in event and 'timestamp' not in event:
                # We need to format this as API expects
                api_payload = {
                    "timestamp": datetime.now().isoformat(),
                    "data": event
                }
            else:
                api_payload = event
            
            # Make the actual HTTP request to the API
            async with aiohttp.ClientSession() as session:
                async with session.post(api_url, json=api_payload) as response:
                    if response.status == 200:
                        logger.info(f"Alert successfully sent to API: {self.id}")
                        # Log success with the response
                        response_text = await response.text()
                        logger.info(f"API Response: {response_text}")
                    else:
                        logger.error(f"Failed to send alert: HTTP {response.status}")
                        response_text = await response.text()
                        logger.error(f"Error Response: {response_text}")
            
            # Log the event details for debugging
            logger.info(f"Alert details sent: {json.dumps(api_payload)}")
            
        except Exception as e:
            logger.error(f"Failed to send alert: {str(e)}")
            logger.error(f"Alert that failed: {json.dumps(event)}")
            # For debugging, print the full exception info
            import traceback
            logger.error(f"Exception traceback: {traceback.format_exc()}")
            
            # Make sure the server is running
            logger.error("Make sure the backend server is running at http://localhost:8000")
