import bcrypt
import re
from datetime import datetime
import getpass
from config import CITIES

def validate_username(username):
    pattern = r'^[a-zA-Z_][a-zA-Z0-9_\'\.]{7,9}$'
    return re.match(pattern, username) is not None

def validate_password_complexity(password):
    if len(password) < 12 or len(password) > 30:
        return False
    checks = [
        r'[A-Z]',
        r'[a-z]',
        r'[0-9]',
        r'[~!@#$%&_\-+=`|\\(){}[\]:";\'<>,.?/]'
    ]
    return all(re.search(check, password) for check in checks)

def prompt_password():
    while True:
        password = getpass.getpass("Wachtwoord (12-30 tekens, min 1 hoofdletter, cijfer en speciaal teken): ")
        if validate_password_complexity(password):
            return password
        print("Wachtwoord voldoet niet aan de eisen.")

def create_user(conn, encryption, username, password, role, first_name, last_name, email, license_number):
    if not validate_username(username):
        raise ValueError("Ongeldige gebruikersnaam")
    if not validate_password_complexity(password):
        raise ValueError("Ongeldig wachtwoord")

    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    email_encrypted = encryption.encrypt(email)
    license_encrypted = encryption.encrypt(license_number)

    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (username, password_hash, role, first_name, last_name, email, license_number, registration_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (username, hashed_pw, role, first_name, last_name, email_encrypted, license_encrypted, datetime.now()))
    conn.commit()
