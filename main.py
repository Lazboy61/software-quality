import sqlite3
import bcrypt
import getpass
from cryptography.fernet import Fernet
import os
import logging
from datetime import datetime
import shutil
import re

DB_NAME = "scooter_management.db"
BACKUP_DIR = "backups"
LOG_FILE = "app.log"

# 🔐 Wachtwoord hashen
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed)

# 🔑 Fernet sleutel laden
def load_key():
    if not os.path.exists("secret.key"):
        key = Fernet.generate_key()
        with open("secret.key", "wb") as key_file:
            key_file.write(key)
    else:
        with open("secret.key", "rb") as key_file:
            key = key_file.read()
    return key

fernet = Fernet(load_key())

# 🔓 Gegevens decrypten
def decrypt_data(encrypted_data):
    if not encrypted_data:
        return ""
    try:
        return fernet.decrypt(encrypted_data.encode()).decode()
    except Exception as e:
        logging.error(f"Decryptie fout: {e}")
        return "⚠️ Ongeldig"


# 🛠️ Database initialiseren
def initialize_database():
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # USERS TABEL
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT CHECK(role IN ('superadmin', 'sysadmin', 'engineer')) NOT NULL,
        email TEXT,
        license_number TEXT,
        first_name TEXT,
        last_name TEXT,
        registration_date TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # TRAVELLERS TABEL
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS travellers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        birthday TEXT,
        gender TEXT,
        street_name TEXT,
        house_number TEXT,
        zip_code TEXT,
        city TEXT,
        email TEXT,
        license_number TEXT UNIQUE CHECK(length(license_number) = 10),
        phone_number TEXT CHECK(length(phone_number) BETWEEN 10 AND 15),
        registration_date TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # SCOOTERS TABEL
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scooters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        brand TEXT NOT NULL,
        model TEXT NOT NULL,
        serial_number TEXT UNIQUE NOT NULL CHECK(length(serial_number) <= 17),
        top_speed INTEGER CHECK(top_speed BETWEEN 0 AND 100),
        battery_capacity INTEGER CHECK(battery_capacity BETWEEN 0 AND 100),
        soc INTEGER CHECK(soc BETWEEN 0 AND 100),
        target_range_min INTEGER,
        target_range_max INTEGER,
        latitude REAL CHECK(latitude BETWEEN -90 AND 90),
        longitude REAL CHECK(longitude BETWEEN -180 AND 180),
        out_of_service INTEGER CHECK(out_of_service IN (0, 1)) DEFAULT 0,
        mileage INTEGER CHECK(mileage >= 0),
        last_maintenance TEXT,
        in_service_date TEXT DEFAULT CURRENT_TIMESTAMP,
        last_updated TEXT
    );
    """)

    # Maak superadmin aan als die nog niet bestaat
    cursor.execute("SELECT id FROM users WHERE username = 'super_admin'")  # Aangepast van 'superadmin'
    if not cursor.fetchone():
        password_hash = hash_password("Admin_123?").decode()  # Aangepast van 'admin123'
        cursor.execute("""
            INSERT INTO users (username, password_hash, role)
            VALUES (?, ?, ?)
        """, ("super_admin", password_hash, "superadmin"))

    conn.commit()
    conn.close()
    logging.info("Database geïnitialiseerd")

# 📂 Backup maken
def backup_database():
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(BACKUP_DIR, f"{DB_NAME}.backup_{timestamp}")
    shutil.copy2(DB_NAME, backup_file)
    logging.info(f"Backup gemaakt: {backup_file}")
    print(f"\n✅ Backup gemaakt: {backup_file}")

# 🔄 Restore database
def restore_database():
    if not os.path.exists(BACKUP_DIR):
        print("Geen backups beschikbaar")
        return
    
    backups = [f for f in os.listdir(BACKUP_DIR) if f.startswith(DB_NAME)]
    if not backups:
        print("Geen backups beschikbaar")
        return
    
    print("\nBeschikbare backups:")
    for i, backup in enumerate(backups, 1):
        print(f"{i}. {backup}")
    
    try:
        choice = int(input("Kies backup om te restoren (0 om te annuleren): "))
        if choice == 0:
            return
        
        selected_backup = os.path.join(BACKUP_DIR, backups[choice-1])
        shutil.copy2(selected_backup, DB_NAME)
        print(f"\n✅ Database hersteld van {selected_backup}")
        logging.info(f"Database hersteld van {selected_backup}")
    except (ValueError, IndexError):
        print("Ongeldige keuze")

# 👥 Travellers registreren
def register_traveller():
    print("\n=== Nieuwe traveller registreren ===")
    
    first_name = input("Voornaam: ")
    last_name = input("Achternaam: ")
    birthday = input("Geboortedatum (YYYY-MM-DD): ")
    gender = input("Geslacht (M/V/X): ")
    street_name = input("Straatnaam: ")
    house_number = input("Huisnummer: ")
    zip_code = input("Postcode: ")
    city = input("Woonplaats: ")
    email = input("E-mail: ")
    
    # Rijbewijsnummer validatie (10 tekens)
    while True:
        license_number = input("Rijbewijsnummer (10 tekens): ")
        if len(license_number) == 10:
            break
        print("Rijbewijsnummer moet precies 10 tekens lang zijn")
    
    # Telefoonnummer validatie (10-15 cijfers)
    while True:
        phone_number = input("Telefoonnummer (10-15 cijfers): ")
        if re.match(r'^\d{10,15}$', phone_number):
            break
        print("Ongeldig telefoonnummer. Gebruik 10-15 cijfers")

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO travellers (
                first_name, last_name, birthday, gender, street_name, house_number,
                zip_code, city, email, license_number, phone_number
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            first_name, last_name, birthday, gender, street_name, house_number,
            zip_code, city, email, license_number, phone_number
        ))
        
        conn.commit()
        print("\n✅ Traveller succesvol geregistreerd")
        logging.info(f"Nieuwe traveller geregistreerd: {first_name} {last_name}")
    except sqlite3.IntegrityError as e:
        print("\n❌ Fout: Rijbewijsnummer bestaat al")
        logging.warning(f"Traveller registratie fout: {e}")
    except Exception as e:
        print("\n❌ Er ging iets mis bij de registratie")
        logging.error(f"Traveller registratie fout: {e}")
    finally:
        conn.close()

# 👥 Travellers bekijken
def view_travellers():
    print("\n=== Travellers Overzicht ===")
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, first_name, last_name, email, phone_number, registration_date 
            FROM travellers ORDER BY last_name
        """)
        travellers = cursor.fetchall()

        print("\nID | Naam | E-mail | Telefoon | Registratiedatum")
        print("-" * 80)
        for traveller in travellers:
            print(f"{traveller[0]} | {traveller[1]} {traveller[2]} | {traveller[3]} | {traveller[4]} | {traveller[5]}")

    except Exception as e:
        logging.error(f"Travellers ophalen fout: {e}")
        print("\n❌ Fout bij ophalen travellers")
    finally:
        conn.close()

