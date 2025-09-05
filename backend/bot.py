import os

# Fix Android SDK path BEFORE any other imports - Force override system variables
android_sdk_path = r"C:\Users\Akpor Samuel\AppData\Local\Android\Sdk"

# Clear any existing variables first
for key in ["ANDROID_HOME", "ANDROID_SDK_ROOT"]:
    if key in os.environ:
        del os.environ[key]

# Set clean paths
os.environ["ANDROID_HOME"] = android_sdk_path
os.environ["ANDROID_SDK_ROOT"] = android_sdk_path
os.environ["PATH"] = f"{android_sdk_path}\\platform-tools;{android_sdk_path}\\tools;{os.environ.get('PATH', '')}"

# Verify the path is set correctly
print(f"[INFO] ANDROID_HOME set to: '{os.environ.get('ANDROID_HOME')}'")
print(f"[INFO] ANDROID_SDK_ROOT set to: '{os.environ.get('ANDROID_SDK_ROOT')}'")
print(f"[INFO] Path exists: {os.path.exists(android_sdk_path)}")

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

# Check if .env file exists
if os.path.exists('.env'):
    print("[INFO] .env file found")
else:
    print("[WARNING] .env file not found! Please create one with your credentials.")

FLEX_USERNAME = os.getenv("FLEX_USERNAME")
FLEX_PASSWORD = os.getenv("FLEX_PASSWORD")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
APP_PACKAGE = os.getenv("APP_PACKAGE", "com.amazon.flex.rabbit")
APP_ACTIVITY = os.getenv("APP_ACTIVITY", "com.amazon.rabbit.android.presentation.core.LaunchActivity")
DEVICE_NAME = os.getenv("DEVICE_NAME", "R94Y200EH1T")
APPIUM_PORT = os.getenv("APPIUM_PORT", "4725")

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
# Android version (using default)
# -------------------
PLATFORM_VERSION = "14"  # Default Android version

# -------------------
# Connection test
# -------------------
def test_connection():
    """Test basic connectivity before starting the bot"""
    print("[INFO] Testing connections...")
    
    try:
        # Test Appium server - try both endpoints for compatibility
        endpoints = [f"http://127.0.0.1:{APPIUM_PORT}/status", f"http://127.0.0.1:{APPIUM_PORT}/wd/hub/status"]
        server_responding = False
        
        for endpoint in endpoints:
            try:
                response = requests.get(endpoint, timeout=5)
                if response.status_code == 200:
                    print(f"[INFO] Appium server responding at {endpoint}")
                    server_responding = True
                    break
            except:
                continue
        
        if not server_responding:
            print("[ERROR] Appium server not responding on any endpoint")
            return False
            
        # Test ADB connection
        result = subprocess.run([f"{android_sdk_path}\\platform-tools\\adb.exe", "devices"], 
                              capture_output=True, text=True, timeout=10)
        if "device" not in result.stdout:
            print("[ERROR] No Android device found. Run 'adb devices' to check.")
            print(f"ADB output: {result.stdout}")
            return False
            
        print("[INFO] Connection tests passed")
        return True
        
    except subprocess.TimeoutExpired:
        print("[ERROR] ADB command timed out")
        return False
    except FileNotFoundError:
        print("[ERROR] ADB not found. Check Android SDK installation.")
        return False
    except Exception as e:
        print(f"[ERROR] Connection test failed: {e}")
        return False

# -------------------
# Appium driver with compatibility fixes
# -------------------
def init_driver():
    print("[INFO] Initializing Appium driver...")
    
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
    options.skipServerInstallation = True
    options.skipDeviceInitialization = True
    
    # Explicitly set Android SDK path as capability
    options.set_capability("appium:androidHome", android_sdk_path)
    options.set_capability("appium:androidSdkRoot", android_sdk_path)

    print(f"[INFO] Using Android SDK: {os.environ.get('ANDROID_HOME')}")
    print(f"[INFO] Connecting to Appium on port {APPIUM_PORT}...")
    
    # Try different endpoint formats for compatibility with Appium 3.x
    connection_urls = [
        f"http://127.0.0.1:{APPIUM_PORT}",
        f"http://127.0.0.1:{APPIUM_PORT}/wd/hub"
    ]
    
    for url in connection_urls:
        try:
            print(f"[DEBUG] Trying connection URL: {url}")
            driver = webdriver.Remote(
                command_executor=url,
                options=options
            )
            print("[SUCCESS] Connected to Appium successfully!")
            return driver
        except Exception as e:
            print(f"[WARNING] Connection failed with {url}: {e}")
            continue
    
    print("[ERROR] Failed to connect with any URL format")
    raise Exception("Could not connect to Appium server")

