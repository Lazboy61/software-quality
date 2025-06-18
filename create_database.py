import sqlite3
from datetime import datetime

# Verbind met database (maakt hem aan als hij nog niet bestaat)
conn = sqlite3.connect("software_quality.db")
cursor = conn.cursor()

# USERS TABEL
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT CHECK(role IN ('superadmin', 'sysadmin', 'engineer')) NOT NULL,
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
    license_number TEXT,
    phone_number TEXT,
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
    top_speed INTEGER,
    battery_capacity INTEGER,
    soc INTEGER,
    target_range_min INTEGER,
    target_range_max INTEGER,
    latitude REAL,
    longitude REAL,
    out_of_service INTEGER CHECK(out_of_service IN (0, 1)) DEFAULT 0,
    mileage INTEGER,
    last_maintenance TEXT,
    in_service_date TEXT DEFAULT CURRENT_TIMESTAMP
);
""")

# Opslaan en sluiten
conn.commit()
conn.close()

print("✅ Database en tabellen zijn aangemaakt.")