# 🛵 Scooter toevoegen
def add_scooter():
    print("\n=== Nieuwe Scooter Toevoegen ===")
    
    brand = input("Merk: ")
    model = input("Model: ")
    
    # Serienummer validatie
    while True:
        serial_number = input("Serienummer (max 17 tekens): ")
        if len(serial_number) <= 17:
            break
        print("Serienummer mag maximaal 17 tekens zijn")
    
    # Optionele velden
    top_speed = input("Top snelheid (km/u, leeg laten indien onbekend): ")
    battery_capacity = input("Batterij capaciteit (%, leeg laten indien onbekend): ")
    soc = input("State of Charge (%, leeg laten indien onbekend): ")
    
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO scooters (
                brand, model, serial_number, top_speed, battery_capacity, soc,
                in_service_date, last_updated
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            brand, model, serial_number, 
            int(top_speed) if top_speed else None,
            int(battery_capacity) if battery_capacity else None,
            int(soc) if soc else None,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        
        conn.commit()
        print("\n✅ Scooter succesvol toegevoegd")
        logging.info(f"Nieuwe scooter toegevoegd: {brand} {model} ({serial_number})")
    except sqlite3.IntegrityError:
        print("\n❌ Fout: Serienummer bestaat al")
        logging.warning("Scooter toevoegen: serienummer bestaat al")
    except ValueError:
        print("\n❌ Fout: Ongeldige numerieke waarde")
        logging.warning("Scooter toevoegen: ongeldige numerieke waarde")
    except Exception as e:
        print("\n❌ Er ging iets mis bij het toevoegen")
        logging.error(f"Scooter toevoegen fout: {e}")
    finally:
        conn.close()

# 🛵 Scooter bewerken
def edit_scooter(role):
    print("\n=== Scooter Bewerken ===")
    scooter_id = input("Scooter ID om te bewerken: ")
    
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # Haal huidige gegevens op
        cursor.execute("SELECT * FROM scooters WHERE id = ?", (scooter_id,))
        scooter = cursor.fetchone()
        
        if not scooter:
            print("\n❌ Scooter niet gevonden")
            return
        
        print("\nHuidige gegevens:")
        print(f"Merk: {scooter[1]}")
        print(f"Model: {scooter[2]}")
        print(f"Serienummer: {scooter[3]}")
        print(f"Top snelheid: {scooter[4]}")
        print(f"Batterij capaciteit: {scooter[5]}%")
        print(f"State of Charge: {scooter[6]}%")
        print(f"Kilometerstand: {scooter[12]}")
        print(f"Status: {'Buiten gebruik' if scooter[10] else 'In gebruik'}")

        # Velden die kunnen worden bewerkt
        if role in ['superadmin', 'sysadmin']:
            print("\nBewerkbare velden:")
            print("1. Top snelheid")
            print("2. Batterij capaciteit")
            print("3. State of Charge")
            print("4. Kilometerstand")
            print("5. Status")
            print("6. Laatste onderhoudsdatum")
        else:
            print("\nBewerkbare velden (engineer):")
            print("3. State of Charge")
            print("4. Kilometerstand")
            print("5. Status")

        choice = input("\nKies veld om te bewerken (0 om te annuleren): ")
        
        if choice == "0":
            return
        
        # Bevestig nieuwe waarde
        field_name = ""
        new_value = None
        
        if choice == "1" and role in ['superadmin', 'sysadmin']:
            field_name = "top_speed"
            new_value = input("Nieuwe top snelheid (km/u): ")
        elif choice == "2" and role in ['superadmin', 'sysadmin']:
            field_name = "battery_capacity"
            new_value = input("Nieuwe batterij capaciteit (%): ")
        elif choice == "3":
            field_name = "soc"
            new_value = input("Nieuwe State of Charge (%): ")
        elif choice == "4":
            field_name = "mileage"
            new_value = input("Nieuwe kilometerstand: ")
        elif choice == "5":
            field_name = "out_of_service"
            new_value = input("Status (0=In gebruik, 1=Buiten gebruik): ")
        elif choice == "6" and role in ['superadmin', 'sysadmin']:
            field_name = "last_maintenance"
            new_value = input("Laatste onderhoudsdatum (YYYY-MM-DD): ")
        else:
            print("\n❌ Ongeldige keuze")
            return
        
        # Update uitvoeren
        cursor.execute(f"""
            UPDATE scooters 
            SET {field_name} = ?, last_updated = ?
            WHERE id = ?
        """, (
            new_value,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            scooter_id
        ))
        
        conn.commit()
        print("\n✅ Scooter succesvol bijgewerkt")
        logging.info(f"Scooter {scooter_id} bijgewerkt: {field_name}={new_value}")
    except Exception as e:
        print("\n❌ Fout bij bewerken scooter")
        logging.error(f"Scooter bewerken fout: {e}")
    finally:
        conn.close()

# 🛵 Scooter locaties bekijken
def view_scooter_locations():
    print("\n=== Scooter Locaties ===")
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, brand, model, latitude, longitude, soc 
            FROM scooters 
            WHERE latitude IS NOT NULL AND longitude IS NOT NULL
        """)
        scooters = cursor.fetchall()

        if not scooters:
            print("\nGeen scooters met locatiegegevens gevonden")
            return
        
        print("\nID | Merk | Model | Locatie | SOC")
        print("-" * 60)
        for scooter in scooters:
            print(f"{scooter[0]} | {scooter[1]} | {scooter[2]} | ({scooter[3]}, {scooter[4]}) | {scooter[5]}%")

    except Exception as e:
        logging.error(f"Scooter locaties ophalen fout: {e}")
        print("\n❌ Fout bij ophalen locaties")
    finally:
        conn.close()

# 🛵 Scooter onderhoud bekijken
def view_scooter_maintenance():
    print("\n=== Scooter Onderhoud ===")
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, brand, model, last_maintenance, mileage, out_of_service 
            FROM scooters 
            ORDER BY last_maintenance ASC
        """)
        scooters = cursor.fetchall()

        print("\nID | Merk | Model | Laatste onderhoud | Kilometerstand | Status")
        print("-" * 80)
        for scooter in scooters:
            status = "Buiten gebruik" if scooter[5] else "In gebruik"
            print(f"{scooter[0]} | {scooter[1]} | {scooter[2]} | {scooter[3] or 'Onbekend'} | {scooter[4]} km | {status}")

    except Exception as e:
        logging.error(f"Scooter onderhoud ophalen fout: {e}")
        print("\n❌ Fout bij ophalen onderhoudsinfo")
    finally:
        conn.close()

