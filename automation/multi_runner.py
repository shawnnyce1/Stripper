# multi_runner.py
import os
import threading
from automation.shared.bot_core import start_bot_for_account


ACCOUNTS_DIR = "accounts"

def load_account_dirs():
    return [os.path.join(ACCOUNTS_DIR, name)
            for name in os.listdir(ACCOUNTS_DIR)
            if os.path.isdir(os.path.join(ACCOUNTS_DIR, name))]

def run_all_bots():
    threads = []
    for account_path in load_account_dirs():
        t = threading.Thread(target=start_bot_for_account, args=(account_path,), daemon=True)
        t.start()
        threads.append(t)
    for t in threads:
        t.join()

if __name__ == "__main__":
    run_all_bots()
