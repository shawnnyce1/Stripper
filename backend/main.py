from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json
import os
import sys
from datetime import datetime
import asyncio

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from automation.shared.bot_core import BotManager
except ImportError:
    # Fallback if automation module is not available
    class BotManager:
        def __init__(self):
            self.bots = {}
        
        async def start_bot(self, account_name):
            return True
        
        async def stop_bot(self, account_name):
            return True
        
        def get_bot_status(self, account_name):
            return "stopped"

app = FastAPI(title="Amazon Flex Grabber API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class LoginRequest(BaseModel):
    email: str
    password: str
    warehouse: str
    account_name: str

class BotConfig(BaseModel):
    enabled: bool
    auto_accept: bool
    min_rate: float
    max_distance: int
    preferred_warehouses: List[str]

class MetricsResponse(BaseModel):
    blocks_grabbed: int
    total_earnings: float
    today_earnings: float
    success_rate: float
    last_activity: Optional[str]

# Global bot manager
bot_manager = BotManager()

@app.get("/")
async def root():
    return {"message": "Amazon Flex Grabber API", "status": "running"}

@app.post("/api/login")
async def login(request: LoginRequest):
    print(f"Received login request: {request}")
    try:
        # Save account configuration
        account_dir = f"accounts/{request.account_name}"
        os.makedirs(account_dir, exist_ok=True)
        
        config = {
            "email": request.email,
            "warehouse": request.warehouse,
            "created_at": datetime.now().isoformat()
        }
        
        with open(f"{account_dir}/config.json", "w") as f:
            json.dump(config, f, indent=2)
        
        # Create .env file (password should be encrypted in production)
        with open(f"{account_dir}/.env", "w") as f:
            f.write(f"EMAIL={request.email}\n")
            f.write(f"PASSWORD={request.password}\n")
            f.write(f"WAREHOUSE={request.warehouse}\n")
        
        print(f"Account saved successfully: {request.account_name}")
        return {"success": True, "message": f"Account {request.account_name} configured successfully"}
    
    except Exception as e:
        print(f"Error saving account: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/accounts")
async def get_accounts():
    accounts = []
    accounts_dir = "accounts"
    
    if os.path.exists(accounts_dir):
        for account_name in os.listdir(accounts_dir):
            account_path = os.path.join(accounts_dir, account_name)
            if os.path.isdir(account_path):
                config_path = os.path.join(account_path, "config.json")
                if os.path.exists(config_path):
                    with open(config_path, "r") as f:
                        config = json.load(f)
                    accounts.append({
                        "name": account_name,
                        "email": config.get("email"),
                        "warehouse": config.get("warehouse"),
                        "status": bot_manager.get_bot_status(account_name)
                    })
    
    return {"accounts": accounts}

@app.post("/api/bot/start/{account_name}")
async def start_bot(account_name: str):
    try:
        success = await bot_manager.start_bot(account_name)
        if success:
            return {"success": True, "message": f"Bot started for {account_name}"}
        else:
            raise HTTPException(status_code=400, detail="Failed to start bot")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/bot/stop/{account_name}")
async def stop_bot(account_name: str):
    try:
        success = await bot_manager.stop_bot(account_name)
        if success:
            return {"success": True, "message": f"Bot stopped for {account_name}"}
        else:
            raise HTTPException(status_code=400, detail="Failed to stop bot")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/metrics/{account_name}")
async def get_metrics(account_name: str):
    try:
        # Load metrics from logs
        logs_path = f"accounts/{account_name}/logs/log.txt"
        metrics = {
            "blocks_grabbed": 0,
            "total_earnings": 0.0,
            "today_earnings": 0.0,
            "success_rate": 0.0,
            "last_activity": None
        }
        
        if os.path.exists(logs_path):
            with open(logs_path, "r") as f:
                logs = f.readlines()
            
            # Parse logs for metrics (simplified)
            blocks_grabbed = len([line for line in logs if "Block accepted" in line])
            metrics["blocks_grabbed"] = blocks_grabbed
            metrics["total_earnings"] = blocks_grabbed * 25.0  # Estimated
            
            if logs:
                metrics["last_activity"] = datetime.now().isoformat()
        
        return metrics
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/metrics/summary")
async def get_summary_metrics():
    total_blocks = 0
    total_earnings = 0.0
    active_bots = 0
    
    accounts_dir = "accounts"
    if os.path.exists(accounts_dir):
        for account_name in os.listdir(accounts_dir):
            if bot_manager.get_bot_status(account_name) == "running":
                active_bots += 1
            
            logs_path = f"{accounts_dir}/{account_name}/logs/log.txt"
            if os.path.exists(logs_path):
                with open(logs_path, "r") as f:
                    logs = f.readlines()
                blocks = len([line for line in logs if "Block accepted" in line])
                total_blocks += blocks
                total_earnings += blocks * 25.0
    
    return {
        "total_blocks": total_blocks,
        "total_earnings": total_earnings,
        "active_bots": active_bots,
        "total_accounts": len(os.listdir(accounts_dir)) if os.path.exists(accounts_dir) else 0
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)