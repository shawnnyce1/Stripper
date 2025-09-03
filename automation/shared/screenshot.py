import os
from datetime import datetime

def save_screenshot(driver, account_name, label="screenshot"):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{label}_{timestamp}.png"
    dir_path = os.path.join("accounts", account_name, "screenshots")
    os.makedirs(dir_path, exist_ok=True)
    filepath = os.path.join(dir_path, filename)

    try:
        driver.save_screenshot(filepath)
        print(f"[{account_name}] 📸 Screenshot saved: {filepath}")
        return filepath
    except Exception as e:
        print(f"[{account_name}] ❌ Screenshot failed: {e}")
        return None
