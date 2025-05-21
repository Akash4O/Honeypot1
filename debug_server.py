#!/usr/bin/env python
"""
Debug version of the server that doesn't automatically start honeypots
"""

import logging
import os
import json
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from utils.logging_config import setup_logger

# Configure logging
logger = setup_logger("honeypot.debug_server")

# Initialize the FastAPI application
app = FastAPI(title="AI HoneyPot System (Debug Mode)")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variable to store alerts
alerts = []

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "AI HoneyPot System API (Debug Mode)"}

@app.get("/honeypots")
async def get_honeypots():
    """Get all honeypots (mock)."""
    return [
        {
            "id": "ssh-honeypot-1",
            "type": "SSH",
            "ip": "0.0.0.0",
            "port": 2222,
            "status": "configured"
        },
        {
            "id": "web-honeypot-1",
            "type": "Web",
            "ip": "0.0.0.0",
            "port": 8089,
            "status": "configured"
        }
    ]

@app.get("/honeypots/{honeypot_id}")
async def get_honeypot(honeypot_id: str):
    """Get a specific honeypot (mock)."""
    if honeypot_id == "ssh-honeypot-1":
        return {
            "id": "ssh-honeypot-1",
            "type": "SSH",
            "ip": "0.0.0.0",
            "port": 2222,
            "status": "configured"
        }
    elif honeypot_id == "web-honeypot-1":
        return {
            "id": "web-honeypot-1",
            "type": "Web",
            "ip": "0.0.0.0",
            "port": 8089,
            "status": "configured"
        }
    raise HTTPException(status_code=404, detail=f"Honeypot {honeypot_id} not found")

@app.get("/alerts")
async def get_alerts():
    """Get all alerts."""
    logger.debug(f"Returning {len(alerts)} alerts")
    return alerts

@app.post("/honeypots/{honeypot_id}/alerts")
async def create_alert(honeypot_id: str, request: Request):
    """Create a new alert."""
    try:
        alert_data = await request.json()
        logger.debug(f"Received alert from {honeypot_id}: {alert_data}")
        
        # Create alert object
        alert = {
            "honeypot_id": honeypot_id,
            "timestamp": alert_data.get("timestamp"),
            "data": alert_data.get("data", {})
        }
        
        # Add AI analysis 
        alert["analysis"] = {
            "threat_level": "medium",
            "classification": "reconnaissance",
            "confidence": 0.75,
            "details": "Simulated attack detected"
        }
        
        # Store the alert
        alerts.append(alert)
        logger.info(f"Processed and stored alert from {honeypot_id}")
        
        return {"status": "success", "message": "Alert processed"}
    except Exception as e:
        logger.error(f"Error processing alert: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing alert: {str(e)}")

@app.get("/threat-intelligence")
async def get_threat_intelligence():
    """Get threat intelligence report (mock)."""
    return {
        "summary": "Debug mock threat intelligence",
        "top_attackers": [
            {"ip": "192.168.1.100", "count": 10, "classification": "scanner"}
        ],
        "attack_types": {
            "ssh_brute_force": 5,
            "web_scanning": 5
        }
    }

if __name__ == "__main__":
    # Run the server
    logger.info("Starting FastAPI debug server on http://0.0.0.0:8000")
    logger.info("This is a debug version that doesn't start actual honeypots")
    
    # Run the server
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")
