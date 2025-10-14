import pytest
from unittest import mock
from pathlib import Path
import json

@pytest.fixture
def mock_gmail_dependencies():
    """Fixture that mocks all Gmail auth dependencies."""

    credentials_path = Path(__file__).resolve().parent.parent / "gmail" / "credentials.json.example"
    with open(credentials_path, "r") as f:
        example_credentials = json.load(f)

    with (
        mock.patch("gmail.auth.os.path.exists") as mock_exists,
        mock.patch("gmail.auth.Credentials") as mock_credentials,
        mock.patch("gmail.auth.build") as mock_build,
        mock.patch("gmail.auth.InstalledAppFlow") as mock_flow,
        mock.patch("gmail.actions.mark_as_read.api_mark_as_read") as mock_api_mark_as_read,
        mock.patch("gmail.actions.mark_as_unread.api_mark_as_unread") as mock_api_mark_as_unread,
        mock.patch("gmail.actions.move_message.api_move_message") as mock_api_move_message,
    ):
        mock_exists.return_value = False
        mock_creds = mock.Mock()
        mock_creds.valid = False
        mock_creds.expired = False
        mock_creds.to_json.return_value = json.dumps(example_credentials)
        mock_credentials.from_authorized_user_info.return_value = mock_creds

        mock_instance = mock.Mock()
        mock_instance.run_local_server.return_value = mock_creds
        mock_flow.from_client_secrets_file.return_value = mock_instance

        mock_api_mark_as_read.return_value = None
        mock_api_mark_as_unread.return_value = None
        mock_api_move_message.return_value = None

        mock_build.return_value = "mocked_gmail_service"

        yield {
            "mock_exists": mock_exists,
            "mock_credentials": mock_credentials,
            "mock_build": mock_build,
            "mock_flow": mock_flow,
            "mock_creds": mock_creds,
            "mock_instance": mock_instance,
            "mock_api_mark_as_read": mock_api_mark_as_read,
            "mock_api_mark_as_unread": mock_api_mark_as_unread,
            "mock_api_move_message": mock_api_move_message,
        }