# 📋 Menu op basis van rol
def show_menu(user_id, role):
    while True:
        print(f"\n=== Hoofdmenu ({role.upper()}) ===")
        
        if role == "superadmin":
            # Superadmin menu opties
            print("1. Gebruikers beheren")
            print("2. Travellers beheren")
            print("3. Scooters beheren")
            print("4. Backups beheren")
            print("5. Logs bekijken")
            print("0. Uitloggen")
            
        elif role == "sysadmin":
            # Sysadmin menu opties
            print("1. Travellers beheren")
            print("2. Scooters beheren")
            print("3. Service Engineers beheren")
            print("4. Backups maken")
            print("5. Logs bekijken")
            print("0. Uitloggen")
            
        elif role == "engineer":
            # Engineer menu opties
            print("1. Scooter status bekijken")
            print("2. Scooter status bijwerken")
            print("0. Uitloggen")

        choice = input("\nKeuze: ")

        if choice == "0":
            break
        
        # Superadmin opties
        elif role == "superadmin":
            if choice == "1":
                manage_users()
            elif choice == "2":
                traveller_menu(role)
            elif choice == "3":
                scooter_menu(role)
            elif choice == "4":
                view_my_details(user_id)
            elif choice == "5":
                backup_database()
            elif choice == "6":
                restore_database()
        
        # Sysadmin opties
        elif role == "sysadmin":
            if choice == "1":
                traveller_menu(role)
            elif choice == "2":
                scooter_menu(role)
            elif choice == "3":
                view_my_details(user_id)
            elif choice == "4":
                backup_database()
        
        # Engineer opties
        elif role == "engineer":
            if choice == "1":
                view_scooter_locations()
            elif choice == "2":
                view_scooter_maintenance()
            elif choice == "3":
                edit_scooter(role)
            elif choice == "4":
                view_my_details(user_id)

