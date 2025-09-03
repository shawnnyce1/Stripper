import os
from datetime import datetime

def log(msg, account_name=None):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    prefix = f"[{account_name}]" if account_name else ""
    print(f"{timestamp} {prefix} {msg}")

    # Optional: Save to file per account
    if account_name:
        log_dir = f"accounts/{account_name}/logs"
        os.makedirs(log_dir, exist_ok=True)
        with open(f"{log_dir}/log.txt", "a", encoding="utf-8") as f:
            f.write(f"{timestamp} {msg}\n")
