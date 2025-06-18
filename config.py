import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "database" / "urban_mobility.db"
BACKUP_DIR = BASE_DIR / "backups"
LOG_DIR = BASE_DIR / "logs"
DB_NAME = "software_quality.db"
LOG_FILE = "app.log"

# Hardcoded superadmin
SUPERADMIN_CREDENTIALS = {
    "username": "super_admin",
    "password": "Admin_123?",
    "role": "superadmin"
}

# Predefined cities
CITIES = [
    "Rotterdam", "Schiedam", "Vlaardingen", 
    "Maassluis", "Capelle aan den IJssel",
    "Spijkenisse", "Hoogvliet", "Pernis",
    "Rozenburg", "Hoek van Holland"
]