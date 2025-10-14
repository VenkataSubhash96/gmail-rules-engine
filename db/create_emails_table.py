import sqlite3

DB_FILE = "emails.db"

def create_emails_table():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS emails (
        id TEXT PRIMARY KEY,
        subject TEXT,
        sender TEXT,
        recipient TEXT,
        snippet TEXT,
        body TEXT,
        received_at TEXT,
        is_read BOOLEAN,
        is_starred BOOLEAN,
        inbox_type TEXT
    )
    """)

    conn.commit()
    conn.close()
    print("Migration complete: emails table created.")

if __name__ == "__main__":
    create_emails_table()
