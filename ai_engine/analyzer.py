import logging
import json
from datetime import datetime
import re
import os

logger = logging.getLogger("honeypot.ai")

class AIAnalyzer:
    """
    AI-powered analyzer for honeypot activity.
    Detects anomalies, classifies attacks, and provides threat intelligence.
    """
    
    def __init__(self):
        """Initialize the AI analyzer with machine learning models."""
        self.models = {}
        self.vectorizers = {}
        self.threat_db = {}
        self.attackers_db = {}
        self.initialize_models()
        
    def initialize_models(self):
        """Initialize rules and patterns for attack detection."""
        # Initialize SSH attack patterns
        self.patterns = {
            'ssh': {
                'command_injection': [r'[;&|`]', r'\bsh\b', r'\bbash\b', r'\bcmd\b'],
                'common_passwords': ['admin', 'root', 'password', '123456', 'qwerty', 'letmein']
            },
            'web': {
                'sql_injection': [r"['\"]\s*OR\s*['\"]?\d+['\"]?\s*=\s*['\"]?\d+['\"]?", 
                                  r"\bUNION\s+SELECT\b", r"\bDROP\s+TABLE\b", r"--", r"#", r";\s*$"],
                'xss': [r"<script", r"javascript:", r"\balert\s*\(", r"\bonerror=", r"\bonload="],
                'path_traversal': [r"\.\.[\\/]", r"\.\.%2F", r"etc/passwd", r"win.ini", r"boot.ini"]
            }
        }
        
        # Initialize threat rules
        self.threat_rules = {
            'critical': [
                {'type': 'web', 'pattern': 'path_traversal', 'repeat_count': 1},
                {'type': 'web', 'pattern': 'sql_injection', 'repeat_count': 1},
                {'type': 'ssh', 'pattern': 'command_injection', 'repeat_count': 1},
                {'type': 'any', 'repeat_count': 20}
            ],
            'high': [
                {'type': 'web', 'pattern': 'xss', 'repeat_count': 1},
                {'type': 'ssh', 'pattern': 'common_passwords', 'repeat_count': 5},
                {'type': 'any', 'repeat_count': 10}
            ],
            'medium': [
                {'type': 'ssh', 'pattern': 'common_passwords', 'repeat_count': 1},
                {'type': 'any', 'repeat_count': 5}
            ]
        }
        
        logger.info("Rule-based analysis patterns initialized")
    
    def analyze_event(self, event):
        """
        Analyze a honeypot event and determine threat level, attack type, and other insights.
        
        Args:
            event (dict): Honeypot event data
            
        Returns:
            dict: Analysis results including threat level, attack classification, and recommendations
        """
        honeypot_id = event.get('honeypot_id', '')
        honeypot_type = honeypot_id.split('-')[0] if '-' in honeypot_id else ''
        data = event.get('data', {})
        source_ip = data.get('source_ip', '')
        attack_type = data.get('attack_type', 'Unknown')
        details = data.get('details', {})
        
        # Track attacker
        self._update_attacker_profile(source_ip, honeypot_type, attack_type, details)
        
        # Determine baseline threat level based on attack type
        threat_level = self._get_baseline_threat_level(attack_type)
        
        # Apply AI analysis based on honeypot type
        if honeypot_type.lower() == 'ssh':
            threat_level, attack_details = self._analyze_ssh_attack(details, threat_level)
        elif honeypot_type.lower() == 'web':
            threat_level, attack_details = self._analyze_web_attack(details, threat_level)
        else:
            attack_details = self._generic_attack_analysis(details, attack_type)
        
        # Check for repeated attacks or known malicious IPs
        threat_level = self._adjust_for_repeated_attacks(source_ip, threat_level)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(source_ip, attack_type, threat_level)
        
        # Prepare full analysis
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "source_ip": source_ip,
            "honeypot_id": honeypot_id,
            "attack_type": attack_type,
            "threat_level": threat_level,  # 0-3: Low, Medium, High, Critical
            "threat_level_label": self._get_threat_level_label(threat_level),
            "attack_details": attack_details,
            "is_known_attacker": source_ip in self.attackers_db,
            "attack_count": self.attackers_db.get(source_ip, {}).get("attack_count", 1),
            "recommendations": recommendations
        }
        
        logger.info(f"AI analysis completed for event from {source_ip}: Threat level {analysis['threat_level_label']}")
        
        return analysis
    
    def _update_attacker_profile(self, ip, honeypot_type, attack_type, details):
        """Update the profile for an attacker IP."""
        if ip not in self.attackers_db:
            self.attackers_db[ip] = {
                "first_seen": datetime.now().isoformat(),
                "attack_count": 1,
                "honeypot_types": [honeypot_type],
                "attack_types": [attack_type],
                "attack_details": [details]
            }
        else:
            profile = self.attackers_db[ip]
            profile["attack_count"] += 1
            profile["last_seen"] = datetime.now().isoformat()
            
            if honeypot_type not in profile["honeypot_types"]:
                profile["honeypot_types"].append(honeypot_type)
                
            if attack_type not in profile["attack_types"]:
                profile["attack_types"].append(attack_type)
            
            # Keep only the last 10 attack details to avoid memory issues
            profile["attack_details"].append(details)
            if len(profile["attack_details"]) > 10:
                profile["attack_details"] = profile["attack_details"][-10:]
    
    def _get_baseline_threat_level(self, attack_type):
        """Get baseline threat level based on attack type."""
        high_threat_attacks = [
            "SQL Injection attempt", "Command injection attempt",
            "Known vulnerability probe", "PHPMyAdmin attack"
        ]
        
        medium_threat_attacks = [
            "Brute force attempt", "Credential stuffing attempt",
            "Web vulnerability scan", "WordPress vulnerability scan"
        ]
        
        if attack_type in high_threat_attacks:
            return 2  # High
        elif attack_type in medium_threat_attacks:
            return 1  # Medium
        else:
            return 0  # Low
    
    def _analyze_ssh_attack(self, details, baseline_threat):
        """Analyze SSH attack details with pattern matching."""
        attack_details = {}
        
        # Extract features
        password = details.get('password_attempt', '')
        client_id = details.get('client_id', '')
        
        # Check for command injection patterns
        for pattern in self.patterns['ssh']['command_injection']:
            if re.search(pattern, password, re.IGNORECASE):
                attack_details["command_injection"] = True
                baseline_threat = max(baseline_threat, 3)  # Critical
                break
        
        # Check for common passwords
        for common_pwd in self.patterns['ssh']['common_passwords']:
            if password.lower() == common_pwd.lower():
                attack_details["common_password"] = True
                attack_details["password_used"] = common_pwd
                baseline_threat = max(baseline_threat, 1)  # Medium
                break
        
        # Check for unusual SSH client
        if client_id:
            common_clients = ["OpenSSH", "PuTTY", "libssh"]
            if not any(client in client_id for client in common_clients):
                attack_details["unusual_client"] = True
                baseline_threat = max(baseline_threat, 1)  # Medium
        
        return baseline_threat, attack_details
    
    def _analyze_web_attack(self, details, baseline_threat):
        """Analyze web attack details with pattern matching."""
        attack_details = {}
        
        # Extract features
        path = details.get('path', '')
        method = details.get('method', '')
        query_string = details.get('query_string', {})
        headers = details.get('headers', {})
        
        # Combine relevant inputs for pattern matching
        combined_input = path + json.dumps(query_string)
        
        # Check for path traversal attempts
        for pattern in self.patterns['web']['path_traversal']:
            if re.search(pattern, combined_input, re.IGNORECASE):
                attack_details["path_traversal"] = True
                attack_details["matched_pattern"] = pattern
                baseline_threat = max(baseline_threat, 3)  # Critical
                break
        
        # Check for SQL injection attempts
        for pattern in self.patterns['web']['sql_injection']:
            if re.search(pattern, combined_input, re.IGNORECASE):
                attack_details["sql_injection"] = True
                attack_details["matched_pattern"] = pattern
                baseline_threat = max(baseline_threat, 3)  # Critical
                break
        
        # Check for XSS attempts
        for pattern in self.patterns['web']['xss']:
            if re.search(pattern, combined_input, re.IGNORECASE):
                attack_details["xss_attempt"] = True
                attack_details["matched_pattern"] = pattern
                baseline_threat = max(baseline_threat, 2)  # High
                break
        
        # Check for user-agent anomalies
        user_agent = headers.get('User-Agent', '')
        if re.search(r'(sqlmap|nikto|nmap|dirbuster|gobuster|wpscan|hydra)', user_agent, re.IGNORECASE):
            attack_details["scanning_tool_detected"] = True
            attack_details["user_agent"] = user_agent
            baseline_threat = max(baseline_threat, 2)  # High
        
        return baseline_threat, attack_details
    
    def _generic_attack_analysis(self, details, attack_type):
        """Generic attack analysis for other honeypot types."""
        # In a real implementation, this would have more sophisticated logic
        return {"raw_details": details}
    
    def _adjust_for_repeated_attacks(self, ip, threat_level):
        """Adjust threat level based on repeated attacks from the same IP."""
        if ip in self.attackers_db:
            attack_count = self.attackers_db[ip].get("attack_count", 0)
            
            # Increase threat level for repeated attackers
            if attack_count > 20:
                threat_level = max(threat_level, 3)  # Critical
            elif attack_count > 10:
                threat_level = max(threat_level, 2)  # High
            elif attack_count > 5:
                threat_level = max(threat_level, 1)  # Medium
        
        return threat_level
    
    def _generate_recommendations(self, ip, attack_type, threat_level):
        """Generate security recommendations based on the attack."""
        recommendations = []
        
        # Basic recommendations based on threat level
        if threat_level >= 3:  # Critical
            recommendations.append("Block this IP address immediately at the firewall level")
            recommendations.append("Investigate all systems for potential compromise")
        elif threat_level >= 2:  # High
            recommendations.append("Consider blocking this IP address")
            recommendations.append("Review logs for successful attacks")
        
        # Attack-specific recommendations
        if "SQL Injection" in attack_type:
            recommendations.append("Review web application input validation")
            recommendations.append("Apply prepared statements for database queries")
        elif "Brute force" in attack_type:
            recommendations.append("Implement account lockout policies")
            recommendations.append("Consider two-factor authentication")
        elif "vulnerability scan" in attack_type.lower():
            recommendations.append("Ensure all software is up to date")
            recommendations.append("Consider web application firewall")
        
        return recommendations
    
    def _get_threat_level_label(self, level):
        """Convert numeric threat level to label."""
        labels = ["Low", "Medium", "High", "Critical"]
        return labels[min(level, 3)]
    
    def get_threat_intelligence(self):
        """
        Generate threat intelligence report based on collected data.
        
        Returns:
            dict: Threat intelligence report
        """
        # Get top attackers
        top_attackers = sorted(
            self.attackers_db.items(),
            key=lambda x: x[1].get("attack_count", 0),
            reverse=True
        )[:10]
        
        # Get most common attack types
        attack_types = {}
        for ip, data in self.attackers_db.items():
            for attack in data.get("attack_types", []):
                attack_types[attack] = attack_types.get(attack, 0) + 1
        
        top_attack_types = sorted(
            attack_types.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        # Generate report
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_attackers": len(self.attackers_db),
            "top_attackers": [
                {"ip": ip, "attack_count": data.get("attack_count", 0)}
                for ip, data in top_attackers
            ],
            "top_attack_types": [
                {"type": attack_type, "count": count}
                for attack_type, count in top_attack_types
            ]
        }
        
        return report
