import pytest
from unittest.mock import patch, MagicMock
from gmail.client import fetch_emails, mark_as_read, mark_as_unread, move_message

# ------------------------
# Tests
# ------------------------

def test_fetch_emails_calls_dependencies():
    """
    Ensure fetch_emails calls get_gmail_service and fetch_inbox_emails
    and returns the expected result.
    """
    mock_service = MagicMock()
    mock_email_list = [
        {"id": "msg1", "subject": "Test", "from": "sender@example.com", "snippet": "Hi"}
    ]

    with patch("gmail.client.get_gmail_service", return_value=mock_service) as mock_get_service:
        with patch("gmail.client.fetch_inbox_emails", return_value=mock_email_list) as mock_fetch:
            result = fetch_emails(max_results=5)
            mock_get_service.assert_called_once()
            mock_fetch.assert_called_once_with(mock_service, 5)

            assert result == mock_email_list


def test_fetch_emails_default_max_results():
    """
    Ensure default max_results is passed correctly.
    """
    mock_service = MagicMock()
    mock_email_list = []

    with patch("gmail.client.get_gmail_service", return_value=mock_service) as mock_get_service:
        with patch("gmail.client.fetch_inbox_emails", return_value=mock_email_list) as mock_fetch:
            result = fetch_emails()

            mock_fetch.assert_called_once_with(mock_service, 500)
            assert result == mock_email_list

def test_mark_as_read_calls_gmail_api():
    mock_service = MagicMock()
    message_id = "msg123"

    mark_as_read(mock_service, message_id)

    mock_service.users().messages().modify.assert_called_once_with(
        userId="me",
        id=message_id,
        body={"removeLabelIds": ["UNREAD"]}
    )
    mock_service.users().messages().modify().execute.assert_called_once()

def test_mark_as_unread_calls_gmail_api():
    mock_service = MagicMock()
    message_id = "msg456"

    mark_as_unread(mock_service, message_id)

    mock_service.users().messages().modify.assert_called_once_with(
        userId="me",
        id=message_id,
        body={"addLabelIds": ["UNREAD"]}
    )
    mock_service.users().messages().modify().execute.assert_called_once()

def test_move_message_to_inbox():
    mock_service = MagicMock()
    message_id = "msg789"
    folder = "INBOX"

    move_message(mock_service, message_id, folder)

    mock_service.users().messages().modify.assert_called_once_with(
        userId="me",
        id=message_id,
        body={"addLabelIds": ["INBOX"], "removeLabelIds": []}
    )
    mock_service.users().messages().modify().execute.assert_called_once()

def test_move_message_to_other_folder():
    mock_service = MagicMock()
    message_id = "msg101"
    folder = "SPAM"

    move_message(mock_service, message_id, folder)

    mock_service.users().messages().modify.assert_called_once_with(
        userId="me",
        id=message_id,
        body={"addLabelIds": ["SPAM"], "removeLabelIds": ["INBOX"]}
    )
    mock_service.users().messages().modify().execute.assert_called_once()
