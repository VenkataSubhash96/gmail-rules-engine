from gmail.auth import get_gmail_service
from gmail.fetcher import fetch_inbox_emails

def mark_as_read(service, message_id):
    """
    Mark an email as read by removing the UNREAD label.
    """
    service.users().messages().modify(
        userId="me",
        id=message_id,
        body={"removeLabelIds": ["UNREAD"]}
    ).execute()

def mark_as_unread(service, message_id):
    """
    Mark an email as unread by adding the UNREAD label.
    """
    service.users().messages().modify(
        userId="me",
        id=message_id,
        body={"addLabelIds": ["UNREAD"]}
    ).execute()

def move_message(service, message_id, folder):
    """
    Move an email to a folder (Gmail label). 
    If the folder is not INBOX, remove INBOX to "archive" it.
    """
    add_labels = [folder]
    remove_labels = []
    if folder != "INBOX":
        remove_labels.append("INBOX")

    service.users().messages().modify(
        userId="me",
        id=message_id,
        body={
            "addLabelIds": add_labels,
            "removeLabelIds": remove_labels
        }
    ).execute()

def fetch_emails(max_results=1000):
    service = get_gmail_service()
    return fetch_inbox_emails(service, max_results)
