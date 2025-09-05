from appium import webdriver
from appium.options.android import UiAutomator2Options

def create_driver(account_name):
    """Initialize Appium driver for given account/device."""
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.automation_name = "UiAutomator2"
    options.device_name = "R94Y200EH1T"
    options.app_package = "com.amazon.flex.rabbit"
    options.app_activity = "com.amazon.rabbit.android.presentation.login.LoginActivity"
    options.no_reset = True
    options.new_command_timeout = 300

    port = 4723
    return webdriver.Remote(f"http://localhost:{port}/wd/hub", options=options)
