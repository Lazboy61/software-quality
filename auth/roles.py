import bcrypt
import re
from datetime import datetime
from ..config import CITIES

def validate_username(username):
    pattern = r'^[a-zA-Z_][a-zA-Z0-9_\'\.]{7,9}$'
    return re.match(pattern, username) is not None


def validate_password_complexity(password):
    if len(password) < 12 or len(password) > 30:
        return False
    checks = [
        r'[A-Z]',  # Minstens 1 hoofdletter
        r'[a-z]',  # Minstens 1 kleine letter
        r'[0-9]',  # Minstens 1 cijfer
        r'[~!@#$%&_\-+=`|\\(){}[\]:";\'<>,.?/]'  # Minstens 1 speciaal teken
    ]
    return all(re.search(check, password) for check in checks)

while True:
    password = getpass.getpass("Wachtwoord (12-30 tekens, min 1 hoofdletter, cijfer en speciaal teken): ")
    if validate_password_complexity(password):
        break
    print("Wachtwoord voldoet niet aan de eisen")

def create_user(conn, encryption, username, password, role, **kwargs):
    if not validate_username(username):
        raise ValueError("Ongeldige gebruikersnaam")
    if not validate_password(password):
        raise ValueError("Ongeldig wachtwoord")

    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    encrypted_data = {
        k: encryption.encrypt(v) 
        for k, v in kwargs.items() 
        if v is not None
    }

    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (username, password_hash, role, registration_date, ...)
        VALUES (?, ?, ?, ?, ...)
    """, (username, hashed_pw, role, datetime.now(), ...))
    conn.commit()