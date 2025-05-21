import asyncio
import logging
from datetime import datetime
import re
import json
from aiohttp import web
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from honeypots.base import BaseHoneypot
from utils.logging_config import setup_logger

logger = setup_logger("honeypot.web")

class WebHoneypot(BaseHoneypot):
    """
    Web Honeypot implementation that simulates a vulnerable web server.
    """
    
    def __init__(self, honeypot_id, ip="0.0.0.0", port=80, **kwargs):
        """
        Initialize a new Web honeypot.
        
        Args:
            honeypot_id (str): Unique identifier for this honeypot
            ip (str): IP address to listen on
            port (int): Port to listen on
        """
        super().__init__(honeypot_id, ip, port)
        self.server_type = kwargs.get('server_type', 'Apache/2.4.41 (Ubuntu)')
        self.vulnerable_paths = kwargs.get('vulnerable_paths', [
            '/admin', '/login', '/wp-admin', '/phpmyadmin', '/config'
        ])
        self.honeypot_type = "Web"
        self.app = web.Application()
        self._setup_routes()
        
    def _setup_routes(self):
        """Set up the web routes for the honeypot."""
        self.app.router.add_get('/', self.handle_root)
        self.app.router.add_get('/login', self.handle_login)
        self.app.router.add_post('/login', self.handle_login_post)
        
        # Add catch-all routes for all methods
        self.app.router.add_route('*', '/{tail:.*}', self.handle_any)
    
    async def handle_root(self, request):
        """Handle requests to the root path."""
        await self._record_web_request(request)
        return web.Response(text="""
        <html>
            <head><title>System Administration</title></head>
            <body>
                <h1>Company Internal Server</h1>
                <p>Please <a href="/login">login</a> to access the system.</p>
            </body>
        </html>
        """, content_type='text/html')
    
    async def handle_login(self, request):
        """Handle GET requests to the login path."""
        await self._record_web_request(request)
        return web.Response(text="""
        <html>
            <head><title>Login</title></head>
            <body>
                <h1>Login</h1>
                <form method="post" action="/login">
                    <p>Username: <input type="text" name="username"></p>
                    <p>Password: <input type="password" name="password"></p>
                    <p><input type="submit" value="Login"></p>
                </form>
            </body>
        </html>
        """, content_type='text/html')
    
    async def handle_login_post(self, request):
        """Handle POST requests to the login path."""
        data = await request.post()
        username = data.get('username', '')
        password = data.get('password', '')
        
        attack_data = {
            "username": username,
            "password": password,
        }
        
        # Analyze the attack
        attack_type = self._analyze_attack(attack_data)
        
        # Record the activity
        await self._record_web_request(request, attack_data, attack_type)
        
        return web.Response(text="""
        <html>
            <head><title>Login Failed</title></head>
            <body>
                <h1>Login Failed</h1>
                <p>Invalid username or password.</p>
                <p><a href="/login">Try again</a></p>
            </body>
        </html>
        """, content_type='text/html')
    
    async def handle_any(self, request):
        """Handle any other request path."""
        path = request.path
        
        # Check if this is a known vulnerable path
        is_vulnerable = any(path.startswith(vp) for vp in self.vulnerable_paths)
        attack_type = "Path scanning" if not is_vulnerable else "Known vulnerability probe"
        
        await self._record_web_request(request, {"path": path}, attack_type)
        
        if is_vulnerable:
            # If it's a known vulnerable path, return a fake error page
            return web.Response(text="""
            <html>
                <head><title>Error</title></head>
                <body>
                    <h1>Server Error</h1>
                    <p>The server encountered an internal error and was unable to complete your request.</p>
                </body>
            </html>
            """, status=500, content_type='text/html')
        else:
            # Otherwise return a normal 404
            return web.Response(text="""
            <html>
                <head><title>Not Found</title></head>
                <body>
                    <h1>404 Not Found</h1>
                    <p>The requested URL was not found on this server.</p>
                </body>
            </html>
            """, status=404, content_type='text/html')
    
    async def _record_web_request(self, request, data=None, attack_type=None):
        """Record a web request."""
        client_ip = request.remote
        
        request_data = {
            "method": request.method,
            "path": request.path,
            "headers": dict(request.headers),
            "query_string": dict(request.query),
            "time": datetime.now().isoformat()
        }
        
        if data:
            request_data.update(data)
            
        # Record the activity
        await self.record_activity(client_ip, request_data, attack_type or "Web request")
    
    def _analyze_attack(self, data):
        """
        Basic analysis of web attacks based on request data.
        
        In a real implementation, this would use the AI engine for
        more sophisticated analysis.
        """
        if "username" in data and "password" in data:
            username = data.get("username", "")
            password = data.get("password", "")
            
            # Check for SQL injection attempts
            sql_patterns = [
                r"'", r'"', r"--", r"#", r"\*", r";", r"OR 1=1", r"OR '1'='1'",
                r"DROP", r"SELECT", r"UNION", r"INSERT", r"DELETE", r"UPDATE"
            ]
            
            for pattern in sql_patterns:
                if re.search(pattern, username, re.IGNORECASE) or re.search(pattern, password, re.IGNORECASE):
                    return "SQL Injection attempt"
            
            # Check for common credentials
            if username.lower() in ["admin", "root", "administrator"] and password:
                return "Common admin credential attack"
                
            return "Credential stuffing attempt"
            
        if "path" in data:
            path = data.get("path", "")
            
            # Check for common web vulnerabilities in path
            if re.search(r"\.(php|asp|jsp|cgi)\.", path, re.IGNORECASE):
                return "Web vulnerability scan"
                
            if "/wp-" in path or "/wordpress" in path:
                return "WordPress vulnerability scan"
                
            if "/phpMyAdmin" in path or "/phpmyadmin" in path:
                return "PHPMyAdmin attack"
                
        return "Unknown web attack"
    
    async def start(self):
        """Start the web honeypot server."""
        await super().start()
        
        try:
            self.runner = web.AppRunner(self.app)
            await self.runner.setup()
            
            self.site = web.TCPSite(self.runner, self.ip, self.port)
            await self.site.start()
            
            logger.info(f"Web honeypot {self.id} listening on {self.ip}:{self.port}")
            
            # Keep the server running
            while self.running:
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"Failed to start Web honeypot: {str(e)}")
            self.status = "Error"
    
    async def stop(self):
        """Stop the web honeypot server."""
        if hasattr(self, 'site'):
            await self.site.stop()
            
        if hasattr(self, 'runner'):
            await self.runner.cleanup()
            
        await super().stop()
