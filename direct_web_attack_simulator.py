#!/usr/bin/env python
"""
Direct Web Attack Simulator

This script simulates web attacks by directly sending alerts to the API
instead of trying to connect to an actual honeypot. This is useful for
demonstrations when the honeypot services aren't running.
"""

import asyncio
import logging
import random
import json
import time
import aiohttp
from datetime import datetime
from urllib.parse import urljoin

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("direct_web_attack_simulator")

# API endpoint
API_URL = "http://localhost:8000/honeypots/web-honeypot-1/alerts"

# Common headers for web requests
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0"
]

# Random source IPs for simulating different attackers
SOURCE_IPS = [
    "192.168.1.100", "10.0.0.25", "172.16.0.50", "192.168.0.10",
    "45.33.21.18", "89.105.194.89", "66.249.66.1", "77.88.55.60",
    "138.197.138.255", "104.236.213.118", "113.12.83.45"
]

class DirectWebAttackSimulator:
    """Simulate web attacks by sending alerts directly to the API."""
    
    def __init__(self, api_url=API_URL):
        """Initialize the direct web attack simulator."""
        self.api_url = api_url
        self.session = None
        self.attack_count = 0
    
    async def setup(self):
        """Set up the simulator."""
        self.session = aiohttp.ClientSession()
    
    async def cleanup(self):
        """Clean up resources."""
        if self.session:
            await self.session.close()
    
    async def send_alert(self, attack_type, attack_details, source_ip=None):
        """Send an alert directly to the API."""
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
        
        logger.info(f"Sending alert for {attack_type} attack from {source_ip}")
        
        try:
            async with self.session.post(self.api_url, json=alert) as response:
                if response.status == 200:
                    self.attack_count += 1
                    logger.info(f"Alert sent successfully: {await response.text()}")
                    return True
                else:
                    logger.error(f"Failed to send alert: {response.status} - {await response.text()}")
                    return False
        except Exception as e:
            logger.error(f"Error sending alert: {str(e)}")
            return False
    
    async def simulate_login_brute_force(self, attempts=5):
        """Simulate login brute force attempts."""
        logger.info(f"Starting login brute force simulation ({attempts} attempts)")
        
        usernames = ["admin", "administrator", "root", "user", "guest"]
        passwords = ["admin", "password", "123456", "qwerty", "letmein", "welcome", "admin123", "pass123"]
        
        source_ip = random.choice(SOURCE_IPS)
        
        for i in range(attempts):
            username = random.choice(usernames)
            password = random.choice(passwords)
            
            attack_details = {
                "url": "/login",
                "method": "POST",
                "username": username,
                "password": password,
                "attempt": i+1,
                "total_attempts": attempts
            }
            
            await self.send_alert("LOGIN_BRUTE_FORCE", attack_details, source_ip)
            await asyncio.sleep(random.uniform(0.5, 2.0))
    
    async def simulate_sql_injection(self, attempts=5):
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
            "' OR '1'='1' LIMIT 1; --",
            "' OR \'1\'=\'1\'",
            "' OR ''='"
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
            
            await self.send_alert("SQL_INJECTION", attack_details, source_ip)
            await asyncio.sleep(random.uniform(0.5, 2.0))
    
    async def simulate_xss_attacks(self, attempts=5):
        """Simulate XSS attacks."""
        logger.info(f"Starting XSS attack simulation ({attempts} attempts)")
        
        payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "javascript:alert('XSS')",
            "<iframe src=\"javascript:alert('XSS')\">",
            "<body onload=alert('XSS')>",
            "<svg/onload=alert('XSS')>",
            "\"><script>alert('XSS')</script>",
            "<img src=\"x\" onerror=\"alert('XSS')\">"
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
            
            await self.send_alert("XSS", attack_details, source_ip)
            await asyncio.sleep(random.uniform(0.5, 2.0))
    
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
            
            await self.send_alert("PATH_TRAVERSAL", attack_details, source_ip)
            await asyncio.sleep(random.uniform(0.5, 2.0))
    
    async def simulate_vulnerability_scanning(self, attempts=10):
        """Simulate vulnerability scanning."""
        logger.info(f"Starting vulnerability scanning simulation ({attempts} attempts)")
        
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
        
        for i in range(attempts):
            target = random.choice(targets)
            
            attack_details = {
                "url": target,
                "method": "GET",
                "user_agent": random.choice(USER_AGENTS),
                "attempt": i+1,
                "total_attempts": attempts
            }
            
            await self.send_alert("VULNERABILITY_SCAN", attack_details, source_ip)
            await asyncio.sleep(random.uniform(0.5, 2.0))
    
    async def run_all_simulations(self):
        """Run all attack simulations."""
        await self.setup()
        
        try:
            # Run simulations one after another
            await self.simulate_login_brute_force(attempts=5)
            await self.simulate_sql_injection(attempts=5)
            await self.simulate_xss_attacks(attempts=5)
            await self.simulate_path_traversal(attempts=5)
            await self.simulate_vulnerability_scanning(attempts=10)
            
            logger.info(f"Completed all web attack simulations. Total alerts: {self.attack_count}")
        finally:
            await self.cleanup()

async def main():
    """Main function to run the direct web attack simulator."""
    print("=" * 70)
    print(f"Direct Web Attack Simulator - {datetime.now()}")
    print("=" * 70)
    print(f"API URL: {API_URL}")
    print("This tool simulates web attacks by sending alerts directly to the API")
    print("=" * 70)
    
    simulator = DirectWebAttackSimulator()
    await simulator.run_all_simulations()

if __name__ == "__main__":
    asyncio.run(main())
