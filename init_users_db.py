import sqlite3

# Connect to (or create) the database
conn = sqlite3.connect('peo_users.db')
cursor = conn.cursor()

# Drop the table if it already exists (⚠️ Only do this intentionally)
cursor.execute("DROP TABLE IF EXISTS users")

# Create the users table with email
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    password BLOB NOT NULL,
    role TEXT DEFAULT 'director',
    password_changed INTEGER DEFAULT 0
)
''')

conn.commit()
conn.close()

print("✅ Users table recreated with email-based login.")
