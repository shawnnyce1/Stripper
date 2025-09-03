# logger.py
import os
import time
from datetime import datetime

LOG_FILE = os.path.join(os.path.dirname(__file__), "status.log")
PERF_FILE = os.path.join(os.path.dirname(__file__), "performance.log")

def log(msg: str):
    """Logs a message to both console and log file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_msg = f"[{timestamp}] {msg}"
    print(full_msg)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(full_msg + "\n")

def log_perf(action: str, success: bool, elapsed: float):
    """Logs performance metrics like grab time, retries, success."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = "SUCCESS" if success else "FAIL"
    with open(PERF_FILE, "a", encoding="utf-8") as f:
        f.write(f"{timestamp},{action},{status},{elapsed:.2f}s\n")
