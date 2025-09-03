import os
import json
from dotenv import load_dotenv

# Path to project root and .env file
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
env_path = os.path.join(project_root, '.env')
load_dotenv(dotenv_path=env_path)

def load_env_config():
    required_keys = ["HOUR_RANGE", "TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"]
    config = {}
    for key in required_keys:
        value = os.getenv(key)
        if not value:
            raise KeyError(f"Missing required config key: {key}")
        config[key.lower()] = value
    return config

def load_account_config(account_path):
    config_path = os.path.join(account_path, "config.json")
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config not found for account: {config_path}")

    with open(config_path, encoding="utf-8") as f:
        data = json.load(f)

    required = ["days", "hour_range", "min_rate", "min_duration", "max_duration"]
    for key in required:
        if key not in data:
            raise KeyError(f"Missing config key: {key}")

    if not isinstance(data["hour_range"], list) or len(data["hour_range"]) != 2:
        raise ValueError("hour_range must be a list like ['08:00', '18:00']")

    return data
