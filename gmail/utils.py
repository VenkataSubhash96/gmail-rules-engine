import sqlite3

DB_FILE = "emails.db"

def get_header(headers, name):
    """Return the value of a header by name, or None."""
    return next((header["value"] for header in headers if header["name"] == name), None)

def get_emails_from_db():
    """Fetch all emails from the database as a list of dictionaries."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM emails")
    emails = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return emails