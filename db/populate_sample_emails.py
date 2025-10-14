import sqlite3
from datetime import datetime, timedelta, timezone
import random

DB_FILE = "emails.db"

def generate_sample_emails(n=100):
    subjects = ["Hello", "Meeting", "Invoice", "Greetings", "Update", "Reminder", "Project", "Follow-up", "Newsletter", "Alert"]
    senders = ["alice@example.com", "bob@example.com", "carol@example.com", "dave@example.com", "eve@example.com"]
    recipients = ["you@example.com"]
    inbox_types = ["INBOX", "TRASH", "STARRED"]

    emails = []

    now = datetime.now(timezone.utc)
    for i in range(1, n+1):
        delta_days = random.randint(0, 30)
        delta_seconds = random.randint(0, 86400)
        received_at = now - timedelta(days=delta_days, seconds=delta_seconds)
        received_at_str = received_at.strftime("%Y-%m-%d %H:%M:%S")

        email = {
            "id": str(i),
            "subject": random.choice(subjects) + f" #{i}",
            "from": random.choice(senders),
            "to": random.choice(recipients),
            "snippet": "This is a snippet of the email content.",
            "body": "This is the full email body.",
            "received_at": received_at_str,
            "is_read": random.choice([0, 1]),
            "is_starred": random.choice([0, 1]),
            "inbox_type": random.choice(inbox_types),
        }
        emails.append(email)

    return emails

def store_sample_emails(emails):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    for email in emails:
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
            email["id"],
            email["subject"],
            email["from"],
            email["to"],
            email["snippet"],
            email["body"],
            email["received_at"],
            email["is_read"],
            email["is_starred"],
            email["inbox_type"]
        ))

    conn.commit()
    conn.close()
    print(f"{len(emails)} sample emails stored in the database.")

if __name__ == "__main__":
    sample_emails = generate_sample_emails(100)
    store_sample_emails(sample_emails)
