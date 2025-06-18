import sqlite3
from pathlib import Path
from ..config import DB_PATH, SUPERADMIN_CREDENTIALS
from .models import initialize_tables
from .encryption import EncryptionManager

class Database:
    def __init__(self):
        self.encryption = EncryptionManager()
        self.conn = None
        self._initialize()

    def _initialize(self):
        """Initialize database and tables"""
        Path(DB_PATH).parent.mkdir(exist_ok=True)
        self.conn = sqlite3.connect(DB_PATH)
        initialize_tables(self.conn)
        self._create_superadmin()
        
    def _create_superadmin(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ?", 
                      (SUPERADMIN_CREDENTIALS["username"],))
        if not cursor.fetchone():
            from auth.roles import create_user
            create_user(
                self.conn,
                self.encryption,
                **SUPERADMIN_CREDENTIALS
            )
        self.conn.commit()

    def get_connection(self):
        return self.conn

    def close(self):
        if self.conn:
            self.conn.close()