import os
import time
from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class FlexGrabber:
    def __init__(self):
        # Set Android SDK path
        os.environ['ANDROID_HOME'] = r'C:\Users\Akpor Samuel\AppData\Local\Android\Sdk'
        os.environ['PATH'] += f";{os.environ['ANDROID_HOME']}\\tools;{os.environ['ANDROID_HOME']}\\platform-tools"
        
        # Desired Capabilities
        self.desired_caps = {
            "platformName": "Android",
            "appium:automationName": "UiAutomator2",
            "appium:deviceName": "R94Y200EH1T",
            "appium:appPackage": "com.amazon.flex.rabbit",
            "appium:appActivity": "com.amazon.rabbit.android.presentation.login.LoginActivity",
            "appium:noReset": True,
            "appium:newCommandTimeout": 300
        }
        
        self.driver = None
        self.wait = None
        
    def connect(self):
        """Connect to Appium server and start session"""
        try:
            options = UiAutomator2Options().load_capabilities(self.desired_caps)
            self.driver = webdriver.Remote("http://127.0.0.1:4723", options=options)
            self.wait = WebDriverWait(self.driver, 10)
            print("✓ Connected to Amazon Flex app")
            return True
        except Exception as e:
            print(f"✗ Failed to connect: {e}")
            return False
    
    def find_blocks(self):
        """Look for available blocks"""
        try:
            # Common selectors for blocks (may need adjustment based on app version)
            block_selectors = [
                "//android.widget.TextView[contains(@text, '$')]",  # Price indicators
                "//android.widget.Button[contains(@text, 'Accept')]",  # Accept buttons
                "//android.view.ViewGroup[contains(@content-desc, 'block')]",  # Block containers
                "//*[contains(@text, 'PM') or contains(@text, 'AM')]"  # Time indicators
            ]
            
            blocks_found = []
            for selector in block_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    if elements:
                        blocks_found.extend(elements)
                        print(f"✓ Found {len(elements)} elements with selector: {selector}")
                except:
                    continue
            
            return blocks_found
            
        except Exception as e:
            print(f"✗ Error finding blocks: {e}")
            return []
    
    def grab_block(self, block_element):
        """Attempt to grab a block"""
        try:
            # Try to click the block or accept button
            block_element.click()
            print("✓ Clicked on block")
            
            # Look for accept/confirm button
            accept_selectors = [
                "//android.widget.Button[contains(@text, 'Accept')]",
                "//android.widget.Button[contains(@text, 'Confirm')]",
                "//android.widget.Button[contains(@text, 'Take')]"
            ]
            
            for selector in accept_selectors:
                try:
                    accept_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    accept_btn.click()
                    print("✓ Block grabbed successfully!")
                    return True
                except TimeoutException:
                    continue
            
            return False
            
        except Exception as e:
            print(f"✗ Error grabbing block: {e}")
            return False
    
    def refresh_page(self):
        """Refresh the blocks page"""
        try:
            # Swipe down to refresh
            size = self.driver.get_window_size()
            start_x = size['width'] // 2
            start_y = size['height'] // 4
            end_y = size['height'] * 3 // 4
            
            self.driver.swipe(start_x, start_y, start_x, end_y, 1000)
            time.sleep(2)
            print("✓ Refreshed page")
            
        except Exception as e:
            print(f"✗ Error refreshing: {e}")
    
    def run_grabber(self, max_attempts=100, refresh_interval=5):
        """Main grabber loop"""
        if not self.connect():
            return
        
        print(f"🚀 Starting Amazon Flex Grabber (max {max_attempts} attempts)")
        
        for attempt in range(max_attempts):
            print(f"\n--- Attempt {attempt + 1}/{max_attempts} ---")
            
            # Find available blocks
            blocks = self.find_blocks()
            
            if blocks:
                print(f"📦 Found {len(blocks)} potential blocks")
                
                # Try to grab the first available block
                for i, block in enumerate(blocks):
                    print(f"Attempting to grab block {i + 1}")
                    if self.grab_block(block):
                        print("🎉 Successfully grabbed a block!")
                        return
                    time.sleep(1)
            else:
                print("📭 No blocks found")
            
            # Refresh and wait
            self.refresh_page()
            time.sleep(refresh_interval)
        
        print(f"⏰ Completed {max_attempts} attempts without success")
    
    def disconnect(self):
        """Close the session"""
        if self.driver:
            self.driver.quit()
            print("✓ Disconnected from app")

if __name__ == "__main__":
    grabber = FlexGrabber()
    
    try:
        # Run the grabber
        grabber.run_grabber(max_attempts=50, refresh_interval=3)
    except KeyboardInterrupt:
        print("\n🛑 Stopped by user")
    finally:
        grabber.disconnect()