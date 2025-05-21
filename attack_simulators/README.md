# Honeypot Attack Simulators

This directory contains simulation tools for testing the AI Honeypot System. These tools generate realistic attack patterns to demonstrate the detection and analysis capabilities of the honeypots.

## Available Simulators

### 1. SSH Attack Simulator

Simulates various SSH attack patterns:
- Brute force login attempts
- Command injection attacks
- Unusual SSH client connections

**Usage:**
```bash
python ssh_attack_simulator.py --ip 127.0.0.1 --port 2222
```

### 2. Web Attack Simulator

Simulates various web-based attack patterns:
- SQL injection attacks
- Cross-Site Scripting (XSS) attacks
- Path traversal attempts
- Common vulnerability scanning
- Login brute force attacks

**Usage:**
```bash
python web_attack_simulator.py --url http://127.0.0.1:8080
```

## How to Run the Simulations

1. First, start the AI Honeypot System:
```bash
python start.py
```

2. Open another terminal window and run the desired attack simulator.

3. Watch the alerts appear in the AI Honeypot Dashboard at http://localhost:3000

4. Check the logs in the `logs` directory to see the detailed attack records and AI analysis.

## Notes

- These simulators are designed for testing and educational purposes only.
- The attack patterns are non-destructive and will not harm the honeypot system.
- The simulators add randomized delays between attacks to create more realistic patterns.
- Each attack type can be customized by modifying the payload lists in the simulator files.