# -------------------
# Debug helper function
# -------------------
def debug_current_screen(driver):
    """Print current screen information for debugging"""
    try:
        print(f"[DEBUG] Current activity: {driver.current_activity}")
        print(f"[DEBUG] Current package: {driver.current_package}")
        
        # Get page source to see what elements are available
        page_source = driver.page_source
        print(f"[DEBUG] Page source length: {len(page_source)}")
        
        # Look for common login-related text
        login_indicators = ["sign in", "login", "email", "password", "username"]
        for indicator in login_indicators:
            if indicator.lower() in page_source.lower():
                print(f"[DEBUG] Found '{indicator}' in page source")
        
        # Look for Amazon Flex specific elements
        flex_indicators = ["block", "flex", "rabbit", "amazon"]
        for indicator in flex_indicators:
            if indicator.lower() in page_source.lower():
                print(f"[DEBUG] Found '{indicator}' in page source")
                
    except Exception as e:
        print(f"[DEBUG] Error getting screen info: {e}")

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
# Auto-login with improved error handling
# -------------------
def auto_login(driver):
    print("[INFO] Attempting auto-login...")
    
    # First, debug what's currently on screen
    debug_current_screen(driver)
    
    try:
        # Check if already logged in by looking for blocks layout
        driver.find_element("id", "com.amazon.flex.rabbit:id/block_item_layout")
        print("[INFO] Already logged in - found blocks layout")
        return True
    except:
        print("[INFO] No blocks layout found - may need to login")
    
    # Try to find any login-related elements with different approaches
    login_element_ids = [
        "ap_email_login",           # Standard Amazon login
        "ap_email",                 # Alternative email field
        "username",                 # Generic username
        "email",                    # Generic email
        "signin_username",          # Alternative
        "user_id"                   # Alternative
    ]
    
    password_element_ids = [
        "ap_password",              # Standard Amazon password
        "password",                 # Generic password
        "signin_password",          # Alternative
        "user_password"             # Alternative
    ]
    
    sign_in_button_ids = [
        "signInSubmit",             # Standard Amazon
        "sign_in_button",           # Alternative
        "login_button",             # Alternative
        "submit_button"             # Alternative
    ]
    
    username_field = None
    password_field = None
    sign_in_button = None
    
    # Try to find username field
    for element_id in login_element_ids:
        try:
            username_field = driver.find_element("id", element_id)
            print(f"[DEBUG] Found username field: {element_id}")
            break
        except:
            continue
    
    # Try to find password field
    for element_id in password_element_ids:
        try:
            password_field = driver.find_element("id", element_id)
            print(f"[DEBUG] Found password field: {element_id}")
            break
        except:
            continue
    
    # Try to find sign in button
    for element_id in sign_in_button_ids:
        try:
            sign_in_button = driver.find_element("id", element_id)
            print(f"[DEBUG] Found sign in button: {element_id}")
            break
        except:
            continue
    
    # If we can't find login elements, maybe we need to navigate to login screen
    if not username_field:
        print("[DEBUG] No username field found. Looking for 'Sign in with Amazon' button...")
        
        # Look for the Amazon Flex specific sign in button
        try:
            sign_in_with_amazon = driver.find_element("id", "com.amazon.flex.rabbit:id/sign_in_button")
            print("[DEBUG] Found 'Sign in with Amazon' button, clicking it...")
            sign_in_with_amazon.click()
            time.sleep(5)  # Wait for Amazon login page to load
            
            # Now try to find the Amazon login fields again
            for element_id in login_element_ids:
                try:
                    username_field = driver.find_element("id", element_id)
                    print(f"[DEBUG] Found username field after clicking 'Sign in with Amazon': {element_id}")
                    break
                except:
                    continue
                    
            # Also try to find password field
            for element_id in password_element_ids:
                try:
                    password_field = driver.find_element("id", element_id)
                    print(f"[DEBUG] Found password field after navigation: {element_id}")
                    break
                except:
                    continue
                    
        except Exception as e:
            print(f"[DEBUG] Could not find or click 'Sign in with Amazon' button: {e}")
            
        # If still no username field, try other navigation elements
        if not username_field:
            navigation_elements = [
                "sign_in",
                "login", 
                "get_started",
                "continue",
                "next"
            ]
            
            for nav_id in navigation_elements:
                try:
                    nav_element = driver.find_element("id", nav_id)
                    print(f"[DEBUG] Found navigation element: {nav_id}")
                    nav_element.click()
                    time.sleep(3)
                    
                    # Try to find username field again
                    for element_id in login_element_ids:
                        try:
                            username_field = driver.find_element("id", element_id)
                            print(f"[DEBUG] Found username field after navigation: {element_id}")
                            break
                        except:
                            continue
                            
                    if username_field:
                        break
                except:
                    continue
    
    if not username_field or not password_field:
        print("[ERROR] Could not find login fields")
        print("[DEBUG] Available elements on screen:")
        try:
            # Get all elements with IDs for debugging
            all_elements = driver.find_elements("xpath", "//*[@resource-id]")
            for element in all_elements[:15]:  # Show first 15 elements
                try:
                    resource_id = element.get_attribute("resource-id")
                    text = element.text
                    class_name = element.get_attribute("class")
                    print(f"[DEBUG] Element: {resource_id} - Text: '{text}' - Class: '{class_name}'")
                except:
                    continue
                    
            # Also look for input fields by class name
            print("[DEBUG] Looking for input fields by class...")
            input_elements = driver.find_elements("class name", "android.widget.EditText")
            for i, element in enumerate(input_elements):
                try:
                    resource_id = element.get_attribute("resource-id")
                    text = element.text
                    hint = element.get_attribute("hint")
                    print(f"[DEBUG] Input field {i}: ID='{resource_id}', Text='{text}', Hint='{hint}'")
                    
                    # Try to use the first EditText as username field
                    if i == 0 and not username_field:
                        username_field = element
                        print(f"[DEBUG] Using input field {i} as username field")
                    # Try to use the second EditText as password field  
                    elif i == 1 and not password_field:
                        password_field = element
                        print(f"[DEBUG] Using input field {i} as password field")
                        
                except Exception as e:
                    print(f"[DEBUG] Error examining input field {i}: {e}")
                    continue
                    
        except Exception as e:
            print(f"[DEBUG] Error getting elements: {e}")
            
        # If we still don't have fields, return False
        if not username_field or not password_field:
            return False
    
    try:
        # Clear and fill username
        username_field.clear()
        username_field.send_keys(FLEX_USERNAME)
        print("[DEBUG] Username entered")
        
        # Find password field again if needed
        if not password_field:
            for element_id in password_element_ids:
                try:
                    password_field = driver.find_element("id", element_id)
                    break
                except:
                    continue
        
        # Clear and fill password  
        password_field.clear()
        password_field.send_keys(FLEX_PASSWORD)
        print("[DEBUG] Password entered")
        
        # Find sign in button again if needed
        if not sign_in_button:
            for element_id in sign_in_button_ids:
                try:
                    sign_in_button = driver.find_element("id", element_id)
                    break
                except:
                    continue
        
        # Click sign in
        if sign_in_button:
            sign_in_button.click()
            print("[DEBUG] Sign in button clicked")
        else:
            print("[WARNING] No sign in button found. Looking for clickable elements...")
            
            # Look for any button or clickable element that might be the sign in button
            try:
                # Look for buttons by class
                buttons = driver.find_elements("class name", "android.widget.Button")
                for i, button in enumerate(buttons):
                    try:
                        text = button.text.lower()
                        resource_id = button.get_attribute("resource-id")
                        print(f"[DEBUG] Button {i}: ID='{resource_id}', Text='{text}'")
                        
                        if any(keyword in text for keyword in ["sign in", "login", "submit", "continue"]):
                            print(f"[DEBUG] Found potential sign in button: {text}")
                            button.click()
                            print("[DEBUG] Clicked potential sign in button")
                            break
                    except:
                        continue
                        
                # Also look for ViewGroups that might be custom buttons
                view_groups = driver.find_elements("class name", "android.view.ViewGroup")
                for i, view_group in enumerate(view_groups[:5]):  # Check first 5 ViewGroups
                    try:
                        resource_id = view_group.get_attribute("resource-id")
                        clickable = view_group.get_attribute("clickable")
                        
                        if clickable == "true" and resource_id and "button" in resource_id.lower():
                            print(f"[DEBUG] Found clickable ViewGroup (potential button): {resource_id}")
                            view_group.click()
                            print("[DEBUG] Clicked ViewGroup button")
                            break
                    except:
                        continue
                        
                # If still no button found, try pressing Enter on password field
                if password_field:
                    print("[DEBUG] Trying Enter key on password field")
                    password_field.send_keys("\n")
                    
            except Exception as e:
                print(f"[DEBUG] Error looking for sign in button: {e}")
                # Fallback: try Enter key
                if password_field:
                    password_field.send_keys("\n")
        
        # Wait for login to complete and check for 2FA
        time.sleep(8)
        
        # Check if 2FA is required
        try:
            # Look for common 2FA elements
            two_fa_indicators = [
                "verification", "code", "authenticate", "security", 
                "two-factor", "2fa", "otp", "verify"
            ]
            
            page_source = driver.page_source.lower()
            if any(indicator in page_source for indicator in two_fa_indicators):
                print("[INFO] 2FA detected! Please complete verification manually.")
                print("[INFO] Check your email for verification code and complete login on device.")
                print("[INFO] Bot will wait 60 seconds for manual completion...")
                
                # Wait up to 60 seconds for manual 2FA completion
                for i in range(12):  # 12 * 5 = 60 seconds
                    time.sleep(5)
                    try:
                        driver.find_element("id", "com.amazon.flex.rabbit:id/block_item_layout")
                        print("[SUCCESS] Login completed after 2FA!")
                        return True
                    except:
                        if i < 11:  # Don't print on last iteration
                            print(f"[INFO] Still waiting for login completion... ({(i+1)*5}s)")
                        continue
                
                print("[ERROR] 2FA completion timed out")
                return False
        except Exception as e:
            print(f"[DEBUG] Error checking for 2FA: {e}")
        
        # Regular login check
        try:
            driver.find_element("id", "com.amazon.flex.rabbit:id/block_item_layout")
            print("[SUCCESS] Login successful!")
            return True
        except:
            print("[WARNING] Login may have failed - could not find blocks layout")
            debug_current_screen(driver)
            return False
            
    except Exception as e:
        print(f"[ERROR] Login process failed: {e}")
        debug_current_screen(driver)
        return False

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
# Block scraping & grabbing with better error handling
# -------------------
def get_available_blocks(driver):
    blocks = []
    try:
        block_elements = driver.find_elements("id", "com.amazon.flex.rabbit:id/block_item_layout")
        print(f"[DEBUG] Found {len(block_elements)} block elements")
        
        for el in block_elements:
            try:
                rate_el = el.find_element("id", "com.amazon.flex.rabbit:id/block_rate")
                duration_el = el.find_element("id", "com.amazon.flex.rabbit:id/block_duration")

                rate_text = rate_el.text.replace("$", "").strip()
                duration_text = duration_el.text.replace("min", "").strip()
                
                rate = float(rate_text)
                duration = int(duration_text)

                blocks.append({"rate": rate, "duration": duration, "element": el})
                print(f"[DEBUG] Block found: ${rate} for {duration}min")
            except Exception as e:
                print(f"[DEBUG] Could not parse block element: {e}")
                continue
    except Exception as e:
        print(f"[DEBUG] No blocks found or error accessing blocks: {e}")

    blocks.sort(key=lambda x: x["rate"], reverse=True)
    return blocks

