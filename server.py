import asyncio
import logging
import os
import signal
import json
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import uvicorn

from honeypots.manager import HoneypotManager
from utils.logging_config import setup_logger

# Configure logging
logger = setup_logger("honeypot.server")

# Initialize the honeypot manager
honeypot_manager = HoneypotManager()

# Initialize the FastAPI application
app = FastAPI(title="AI HoneyPot System")

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

@app.on_event("startup")
async def startup_event():
    """Start honeypots when the server starts."""
    logger.info("Starting honeypot server")
    try:
        # Start the honeypots in a separate task
        # Use asyncio.create_task to run it in the background
        asyncio.create_task(honeypot_manager.start_all())
        logger.info("Honeypot startup task initiated")
        
        # Log the configured honeypots
        for hid, honeypot in honeypot_manager.honeypots.items():
            logger.info(f"Honeypot {hid}: type={honeypot.honeypot_type}, ip={honeypot.ip}, port={honeypot.port}")
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        # Don't raise the exception - let the server continue running

@app.on_event("shutdown")
async def shutdown_event():
    """Stop honeypots when the server stops."""
    logger.info("Stopping honeypot server")
    try:
        await honeypot_manager.stop_all()
        logger.info("All honeypots stopped successfully")
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")
        # Continue with shutdown even if there are errors

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Welcome to AI HoneyPot System"}

@app.get("/honeypots")
async def get_honeypots():
    """Get status for all honeypots."""
    return honeypot_manager.get_honeypot_status()

@app.get("/honeypots/{honeypot_id}")
async def get_honeypot(honeypot_id: str):
    """Get status for a specific honeypot."""
    status = honeypot_manager.get_honeypot_status(honeypot_id)
    if not status:
        raise HTTPException(status_code=404, detail="Honeypot not found")
    return status

@app.post("/honeypots")
async def create_honeypot(data: dict):
    """Create a new honeypot."""
    honeypot_id = data.get("id")
    honeypot_type = data.get("type")
    ip = data.get("ip", "0.0.0.0")
    port = data.get("port", 0)
    options = data.get("options", {})
    
    if not honeypot_id or not honeypot_type:
        raise HTTPException(status_code=400, detail="Missing required fields")
    
    honeypot = honeypot_manager.create_honeypot(honeypot_id, honeypot_type, ip, port, **options)
    if not honeypot:
        raise HTTPException(status_code=500, detail="Failed to create honeypot")
    
    return {"message": "Honeypot created", "id": honeypot_id}

@app.post("/honeypots/{honeypot_id}/start")
async def start_honeypot(honeypot_id: str):
    """Start a specific honeypot."""
    success = await honeypot_manager.start_honeypot(honeypot_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to start honeypot")
    return {"message": f"Honeypot {honeypot_id} started"}

@app.post("/honeypots/{honeypot_id}/stop")
async def stop_honeypot(honeypot_id: str):
    """Stop a specific honeypot."""
    success = await honeypot_manager.stop_honeypot(honeypot_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to stop honeypot")
    return {"message": f"Honeypot {honeypot_id} stopped"}

@app.delete("/honeypots/{honeypot_id}")
async def delete_honeypot(honeypot_id: str):
    """Delete a specific honeypot."""
    success = honeypot_manager.remove_honeypot(honeypot_id)
    if not success:
        raise HTTPException(status_code=404, detail="Honeypot not found")
    return {"message": f"Honeypot {honeypot_id} deleted"}

@app.get("/alerts")
async def get_alerts():
    """Get all recorded alerts."""
    logger.info(f"GET /alerts - Returning {len(alerts)} alerts")
    return alerts

@app.post("/honeypot/{honeypot_id}/alert")
async def create_alert(honeypot_id: str, alert_data: dict):
    """Create a new alert and analyze it with AI."""
    logger.info(f"POST /honeypot/{honeypot_id}/alert - Received alert data: {json.dumps(alert_data)}")
    
    try:
        # Create the basic alert
        alert = {
            "honeypot_id": honeypot_id,
            "timestamp": alert_data.get("timestamp", datetime.now().isoformat()),
            "data": alert_data.get("data", alert_data)  # Fallback to using the entire payload as data
        }
        
        # Ensure data has source_ip and attack_type fields
        if "source_ip" not in alert["data"] and alert["data"].get("details", {}).get("source_ip"):
            alert["data"]["source_ip"] = alert["data"]["details"]["source_ip"]
            
        if "attack_type" not in alert["data"]:
            alert["data"]["attack_type"] = "Unknown Attack"
        
        # Use AI to analyze the alert
        logger.info(f"Analyzing alert with AI engine...")
        analysis = honeypot_manager.analyze_event(alert)
        
        # Combine alert with analysis
        alert["analysis"] = analysis
        
        # Store the alert
        alerts.append(alert)
        logger.info(f"Alert stored successfully. Total alerts: {len(alerts)}")
        logger.info(f"New alert details: {json.dumps(alert)}")
        
        return alert
    except Exception as e:
        logger.error(f"Error processing alert: {str(e)}")
        import traceback
        logger.error(f"Exception traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error processing alert: {str(e)}")

@app.get("/threat-intelligence")
async def get_threat_intelligence():
    """Get threat intelligence report."""
    return honeypot_manager.get_threat_intelligence()

if __name__ == "__main__":
    # Run the server
    logger.info("Starting FastAPI server on http://0.0.0.0:8000")
    logger.info("Honeypot Manager and AI Analyzer initialized")
    logger.info(f"Server has {len(honeypot_manager.honeypots)} honeypots configured")
    
    # Print troubleshooting info
    for hid, honeypot in honeypot_manager.honeypots.items():
        logger.info(f"Honeypot {hid}: type={honeypot.honeypot_type}, ip={honeypot.ip}, port={honeypot.port}")
    
    # Run the server
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
