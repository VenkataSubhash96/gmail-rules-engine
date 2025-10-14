from gmail.auth import get_gmail_service
from gmail.client import move_message as api_move_message

def move_message(message_id, folder):
    """
    Move email to a folder in Gmail (no DB update needed).
    """
    service = get_gmail_service()
    api_move_message(service, message_id, folder)
