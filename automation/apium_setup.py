import os
from appium import webdriver
from appium.options.android import UiAutomator2Options

# Set Android SDK path
os.environ['ANDROID_HOME'] = r'C:\Users\Akpor Samuel\AppData\Local\Android\Sdk'
os.environ['PATH'] += f";{os.environ['ANDROID_HOME']}\\tools;{os.environ['ANDROID_HOME']}\\platform-tools"

# Desired Capabilities
desired_caps = {
    "platformName": "Android",
    "appium:automationName": "UiAutomator2",
    "appium:deviceName": "R94Y200EH1T",  # Replace if your device changes
    "appium:appPackage": "com.amazon.flex.rabbit",
    "appium:appActivity": "com.amazon.rabbit.android.presentation.login.LoginActivity",
    "appium:noReset": True,
    "appium:newCommandTimeout": 300
}

# Load options
options = UiAutomator2Options().load_capabilities(desired_caps)

print("Connecting to Appium server with config:", desired_caps)

# Start Appium session
driver = webdriver.Remote("http://127.0.0.1:4723", options=options)

print("Session started successfully!")

# Close session (you can remove this if you want to keep it open)
driver.quit()
