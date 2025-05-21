import asyncio
import logging
from datetime import datetime
import re
import json
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from honeypots.base import BaseHoneypot
from utils.logging_config import setup_logger

logger = setup_logger("honeypot.ssh")

class SSHHoneypot(BaseHoneypot):
    """
    SSH Honeypot implementation that simulates an SSH server and records login attempts.
    """
    
    def __init__(self, honeypot_id, ip="0.0.0.0", port=22, **kwargs):
        """
        Initialize a new SSH honeypot.
        
        Args:
            honeypot_id (str): Unique identifier for this honeypot
            ip (str): IP address to listen on
            port (int): Port to listen on
        """
        super().__init__(honeypot_id, ip, port)
        self.banner = kwargs.get('banner', 'SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.5')
        self.honeypot_type = "SSH"
        
    async def handle_client(self, reader, writer):
        """Handle a client connection."""
        client_ip = writer.get_extra_info('peername')[0]
        logger.info(f"SSH connection from {client_ip}")
        
        # Send SSH banner
        writer.write(f"{self.banner}\r\n".encode())
        await writer.drain()
        
        # Record connection
        login_data = {
            "connection_time": datetime.now().isoformat()
        }
        
        try:
            # Wait for client identification
            client_id = await asyncio.wait_for(reader.readline(), timeout=30)
            if client_id:
                login_data["client_id"] = client_id.decode().strip()
            
            # Wait for authentication attempt
            writer.write(b"Password: ")
            await writer.drain()
            
            # Wait for password
            password = await asyncio.wait_for(reader.readline(), timeout=30)
            if password:
                login_data["password_attempt"] = password.decode().strip()
                
            # Always deny access
            writer.write(b"Access denied\r\n")
            await writer.drain()
            
            # Analyze the attack
            attack_type = self._analyze_attack(login_data)
            
            # Record the activity
            await self.record_activity(client_ip, login_data, attack_type)
            
        except asyncio.TimeoutError:
            logger.info(f"Connection from {client_ip} timed out")
        except Exception as e:
            logger.error(f"Error handling SSH connection: {str(e)}")
        finally:
            writer.close()
            await writer.wait_closed()
    
    def _analyze_attack(self, login_data):
        """
        Basic analysis of the attack based on login data.
        
        In a real implementation, this would use the AI engine for 
        more sophisticated analysis.
        """
        if "password_attempt" not in login_data:
            return "Connection attempt"
        
        password = login_data.get("password_attempt", "")
        
        # Check for common attack patterns
        if password.lower() in ["admin", "root", "password", "123456"]:
            return "Common password attack"
        
        if re.search(r'[;|&]', password):
            return "Command injection attempt"
            
        return "Brute force attempt"
    
    async def start(self):
        """Start the SSH honeypot server."""
        await super().start()
        
        try:
            self.server = await asyncio.start_server(
                self.handle_client, self.ip, self.port
            )
            
            logger.info(f"SSH honeypot {self.id} listening on {self.ip}:{self.port}")
            
            async with self.server:
                await self.server.serve_forever()
        except Exception as e:
            logger.error(f"Failed to start SSH honeypot: {str(e)}")
            self.status = "Error"
    
    async def stop(self):
        """Stop the SSH honeypot server."""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            self.server = None
        
        await super().stop()