def grab_block(driver, block):
    try:
        print(f"[INFO] Attempting to grab block: ${block['rate']} for {block['duration']}min")
        block["element"].click()
        time.sleep(0.5)
        
        try:
            confirm_button = driver.find_element("id", "com.amazon.flex.rabbit:id/confirm_button")
            confirm_button.click()
            print(f"[DEBUG] Confirm button clicked")
        except Exception as e:
            print(f"[DEBUG] No confirm button found or error clicking: {e}")
        
        send_telegram_message(f"✅ Grabbed block: ${block['rate']} for {block['duration']} min")
        print(f"[SUCCESS] Grabbed block: ${block['rate']} for {block['duration']} min")
        
    except Exception as e:
        print(f"[ERROR] Failed to grab block: {e}")

# -------------------
# Fast scanning loop with CPU saver
# -------------------
def scan_loop(driver):
    print("[INFO] Starting scan loop...")
    idle_counter = 0
    current_interval = SCAN_FAST_INTERVAL

    while True:
        try:
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
            
        except Exception as e:
            print(f"[ERROR] Error in scan loop: {e}")
            time.sleep(5)  # Wait before retrying

# -------------------
# Auto-refresh loop
# -------------------
def refresh_loop(driver):
    print("[INFO] Starting refresh loop...")
    while True:
        try:
            if not is_within_hour_range():
                time.sleep(30)
                continue
            
            # Swipe to refresh
            driver.swipe(500, 1200, 500, 400, 300)
            time.sleep(REFRESH_FAST_INTERVAL)
            
        except Exception as e:
            print(f"[ERROR] Error in refresh loop: {e}")
            time.sleep(5)  # Wait before retrying