# 🛵 Scooter menu
def scooter_menu(role):
    while True:
        print("\n=== Scooter Beheer ===")
        print("1. Scooters bekijken")
        print("2. Scooter toevoegen")
        print("3. Scooter bewerken")
        print("0. Terug naar hoofdmenu")

        choice = input("\nKeuze: ")
        
        if choice == "0":
            break
        elif choice == "1":
            view_scooters()
        elif choice == "2" and role in ['superadmin', 'sysadmin']:
            add_scooter()
        elif choice == "3":
            edit_scooter(role)
        else:
            print("\n❌ Ongeldige keuze of geen rechten")

# 👥 Traveller menu
def traveller_menu(role):
    while True:
        print("\n=== Traveller Beheer ===")
        print("1. Travellers bekijken")
        print("2. Traveller registreren")
        print("0. Terug naar hoofdmenu")

        choice = input("\nKeuze: ")
        
        if choice == "0":
            break
        elif choice == "1":
            view_travellers()
        elif choice == "2":
            register_traveller()
        else:
            print("\n❌ Ongeldige keuze")

# 🛵 Scooters bekijken
def view_scooters():
    print("\n=== Scooters Overzicht ===")
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, brand, model, serial_number, soc, out_of_service, last_updated 
            FROM scooters 
            ORDER BY brand, model
        """)
        scooters = cursor.fetchall()

        print("\nID | Merk | Model | Serienummer | SOC | Status | Laatste update")
        print("-" * 90)
        for scooter in scooters:
            status = "Buiten gebruik" if scooter[5] else "In gebruik"
            print(f"{scooter[0]} | {scooter[1]} | {scooter[2]} | {scooter[3]} | {scooter[4]}% | {status} | {scooter[6]}")

    except Exception as e:
        logging.error(f"Scooters ophalen fout: {e}")
        print("\n❌ Fout bij ophalen scooters")
    finally:
        conn.close()

# 👤 Eigen gegevens bekijken
def view_my_details(user_id):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT username, role, email, license_number, first_name, last_name, registration_date 
            FROM users WHERE id = ?
        """, (user_id,))
        user = cursor.fetchone()

        if user:
            print("\n=== Mijn gegevens ===")
            print(f"Gebruikersnaam: {user[0]}")
            print(f"Rol: {user[1]}")
            print(f"Naam: {user[4]} {user[5]}")
            print(f"Registratiedatum: {user[6]}")
            
            # Decrypt gevoelige gegevens
            if user[2]:
                print(f"E-mail: {decrypt_data(user[2])}")
            if user[3]:
                print(f"Rijbewijsnummer: {decrypt_data(user[3])}")
    except Exception as e:
        logging.error(f"Gegevens ophalen fout: {e}")
        print("\n❌ Fout bij ophalen gegevens")
    finally:
        conn.close()

