import sqlite3

# Connect to SQLite database (creates file if it doesn't exist)
conn = sqlite3.connect('directlink.db')

# Create a cursor object to execute SQL commands
cursor = conn.cursor()

# Create the 'users' table
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role TEXT CHECK(role IN ('Consumer', 'Provider', 'Admin')) NOT NULL
)
''')

# Commit changes and close connection
conn.commit()
conn.close()

print("Database and 'users' table created successfully!")
