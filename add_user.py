import sqlite3
import bcrypt
import os

# Connect to DB
#conn = sqlite3.connect('peo_users.db')
#cursor = conn.cursor()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'peo_users.db')

emails = [
    "ohtleeuw@gmail.com",
    "pmleeuw@gmail.com",
    "kagishotlhakung54@gmail.com",
    "kgotsofalo.leeuw@gmail.com",
    "tshepobc@gmail.com",
    "itu_Leeuw13@proton.me",
    "mpho.motaung82@gmail.com",
    "svkleeuw@gmail.com"
]

default_password = 'changeme123'

# === Insert Users ===
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

for email in emails:
    hashed_pw = bcrypt.hashpw(default_password.encode('utf-8'), bcrypt.gensalt())
    try:
        cursor.execute(
            "INSERT INTO users (email, password, password_changed) VALUES (?, ?, 0)",
            (email, hashed_pw)
        )
        print(f"✅ {email} added.")
    except sqlite3.IntegrityError:
        print(f"⚠️ {email} already exists.")

conn.commit()
conn.close()
