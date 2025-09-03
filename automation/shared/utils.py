import re
import os
import time
from datetime import datetime

def extract_rate(text):
    """Extract block rate from string, e.g., '$54.00' → 54.0"""
    match = re.search(r"\$(\d+(\.\d+)?)", text)
    return float(match.group(1)) if match else 0.0

def extract_duration(text):
    """Extract duration from string like '3 hrs 15 min' → 3.25"""
    hrs = re.search(r"(\d+)\s*hr", text)
    mins = re.search(r"(\d+)\s*min", text)
    h = int(hrs.group(1)) if hrs else 0
    m = int(mins.group(1)) if mins else 0
    return round(h + m / 60.0, 2)

def within_hour_range(block_time: str, hour_range: list):
    """Check if block time is within allowed hour range"""
    try:
        start_time = datetime.strptime(block_time.split(" - ")[0], "%I:%M %p")
        lower = datetime.strptime(hour_range[0], "%H:%M")
        upper = datetime.strptime(hour_range[1], "%H:%M")
        return lower.time() <= start_time.time() <= upper.time()
    except Exception:
        return False

def get_hour_range(config):
    """Return a range object for checking current time"""
    return HourRange(config["hour_range"][0], config["hour_range"][1])

def prioritize_blocks(blocks, config, account_name=None):
    """Filter and sort blocks based on duration, rate, and hour"""
    filtered = []
    for block in blocks:
        rate = extract_rate(block["text"])
        duration = extract_duration(block["text"])
        time_window = block.get("text", "")

        if (rate >= config["min_rate"] and
            config["min_duration"] <= duration <= config["max_duration"] and
            within_hour_range(time_window, config["hour_range"])):

            block["rate"] = rate
            block["duration"] = duration
            filtered.append(block)

    return sorted(filtered, key=lambda b: (-b["rate"], -b["duration"]))

def take_screenshot(driver, account_name, label="screenshot"):
    """Save screenshot with timestamp per account"""
    folder = f"accounts/{account_name}/screenshots"
    os.makedirs(folder, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(folder, f"{label}_{timestamp}.png")
    driver.save_screenshot(path)

class HourRange:
    """Helper to check if current hour is within range"""
    def __init__(self, start, end):
        self.start = datetime.strptime(start, "%H:%M").time()
        self.end = datetime.strptime(end, "%H:%M").time()

    def contains(self, now_str):
        now = datetime.strptime(now_str, "%H:%M").time()
        return self.start <= now <= self.end