# -------------------
# Main function with comprehensive error handling
# -------------------
def main():
    print("[INFO] Starting Amazon Flex Grabber Bot...")
    print(f"[INFO] App Package: {APP_PACKAGE}")
    print(f"[INFO] Device: {DEVICE_NAME}")
    print(f"[INFO] Appium Port: {APPIUM_PORT}")
    
    # Check credentials
    if not FLEX_USERNAME or not FLEX_PASSWORD:
        print("[ERROR] FLEX_USERNAME or FLEX_PASSWORD not set in .env file")
        print("Please update your .env file with your Amazon Flex credentials")
        return
    
    print(f"[INFO] Username: {'SET' if FLEX_USERNAME else 'NOT SET'}")
    print(f"[INFO] Password: {'SET' if FLEX_PASSWORD else 'NOT SET'}")
    
    # Test connections first
    if not test_connection():
        print("[ERROR] Pre-flight checks failed. Please:")
        print("1. Make sure Appium server is running: appium --port 4725")
        print("2. Check device connection: adb devices")
        print("3. Enable USB debugging on your Android device")
        return
    
    # Initialize driver
    try:
        driver = init_driver()
    except Exception as e:
        print(f"[ERROR] Failed to initialize driver: {e}")
        return
    
    # Auto-login
    try:
        if not auto_login(driver):
            print("[ERROR] Failed to login. Please check:")
            print("1. Your Amazon Flex credentials in .env file")
            print("2. That the Amazon Flex app is installed")
            print("3. That you can login manually with these credentials")
            driver.quit()
            return
    except Exception as e:
        print(f"[ERROR] Login process failed: {e}")
        driver.quit()
        return
    
    # Start bot loops
    try:
        print("[INFO] Starting bot threads...")
        threading.Thread(target=scan_loop, args=(driver,), daemon=True).start()
        threading.Thread(target=refresh_loop, args=(driver,), daemon=True).start()

        print("[SUCCESS] Bot started successfully! Press CTRL+C to stop.")
        print(f"[INFO] Scanning for blocks with rate >= ${MIN_RATE} and duration {MIN_DURATION}-{MAX_DURATION} min")
        print(f"[INFO] Active hours: {HOUR_RANGE[0]}:00 - {HOUR_RANGE[1]}:00")
        print(f"[INFO] Active days: {', '.join(DAYS)}")
        
        # Keep main thread alive
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n[INFO] Stopping bot...")
        try:
            driver.quit()
        except:
            pass
        print("[INFO] Bot stopped.")
        
    except Exception as e:
        print(f"[ERROR] Bot crashed: {e}")
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    main()