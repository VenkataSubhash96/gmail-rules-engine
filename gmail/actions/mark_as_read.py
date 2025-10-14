from gmail.auth import get_gmail_service
from gmail.client import mark_as_read as api_mark_as_read
import sqlite3

DB_FILE = "emails.db"

def mark_as_read(message_id):
    """
    Mark email as read in Gmail and update is_read column in DB.
    """
    service = get_gmail_service()
    api_mark_as_read(service, message_id)

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE emails SET is_read = 1 WHERE id = ?", (message_id,))
    conn.commit()
    conn.close()
