from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import subprocess, json

app = FastAPI()

class Preferences(BaseModel):
    days: List[str]
    hours: List[str]
    min_rate: float

CONFIG_PATH = "automation/config.json"

@app.post("/save_config")
def save_config(preferences: Preferences):
    with open(CONFIG_PATH, "w") as f:
        json.dump(preferences.dict(), f)
    return {"status": "config_saved"}

@app.post("/start_bot")
def start_bot():
    try:
        subprocess.Popen(["python", "automation/bot.py"])
        return {"status": "bot_started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status")
def get_status():
    try:
        with open("automation/status.log") as f:
            return {"logs": f.read()}
    except:
        return {"logs": "No logs yet"}
