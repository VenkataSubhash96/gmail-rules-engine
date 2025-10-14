from datetime import datetime, timezone
import sqlite3
from gmail.client import fetch_emails
import re

DB_FILE = "emails.db"

def parse_received_at(received_at_str):
    received_at_str = re.sub(r"\s*\(.*\)$", "", received_at_str)
    received_at_str = re.sub(r"\sGMT$", " +0000", received_at_str)
    formats = [
        "%a, %d %b %Y %H:%M:%S %z",
        "%d %b %Y %H:%M:%S %z",
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(received_at_str, fmt)
            return dt.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue
    print(f"Warning: Could not parse received_at '{received_at_str}'")
    return None

def store_emails_in_db(max_results=500):
    """
    Fetch emails using Gmail API and store them in SQLite.
    """
    emails = fetch_emails(max_results=max_results)
    if not emails:
        return 0

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    for email in emails:
        iso_received_at = parse_received_at(email.get("received_at"))
        
        cursor.execute("""
        INSERT INTO emails (id, subject, sender, recipient, snippet, body, received_at, is_read, is_starred, inbox_type)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            subject=excluded.subject,
            sender=excluded.sender,
            recipient=excluded.recipient,
            snippet=excluded.snippet,
            body=excluded.body,
            received_at=excluded.received_at
        """, (
            email.get("id"),
            email.get("subject"),
            email.get("from"),
            email.get("to"),
            email.get("snippet"),
            email.get("body", ""),
            iso_received_at,
            email.get("is_read"),
            email.get("is_starred"),
            email.get("inbox_type")
        ))

    conn.commit()
    conn.close()
    print(f"{len(emails)} emails stored in the database.")
    return len(emails)

if __name__ == "__main__":
    store_emails_in_db()
