from cryptography.fernet import Fernet
from datetime import datetime
import os
from ..config import LOG_DIR

class SecureLogger:
    def __init__(self, encryption_key):
        self.cipher = Fernet(encryption_key)
        LOG_DIR.mkdir(exist_ok=True)
        self.log_file = LOG_DIR / "system.log"

    def log(self, action, username, description, suspicious=False):
        timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        log_entry = f"{timestamp} | {username} | {action} | {description} | {'SUSPICIOUS' if suspicious else 'Normal'}"
        
        encrypted = self.cipher.encrypt(log_entry.encode())
        with open(self.log_file, 'ab') as f:
            f.write(encrypted + b'\n')