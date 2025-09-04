import asyncio
import json
import os
import logging
from datetime import datetime
from typing import Dict, Optional
from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class FlexBot:
    def __init__(self, account_name: str):
        self.account_name = account_name
        self.account_dir = f"accounts/{account_name}"
        self.driver = None
        self.is_running = False
        self.logger = self._setup_logger()
        
    def _setup_logger(self):
        logger = logging.getLogger(f"FlexBot_{self.account_name}")
        logger.setLevel(logging.INFO)
        
        # Create logs directory
        logs_dir = f"{self.account_dir}/logs"
        os.makedirs(logs_dir, exist_ok=True)
        
        # File handler
        handler = logging.FileHandler(f"{logs_dir}/log.txt")
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def load_config(self):
        """Load account configuration"""
        config_path = f"{self.account_dir}/config.json"
        env_path = f"{self.account_dir}/.env"
        
        if not os.path.exists(config_path) or not os.path.exists(env_path):
            raise FileNotFoundError(f"Configuration files not found for {self.account_name}")
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Load environment variables
        with open(env_path, 'r') as f:
            for line in f:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
        
        return config
    
    def setup_driver(self):
        """Setup Appium driver for Android"""
        try:
            options = UiAutomator2Options()
            options.platform_name = "Android"
            options.device_name = "Android Emulator"
            options.app_package = "com.amazon.rabbit"
            options.app_activity = "com.amazon.rabbit.MainActivity"
            options.automation_name = "UiAutomator2"
            
            self.driver = webdriver.Remote(
                command_executor='http://localhost:4723',
                options=options
            )
            self.logger.info("Appium driver initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to setup driver: {str(e)}")
            return False
    
    async def login(self):
        """Login to Amazon Flex app"""
        try:
            email = os.getenv('EMAIL')
            password = os.getenv('PASSWORD')
            
            if not email or not password:
                raise ValueError("Email or password not found in environment")
            
            # Wait for login screen
            email_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "ap_email"))
            )
            
            email_field.send_keys(email)
            
            # Continue button
            continue_btn = self.driver.find_element(By.ID, "continue")
            continue_btn.click()
            
            # Password field
            password_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "ap_password"))
            )
            password_field.send_keys(password)
            
            # Sign in button
            signin_btn = self.driver.find_element(By.ID, "signInSubmit")
            signin_btn.click()
            
            self.logger.info("Login successful")
            return True
            
        except Exception as e:
            self.logger.error(f"Login failed: {str(e)}")
            return False
    
    async def check_for_blocks(self):
        """Check for available delivery blocks"""
        try:
            # Navigate to offers page
            offers_tab = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//android.widget.TextView[@text='Offers']"))
            )
            offers_tab.click()
            
            # Look for available blocks
            blocks = self.driver.find_elements(By.CLASS_NAME, "offer-card")
            
            if blocks:
                self.logger.info(f"Found {len(blocks)} available blocks")
                return blocks
            else:
                self.logger.info("No blocks available")
                return []
                
        except Exception as e:
            self.logger.error(f"Error checking for blocks: {str(e)}")
            return []
    
    async def accept_block(self, block_element):
        """Accept a delivery block"""
        try:
            # Click on the block
            block_element.click()
            
            # Look for accept button
            accept_btn = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//android.widget.Button[contains(@text, 'Accept')]"))
            )
            accept_btn.click()
            
            # Confirm acceptance
            confirm_btn = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//android.widget.Button[contains(@text, 'Confirm')]"))
            )
            confirm_btn.click()
            
            self.logger.info("Block accepted successfully")
            return True
            
        except TimeoutException:
            self.logger.warning("Block acceptance timed out - may have been taken")
            return False
        except Exception as e:
            self.logger.error(f"Error accepting block: {str(e)}")
            return False
    
    async def run_bot_cycle(self):
        """Main bot cycle"""
        while self.is_running:
            try:
                blocks = await self.check_for_blocks()
                
                for block in blocks:
                    if not self.is_running:
                        break
                    
                    success = await self.accept_block(block)
                    if success:
                        self.logger.info("Block grabbed successfully!")
                        break
                
                # Wait before next check
                await asyncio.sleep(5)
                
            except Exception as e:
                self.logger.error(f"Error in bot cycle: {str(e)}")
                await asyncio.sleep(10)
    
    async def start(self):
        """Start the bot"""
        try:
            self.load_config()
            
            if not self.setup_driver():
                return False
            
            if not await self.login():
                return False
            
            self.is_running = True
            self.logger.info("Bot started successfully")
            
            # Start the main bot cycle
            await self.run_bot_cycle()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start bot: {str(e)}")
            return False
    
    async def stop(self):
        """Stop the bot"""
        self.is_running = False
        if self.driver:
            self.driver.quit()
        self.logger.info("Bot stopped")

class BotManager:
    def __init__(self):
        self.bots: Dict[str, FlexBot] = {}
        self.bot_tasks: Dict[str, asyncio.Task] = {}
    
    async def start_bot(self, account_name: str) -> bool:
        """Start a bot for the given account"""
        if account_name in self.bots and self.bots[account_name].is_running:
            return False  # Bot already running
        
        try:
            bot = FlexBot(account_name)
            self.bots[account_name] = bot
            
            # Start bot in background task
            task = asyncio.create_task(bot.start())
            self.bot_tasks[account_name] = task
            
            return True
            
        except Exception as e:
            print(f"Error starting bot for {account_name}: {str(e)}")
            return False
    
    async def stop_bot(self, account_name: str) -> bool:
        """Stop a bot for the given account"""
        if account_name not in self.bots:
            return False
        
        try:
            bot = self.bots[account_name]
            await bot.stop()
            
            # Cancel the task
            if account_name in self.bot_tasks:
                self.bot_tasks[account_name].cancel()
                del self.bot_tasks[account_name]
            
            del self.bots[account_name]
            return True
            
        except Exception as e:
            print(f"Error stopping bot for {account_name}: {str(e)}")
            return False
    
    def get_bot_status(self, account_name: str) -> str:
        """Get the status of a bot"""
        if account_name in self.bots and self.bots[account_name].is_running:
            return "running"
        return "stopped"

# Legacy function for backward compatibility
async def start_bot_for_account(account_path: str):
    """Start bot for account (legacy function)"""
    account_name = os.path.basename(account_path)
    bot = FlexBot(account_name)
    await bot.start()