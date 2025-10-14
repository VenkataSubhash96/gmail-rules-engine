import pytest
from unittest.mock import MagicMock
from gmail.fetcher import fetch_inbox_emails

# ------------------------
# Fixtures
# ------------------------

@pytest.fixture
def fake_service():
    """
    Returns a mocked Gmail API service object.
    """
    service = MagicMock()

    service.users().messages().list().execute.return_value = {
        "messages": [
            {"id": "msg1"},
            {"id": "msg2"}
        ]
    }

    service.users().messages().get().execute.side_effect = [
        {
            "id": "msg1",
            "snippet": "Snippet 1",
            "payload": {
                "headers": [
                    {"name": "Subject", "value": "Test Subject 1"},
                    {"name": "From", "value": "sender1@example.com"},
                    {"name": "Date", "value": "Mon, 13 Oct 2025 12:00:00 +0000"}
                ]
            }
        },
        {
            "id": "msg2",
            "snippet": "Snippet 2",
            "payload": {
                "headers": [
                    {"name": "Subject", "value": "Test Subject 2"},
                    {"name": "From", "value": "sender2@example.com"},
                    {"name": "Date", "value": "Tue, 14 Oct 2025 14:00:00 +0000"}
                ]
            }
        }
    ]

    return service


# ------------------------
# Tests
# ------------------------

def test_fetch_inbox_emails_success(fake_service):
    emails = fetch_inbox_emails(fake_service, max_results=2)
    assert len(emails) == 2

    assert emails[0]["id"] == "msg1"
    assert emails[0]["snippet"] == "Snippet 1"
    assert emails[0]["subject"] == "Test Subject 1"
    assert emails[0]["from"] == "sender1@example.com"
    assert emails[0]["received_at"] == "Mon, 13 Oct 2025 12:00:00 +0000"

    assert emails[1]["id"] == "msg2"
    assert emails[1]["subject"] == "Test Subject 2"
    assert emails[1]["from"] == "sender2@example.com"


def test_fetch_inbox_emails_empty_list():
    service = MagicMock()
    service.users().messages().list().execute.return_value = {}
    emails = fetch_inbox_emails(service)
    assert emails == []


def test_fetch_inbox_emails_partial_failure():
    service = MagicMock()
    service.users().messages().list().execute.return_value = {
        "messages": [{"id": "msg1"}, {"id": "msg2"}]
    }

    service.users().messages().get().execute.side_effect = [
        {
            "id": "msg1",
            "snippet": "Snippet 1",
            "payload": {"headers": [{"name": "Subject", "value": "S1"}]}
        },
        Exception("API failure")
    ]

    emails = fetch_inbox_emails(service, max_results=2)
    assert len(emails) == 1
    assert emails[0]["id"] == "msg1"
    assert emails[0]["subject"] == "S1"
