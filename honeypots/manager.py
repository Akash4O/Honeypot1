import asyncio
import logging
import json
from datetime import datetime
import os
import yaml
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logging_config import setup_logger
from honeypots.ssh_honeypot import SSHHoneypot
from honeypots.web_honeypot import WebHoneypot
from ai_engine.analyzer import AIAnalyzer

logger = setup_logger("honeypot.manager")

class HoneypotManager:
    """
    Manages the creation, configuration, and orchestration of multiple honeypots.
    Acts as the central component of the honeypot system.
    """
    
    def __init__(self, config_file=None):
        """
        Initialize the honeypot manager.
        
        Args:
            config_file (str, optional): Path to configuration file
        """
        self.honeypots = {}
        self.config = {}
        self.running = False
        self.ai_analyzer = AIAnalyzer()
        
        # Load configuration if provided
        if config_file and os.path.exists(config_file):
            self.load_config(config_file)
        else:
            # Use default configuration
            self.config = {
                "honeypots": [
                    {
                        "id": "ssh-honeypot-1",
                        "type": "SSH",
                        "ip": "0.0.0.0",
                        "port": 2222,  # Use non-privileged port for SSH
                        "options": {
                            "banner": "SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.5"
                        }
                    },
                    {
                        "id": "web-honeypot-1",
                        "type": "Web",
                        "ip": "0.0.0.0",
                        "port": 8089,  # Use non-privileged port for HTTP (changed from 8080 to avoid conflicts)
                        "options": {
                            "server_type": "Apache/2.4.41 (Ubuntu)"
                        }
                    }
                ]
            }
    
    def load_config(self, config_file):
        """
        Load configuration from a YAML file.
        
        Args:
            config_file (str): Path to configuration file
        """
        try:
            with open(config_file, 'r') as f:
                self.config = yaml.safe_load(f)
                logger.info(f"Configuration loaded from {config_file}")
        except Exception as e:
            logger.error(f"Failed to load configuration: {str(e)}")
            # Use default config as fallback
            self.config = {"honeypots": []}
    
    def save_config(self, config_file):
        """
        Save current configuration to a YAML file.
        
        Args:
            config_file (str): Path to save configuration
        """
        try:
            with open(config_file, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False)
                logger.info(f"Configuration saved to {config_file}")
        except Exception as e:
            logger.error(f"Failed to save configuration: {str(e)}")
    
    def create_honeypot(self, honeypot_id, honeypot_type, ip, port, **options):
        """
        Create a new honeypot instance.
        
        Args:
            honeypot_id (str): Unique identifier for the honeypot
            honeypot_type (str): Type of honeypot (SSH, Web, etc.)
            ip (str): IP address to listen on
            port (int): Port to listen on
            **options: Additional options for the honeypot
            
        Returns:
            BaseHoneypot: The created honeypot instance
        """
        if honeypot_id in self.honeypots:
            logger.warning(f"Honeypot with ID {honeypot_id} already exists")
            return self.honeypots[honeypot_id]
        
        honeypot = None
        
        try:
            if honeypot_type.upper() == "SSH":
                honeypot = SSHHoneypot(honeypot_id, ip, port, **options)
            elif honeypot_type.upper() == "WEB":
                honeypot = WebHoneypot(honeypot_id, ip, port, **options)
            else:
                logger.error(f"Unsupported honeypot type: {honeypot_type}")
                return None
            
            self.honeypots[honeypot_id] = honeypot
            logger.info(f"Created {honeypot_type} honeypot with ID {honeypot_id}")
            
            # Add to configuration if not already there
            if not any(h["id"] == honeypot_id for h in self.config.get("honeypots", [])):
                self.config.setdefault("honeypots", []).append({
                    "id": honeypot_id,
                    "type": honeypot_type,
                    "ip": ip,
                    "port": port,
                    "options": options
                })
                
            return honeypot
        except Exception as e:
            logger.error(f"Failed to create honeypot: {str(e)}")
            return None
    
    def remove_honeypot(self, honeypot_id):
        """
        Remove a honeypot by ID.
        
        Args:
            honeypot_id (str): ID of the honeypot to remove
            
        Returns:
            bool: True if successful, False otherwise
        """
        if honeypot_id not in self.honeypots:
            logger.warning(f"Honeypot with ID {honeypot_id} does not exist")
            return False
        
        honeypot = self.honeypots[honeypot_id]
        
        try:
            if honeypot.status == "Active":
                # Schedule honeypot for stopping
                asyncio.create_task(honeypot.stop())
                
            del self.honeypots[honeypot_id]
            
            # Remove from configuration
            self.config["honeypots"] = [
                h for h in self.config.get("honeypots", [])
                if h["id"] != honeypot_id
            ]
            
            logger.info(f"Removed honeypot with ID {honeypot_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to remove honeypot: {str(e)}")
            return False
    
    def get_honeypot(self, honeypot_id):
        """
        Get a honeypot by ID.
        
        Args:
            honeypot_id (str): ID of the honeypot
            
        Returns:
            BaseHoneypot: The honeypot instance
        """
        return self.honeypots.get(honeypot_id)
    
    def get_all_honeypots(self):
        """
        Get all honeypot instances.
        
        Returns:
            dict: Dictionary of honeypot instances
        """
        return self.honeypots
    
    def get_honeypot_status(self, honeypot_id=None):
        """
        Get honeypot status.
        
        Args:
            honeypot_id (str, optional): ID of the honeypot to get status for
            
        Returns:
            dict: Status information
        """
        if honeypot_id:
            honeypot = self.get_honeypot(honeypot_id)
            if honeypot:
                return honeypot.get_status()
            return None
        
        # Get status for all honeypots
        status = {}
        for hid, honeypot in self.honeypots.items():
            status[hid] = honeypot.get_status()
        return status
    
    async def start_all(self):
        """Start all configured honeypots."""
        self.running = True
        tasks = []
        
        # Load honeypots from configuration if not already loaded
        for honeypot_config in self.config.get("honeypots", []):
            honeypot_id = honeypot_config["id"]
            if honeypot_id not in self.honeypots:
                self.create_honeypot(
                    honeypot_id,
                    honeypot_config["type"],
                    honeypot_config.get("ip", "0.0.0.0"),
                    honeypot_config.get("port", 0),
                    **honeypot_config.get("options", {})
                )
        
        # Start each honeypot
        for honeypot_id, honeypot in self.honeypots.items():
            logger.info(f"Starting honeypot {honeypot_id}")
            task = asyncio.create_task(honeypot.start())
            tasks.append(task)
        
        # Wait for all tasks to complete
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def stop_all(self):
        """Stop all running honeypots."""
        self.running = False
        tasks = []
        
        for honeypot_id, honeypot in self.honeypots.items():
            if honeypot.status == "Active":
                logger.info(f"Stopping honeypot {honeypot_id}")
                task = asyncio.create_task(honeypot.stop())
                tasks.append(task)
        
        # Wait for all tasks to complete
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def start_honeypot(self, honeypot_id):
        """
        Start a specific honeypot.
        
        Args:
            honeypot_id (str): ID of the honeypot to start
            
        Returns:
            bool: True if successful, False otherwise
        """
        honeypot = self.get_honeypot(honeypot_id)
        if not honeypot:
            logger.warning(f"Honeypot with ID {honeypot_id} does not exist")
            return False
        
        try:
            if honeypot.status != "Active":
                await honeypot.start()
                logger.info(f"Started honeypot {honeypot_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to start honeypot {honeypot_id}: {str(e)}")
            return False
    
    async def stop_honeypot(self, honeypot_id):
        """
        Stop a specific honeypot.
        
        Args:
            honeypot_id (str): ID of the honeypot to stop
            
        Returns:
            bool: True if successful, False otherwise
        """
        honeypot = self.get_honeypot(honeypot_id)
        if not honeypot:
            logger.warning(f"Honeypot with ID {honeypot_id} does not exist")
            return False
        
        try:
            if honeypot.status == "Active":
                await honeypot.stop()
                logger.info(f"Stopped honeypot {honeypot_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to stop honeypot {honeypot_id}: {str(e)}")
            return False
    
    def analyze_event(self, event):
        """
        Analyze a honeypot event using the AI engine.
        
        Args:
            event (dict): Honeypot event data
            
        Returns:
            dict: Analysis results
        """
        return self.ai_analyzer.analyze_event(event)
    
    def get_threat_intelligence(self):
        """
        Get threat intelligence report.
        
        Returns:
            dict: Threat intelligence report
        """
        return self.ai_analyzer.get_threat_intelligence()
