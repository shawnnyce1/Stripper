# automation/shared/login.py
import os
import time
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from dotenv import load_dotenv

load_dotenv()

FLEX_EMAIL = os.getenv("FLEX_EMAIL")
FLEX_PASSWORD = os.getenv("FLEX_PASSWORD")
FLEX_2FA = os.getenv("FLEX_2FA")  # Optional: if you have a default OTP or method

class FlexLoginBot:
    def __init__(self, device_name="emulator-5554", app_package="com.amazon.flex", app_activity=".MainActivity"):
        self.desired_caps = {
            "platformName": "Android",
            "deviceName": device_name,
            "appPackage": app_package,
            "appActivity": app_activity,
            "noReset": True,  # keep logged-in session
        }
        self.driver = webdriver.Remote("http://localhost:4723/wd/hub", self.desired_caps)
        self.driver.implicitly_wait(10)

    def login(self, email=FLEX_EMAIL, password=FLEX_PASSWORD):
        try:
            # Enter email
            email_field = self.driver.find_element(AppiumBy.ID, "com.amazon.flex:id/email")
            email_field.clear()
            email_field.send_keys(email)

            # Click Continue
            self.driver.find_element(AppiumBy.ID, "com.amazon.flex:id/continue_button").click()
            time.sleep(1)

            # Enter password
            password_field = self.driver.find_element(AppiumBy.ID, "com.amazon.flex:id/password")
            password_field.clear()
            password_field.send_keys(password)

            # Click Login
            self.driver.find_element(AppiumBy.ID, "com.amazon.flex:id/sign_in_button").click()
            time.sleep(2)

            # Optional 2FA
            if FLEX_2FA:
                try:
                    otp_field = self.driver.find_element(AppiumBy.ID, "com.amazon.flex:id/otp")
                    otp_field.send_keys(FLEX_2FA)
                    self.driver.find_element(AppiumBy.ID, "com.amazon.flex:id/otp_continue_button").click()
                    time.sleep(2)
                except Exception:
                    print("2FA not required or OTP field not found")

            print("Login successful!")
            return True
        except Exception as e:
            print(f"Login failed: {e}")
            return False

    def close(self):
        self.driver.quit()


if __name__ == "__main__":
    bot = FlexLoginBot()
    bot.login()
    bot.close()
