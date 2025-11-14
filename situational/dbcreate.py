import sqlite3

# Connect to (or create) the database file
conn = sqlite3.connect("memory/Reminders.db")

# Create a cursor object to execute SQL commands
cursor = conn.cursor()

# Create the reminders table
cursor.execute("""
CREATE TABLE IF NOT EXISTS reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    to_remind DATETIME,
    done INTEGER DEFAULT 0
)
""")

# Commit and close
conn.commit()
conn.close()

print("✅ Reminders.db created with table 'reminders'")
