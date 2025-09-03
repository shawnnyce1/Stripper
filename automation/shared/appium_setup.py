from appium import webdriver
from appium.options.android import UiAutomator2Options

def create_driver(account_name):
    """Initialize Appium driver for given account/device."""
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.device_name = account_name  # MUST match `adb devices` name
    options.app_package = "com.amazon.mShop.android.shopping"
    options.app_activity = "com.amazon.mShop.home.HomeActivity"
    options.automation_name = "UiAutomator2"

    # If using different Appium ports for devices, update here
    port = 4723  # Or dynamically assign per account if needed
    return webdriver.Remote(f"http://localhost:{port}/wd/hub", options=options)
