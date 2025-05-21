from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import logging
from datetime import datetime
import json

app = FastAPI(title="AI HoneyPot System")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('honeypot.log'),
        logging.StreamHandler()
    ]
)

# Mock database for demonstration
honeypot_data = {}
alerts = []

@app.get("/")
async def root():
    return {"message": "Welcome to AI HoneyPot System"}

@app.get("/alerts")
async def get_alerts():
    return alerts

@app.get("/honeypots")
async def get_honeypots():
    return honeypot_data

@app.post("/honeypot/{honeypot_id}/alert")
async def create_alert(honeypot_id: str, alert_data: dict):
    alert = {
        "honeypot_id": honeypot_id,
        "timestamp": datetime.now().isoformat(),
        "data": alert_data
    }
    alerts.append(alert)
    logging.info(f"New alert received: {json.dumps(alert)}")
    return alert

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
