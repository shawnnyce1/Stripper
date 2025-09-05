# Amazon Flex Grabber Configuration

# Device Settings
DEVICE_NAME = "R94Y200EH1T"  # Your device ID
ANDROID_HOME = r'C:\Users\Akpor Samuel\AppData\Local\Android\Sdk'

# App Settings
APP_PACKAGE = "com.amazon.flex.rabbit"
APP_ACTIVITY = "com.amazon.rabbit.android.presentation.login.LoginActivity"

# Grabber Settings
MAX_ATTEMPTS = 100  # Maximum number of attempts
REFRESH_INTERVAL = 3  # Seconds between refreshes
CLICK_DELAY = 1  # Delay between clicks
TIMEOUT = 10  # Element wait timeout

# Block Preferences (customize these based on your preferences)
MIN_RATE = 18  # Minimum hourly rate ($)
PREFERRED_TIMES = ["6:00", "7:00", "8:00", "18:00", "19:00", "20:00"]  # Preferred start times
AVOID_TIMES = ["12:00", "13:00", "14:00"]  # Times to avoid

# Appium Server
APPIUM_SERVER = "http://127.0.0.1:4723"

# Logging
ENABLE_LOGGING = True
LOG_FILE = "flex_grabber.log"