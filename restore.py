from cryptography.fernet import Fernet
from datetime import datetime, timedelta
from .config import CITIES
from ..database.encryption import EncryptionManager
from auth import main as auth_main
from database import Database

class RestoreManager:
    def __init__(self):
        self.codes = {}
        
    def generate_code(self, backup_file, admin_id, expires_hours=24):
        code = Fernet.generate_key().decode()[:8]
        self.codes[code] = {
            'backup': backup_file,
            'admin_id': admin_id,
            'expires': datetime.now() + timedelta(hours=expires_hours),
            'used': False
        }
        return code
        
    def validate_code(self, code, admin_id):
        if code in self.codes and not self.codes[code]['used']:
            if self.codes[code]['admin_id'] == admin_id:
                if datetime.now() < self.codes[code]['expires']:
                    self.codes[code]['used'] = True
                    return self.codes[code]['backup']
        return None