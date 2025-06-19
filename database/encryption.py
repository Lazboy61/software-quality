from cryptography.fernet import Fernet
import os

class EncryptionManager:
    def __init__(self, key_file="secret.key"):
        self.key_file = key_file
        self.fernet = self._load_or_create_key()

    def _load_or_create_key(self):
        if not os.path.exists(self.key_file):
            key = Fernet.generate_key()
            with open(self.key_file, "wb") as f:
                f.write(key)
        else:
            with open(self.key_file, "rb") as f:
                key = f.read()
        return Fernet(key)

    def encrypt(self, data: str) -> str:
        return self.fernet.encrypt(data.encode()).decode()

    def decrypt(self, token: str) -> str:
        return self.fernet.decrypt(token.encode()).decode()
