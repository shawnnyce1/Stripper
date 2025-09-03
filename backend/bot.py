import os
import time
import threading
import subprocess
import requests
from datetime import datetime
from appium import webdriver
from appium.options.android import UiAutomator2Options
from dotenv import load_dotenv

# -------------------
# Load environment
# -------------------
load_dotenv()

FLEX_USERNAME = os.getenv("FLEX_USERNAME")
FLEX_PASSWORD = os.getenv("FLEX_PASSWORD")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
APP_PACKAGE = os.getenv("APP_PACKAGE", "com.amazon.flex.rabbit")
APP_ACTIVITY = os.getenv("APP_ACTIVITY", "com.amazon.rabbit.android.presentation.core.LaunchActivity")
DEVICE_NAME = os.getenv("DEVICE_NAME", "emulator-5554")
APPIUM_PORT = os.getenv("APPIUM_PORT", "4724")

SCAN_FAST_INTERVAL = float(os.getenv("SCAN_FAST_INTERVAL", 0.1))
SCAN_SLOW_INTERVAL = float(os.getenv("SCAN_SLOW_INTERVAL", 1.2))
REFRESH_FAST_INTERVAL = float(os.getenv("REFRESH_FAST_INTERVAL", 0.3))
REFRESH_SLOW_INTERVAL = float(os.getenv("REFRESH_SLOW_INTERVAL", 1.5))
CPU_SAVER_ENABLED = os.getenv("CPU_SAVER_ENABLED", "true").lower() == "true"
CPU_SAVER_MAX_IDLE = int(os.getenv("CPU_SAVER_MAX_IDLE", 10))
CPU_SAVER_STEP = int(os.getenv("CPU_SAVER_STEP", 2))
MIN_RATE = float(os.getenv("MIN_RATE", 25))
MIN_DURATION = int(os.getenv("MIN_DURATION", 60))
MAX_DURATION = int(os.getenv("MAX_DURATION", 240))

# Parse hour range properly
hour_range_str = os.getenv("HOUR_RANGE", "6-22")
try:
    HOUR_RANGE = list(map(int, hour_range_str.split("-")))
    if len(HOUR_RANGE) != 2:
        HOUR_RANGE = [6, 22]
except:
    HOUR_RANGE = [6, 22]

DAYS = os.getenv("DAYS", "Mon,Tue,Wed,Thu,Fri,Sat,Sun").split(",")


# -------------------
# Auto-detect Android version from device
# -------------------
def get_android_version(device_name):
    try:
        output = subprocess.check_output(
            ["adb", "-s", device_name, "shell", "getprop", "ro.build.version.release"],
            stderr=subprocess.STDOUT
        )
        version = output.decode().strip()
        print(f"[INFO] Detected Android version: {version}")
        return version
    except Exception as e:
        print(f"[WARN] Could not detect Android version, defaulting to 14: {e}")
        return "14"


PLATFORM_VERSION = get_android_version(DEVICE_NAME)


# -------------------
# Appium driver
# -------------------
def init_driver():
    options = UiAutomator2Options()
    options.platformName = "Android"
    options.automationName = "UiAutomator2"
    options.deviceName = DEVICE_NAME
    options.platformVersion = PLATFORM_VERSION
    options.appPackage = APP_PACKAGE
    options.appActivity = APP_ACTIVITY
    options.noReset = True
    options.newCommandTimeout = 3600
    options.ensureWebviewsHavePages = True
    options.nativeWebScreenshot = True
    options.connectHardwareKeyboard = True

    print(f"[INFO] Connecting to Appium on port {APPIUM_PORT} ...")
    driver = webdriver.Remote(
        command_executor=f"http://127.0.0.1:{APPIUM_PORT}",
        options=options
    )
    print("[INFO] Connected to Appium successfully.")
    return driver


# -------------------
# Telegram notifications
# -------------------
def send_telegram_message(message: str):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": message})
    except Exception as e:
        print(f"[ERROR] Failed to send Telegram message: {e}")


# -------------------
# Utilities
# -------------------
def is_within_hour_range():
    now = datetime.now()
    return (
        HOUR_RANGE[0] <= now.hour <= HOUR_RANGE[1]
        and now.strftime("%a") in DAYS
    )


def filter_block(block):
    return (
        MIN_RATE <= block.get("rate", 0)
        and MIN_DURATION <= block.get("duration", 0) <= MAX_DURATION
    )


# -------------------
# Block scraping & grabbing
# -------------------
def get_available_blocks(driver):
    blocks = []
    try:
        block_elements = driver.find_elements("id", "com.amazon.flex.rabbit:id/block_item_layout")
        for el in block_elements:
            try:
                rate_el = el.find_element("id", "com.amazon.flex.rabbit:id/block_rate")
                duration_el = el.find_element("id", "com.amazon.flex.rabbit:id/block_duration")

                rate = float(rate_el.text.replace("$", "").strip())
                duration = int(duration_el.text.replace("min", "").strip())

                blocks.append({"rate": rate, "duration": duration, "element": el})
            except Exception:
                continue
    except Exception:
        pass

    blocks.sort(key=lambda x: x["rate"], reverse=True)
    return blocks


def grab_block(driver, block):
    try:
        block["element"].click()
        time.sleep(0.2)
        try:
            confirm_button = driver.find_element("id", "com.amazon.flex.rabbit:id/confirm_button")
            confirm_button.click()
        except Exception:
            pass
        send_telegram_message(f"✅ Grabbed block: ${block['rate']} for {block['duration']} min")
        print(f"[SUCCESS] Grabbed block: ${block['rate']} for {block['duration']} min")
    except Exception as e:
        print(f"[ERROR] Failed to grab block: {e}")


# -------------------
# Fast scanning loop with CPU saver
# -------------------
def scan_loop(driver):
    idle_counter = 0
    current_interval = SCAN_FAST_INTERVAL

    while True:
        if not is_within_hour_range():
            print("[INFO] Outside hour range, sleeping 30s...")
            time.sleep(30)
            continue

        blocks = get_available_blocks(driver)
        grabbed_any = False

        for block in blocks:
            if filter_block(block):
                threading.Thread(
                    target=grab_block,
                    args=(driver, block),
                    daemon=True
                ).start()
                grabbed_any = True

        # CPU saver logic
        if CPU_SAVER_ENABLED:
            if not grabbed_any:
                idle_counter += 1
                current_interval = min(
                    SCAN_SLOW_INTERVAL,
                    SCAN_FAST_INTERVAL + CPU_SAVER_STEP * idle_counter
                )
                if idle_counter >= CPU_SAVER_MAX_IDLE:
                    current_interval = SCAN_SLOW_INTERVAL
            else:
                idle_counter = 0
                current_interval = SCAN_FAST_INTERVAL

        time.sleep(current_interval)


# -------------------
# Auto-refresh loop
# -------------------
def refresh_loop(driver):
    while True:
        if not is_within_hour_range():
            time.sleep(30)
            continue
        try:
            driver.swipe(500, 1200, 500, 400, 300)
        except Exception:
            pass
        time.sleep(REFRESH_FAST_INTERVAL)


# -------------------
# Main
# -------------------
def main():
    driver = init_driver()
    threading.Thread(target=scan_loop, args=(driver,), daemon=True).start()
    threading.Thread(target=refresh_loop, args=(driver,), daemon=True).start()

    print("[INFO] Bot started. Press CTRL+C to stop.")
    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
