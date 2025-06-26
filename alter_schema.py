import sqlite3

conn = sqlite3.connect('peo_users.db')
cursor = conn.cursor()

cursor.execute('ALTER TABLE users ADD COLUMN password_changed TEXT')

conn.commit()
conn.close()

print("✅ Column 'password_changed' added.")
