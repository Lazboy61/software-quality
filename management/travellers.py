import re
from datetime import datetime
from ..config import CITIES
from ..database.encryption import EncryptionManager

class TravellerManager:
    def __init__(self, conn, encryption):
        self.conn = conn
        self.encryption = encryption

    def validate_license_number(number):
        return re.match(r'^\d{4}[A-Z]{2}$', number) is not None
    
    def format_phone_number(phone): 
        return f"+31-6-{phone}" if re.match(r'^\d{8}$', phone) else None
    
    def add_traveller(self, data):
        if not self.validate_license(data['license_number']):
            raise ValueError("Ongeldig rijbewijsnummer")
        
        if data['city'] not in CITIES:
            raise ValueError("Ongeldige stad")

        encrypted_data = {
            'email': self.encryption.encrypt(data['email']),
            'license_number': self.encryption.encrypt(data['license_number']),
            'phone_number': self.encryption.encrypt(f"+31-6-{data['phone_number']}")
        }

        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO travellers (..., registration_date)
            VALUES (..., ?)
        """, (..., datetime.now()))
        self.conn.commit()