# 👥 Gebruikers beheren (alleen voor superadmin)
def manage_users():
    print("\n=== Gebruikersbeheer ===")
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("SELECT id, username, role, first_name, last_name, registration_date FROM users")
        users = cursor.fetchall()

        print("\nID | Gebruikersnaam | Rol | Naam | Registratiedatum")
        print("-" * 80)
        for user in users:
            print(f"{user[0]} | {user[1]} | {user[2]} | {user[3]} {user[4]} | {user[5]}")

        print("\nOpties:")
        print("1. Gebruiker verwijderen")
        print("2. Gebruikersrol wijzigen")
        print("0. Terug naar hoofdmenu")
        choice = input("\nKeuze: ")

        if choice == "1":
            user_id = input("ID van te verwijderen gebruiker: ")
            if user_id == "1":
                print("\n❌ Superadmin kan niet verwijderd worden")
                return
            
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
            print("\n✅ Gebruiker verwijderd")
            logging.info(f"Gebruiker verwijderd (ID: {user_id})")
        elif choice == "2":
            user_id = input("ID van gebruiker om rol te wijzigen: ")
            if user_id == "1":
                print("\n❌ Superadmin rol kan niet gewijzigd worden")
                return
            
            new_role = input("Nieuwe rol (sysadmin/engineer): ").lower()
            if new_role not in ['sysadmin', 'engineer']:
                print("\n❌ Ongeldige rol")
                return
            
            cursor.execute("UPDATE users SET role = ? WHERE id = ?", (new_role, user_id))
            conn.commit()
            print("\n✅ Gebruikersrol bijgewerkt")
            logging.info(f"Gebruiker {user_id} rol gewijzigd naar {new_role}")
    except Exception as e:
        logging.error(f"Gebruikersbeheer fout: {e}")
        print("\n❌ Fout bij gebruikersbeheer")
    finally:
        conn.close()

