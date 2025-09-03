import os
import time
import threading
import base64
from datetime import datetime
from dotenv import load_dotenv
from appium.webdriver.common.appiumby import AppiumBy

from automation.shared.logger import log
from automation.shared.config import load_config
from automation.shared.notification import send_telegram

from automation.captcha_solver import solve_captcha
from automation.shared.appium_setup import create_driver

load_dotenv()

PAUSE_FLAGS = {}

def screenshot_and_notify(driver, account_name, message):
    screenshot_path = f"accounts/{account_name}/screenshots"
    os.makedirs(screenshot_path, exist_ok=True)
    file_name = f"{screenshot_path}/{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    driver.save_screenshot(file_name)
    send_telegram(f"{account_name}: {message}", image_path=file_name)

def block_matches_criteria(block_text, config):
    rate = int(block_text.split("$")[-1].split()[0])
    for day in config["days"]:
        if day in block_text:
            start_hour = int(config["hour_range"][0].split(":")[0])
            end_hour = int(config["hour_range"][1].split(":")[0])
            duration = int(block_text.split("hr")[0].split()[-1])
            if config["min_duration"] <= duration <= config["max_duration"] and rate >= config["min_rate"]:
                return True
    return False

def scan_loop(driver, config, account_name):
    dry_run = os.getenv("DRY_RUN", "false").lower() == "true"
    log(f"Starting scan loop. Dry run: {dry_run}", account_name)
    while True:
        if PAUSE_FLAGS.get(account_name):
            log("Paused... waiting", account_name)
            time.sleep(5)
            continue

        try:
            blocks = driver.find_elements(AppiumBy.XPATH, "//android.widget.TextView[contains(@text,'block')]")
            for block in blocks:
                block_text = block.text
                if block_matches_criteria(block_text, config):
                    log(f"Found matching block: {block_text}", account_name)
                    screenshot_and_notify(driver, account_name, f"Matching block: {block_text}")
                    if not dry_run:
                        block.click()
                        log("Clicked block", account_name)
                    else:
                        log("Dry run active - did not click", account_name)
                    time.sleep(5)
        except Exception as e:
            log(f"Error in scan loop: {e}", account_name)

        time.sleep(1)

def start_bot_for_account(account_path):
    account_name = os.path.basename(account_path)
    PAUSE_FLAGS[account_name] = False
    try:
        config = load_config(account_path)
        driver = create_driver(account_path)
        log("Driver started", account_name)

        scan_thread = threading.Thread(target=scan_loop, args=(driver, config, account_name), daemon=True)
        scan_thread.start()

    except Exception as e:
        log(f"Bot startup error: {e}", account_name)