# 🔐 Inloggen
def login():
    print("\n=== Inloggen ===")
    username = input("Gebruikersnaam: ")
    password = getpass.getpass("Wachtwoord: ")

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, password_hash, role FROM users WHERE username = ?
        """, (username,))
        result = cursor.fetchone()

        if result and verify_password(password, result[1].encode()):
            print(f"\n✅ Ingelogd als {username} ({result[2]})")
            logging.info(f"Succesvolle login: {username} ({result[2]})")
            return result[0], result[2]  # return user_id en role
        else:
            print("\n❌ Ongeldige gebruikersnaam of wachtwoord.")
            logging.warning(f"Mislukte loginpoging voor: {username}")
            return None, None
    except Exception as e:
        logging.error(f"Login error: {e}")
        return None, None
    finally:
        conn.close()

# 🆕 Gebruiker registreren
def register_user():
    print("\n=== Nieuwe gebruiker registreren ===")
    username = input("Gebruikersnaam: ")
    
    # Wachtwoord validatie
    while True:
        password = getpass.getpass("Wachtwoord (min. 8 tekens): ")
        if len(password) >= 8:
            break
        print("Wachtwoord moet minimaal 8 tekens lang zijn")

    role = input("Rol (superadmin/sysadmin/engineer): ").lower()
    email = input("E-mail: ")
    license_number = input("Rijbewijsnummer: ")
    first_name = input("Voornaam: ")
    last_name = input("Achternaam: ")

    if role not in ['superadmin', 'sysadmin', 'engineer']:
        print("Ongeldige rol.")
        return

    try:
        password_hash = hash_password(password).decode()
        email_encrypted = fernet.encrypt(email.encode()).decode()
        license_encrypted = fernet.encrypt(license_number.encode()).decode()

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO users (username, password_hash, role, email, license_number, first_name, last_name)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (username, password_hash, role, email_encrypted, license_encrypted, first_name, last_name))
        
        conn.commit()
        print("\n✅ Gebruiker succesvol geregistreerd.")
        logging.info(f"Nieuwe gebruiker geregistreerd: {username} ({role})")
    except sqlite3.IntegrityError:
        print("\n❌ Gebruikersnaam bestaat al.")
        logging.warning(f"Poging tot registratie met bestaande gebruikersnaam: {username}")
    except Exception as e:
        print("\n❌ Er ging iets mis bij de registratie.")
        logging.error(f"Registratiefout: {e}")
    finally:
        conn.close()

# Logging instellen
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode='a'
)

# ▶️ Start
def main():
    initialize_database()
    
    while True:
        print("\n=== Startmenu ===")
        print("1. Inloggen")
        print("2. Registreren (alleen voor systeembeheerders)")
        print("0. Stoppen")

        choice = input("\nKeuze: ")
        if choice == "1":
            user_id, role = login()
            if user_id:
                show_menu(user_id, role)
        elif choice == "2":
            # Alleen superadmin mag nieuwe sysadmins aanmaken
            # Andere gebruikers moeten door superadmin/sysadmin aangemaakt worden
            print("\nNieuwe gebruikers moeten door een beheerder aangemaakt worden")
        elif choice == "0":
            print("\nTot ziens!")
            logging.info("Applicatie afgesloten")
            break
        else:
            print("\n❌ Ongeldige keuze")

if __name__ == "__main__":
    main()