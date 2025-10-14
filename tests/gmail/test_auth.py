import pytest
from gmail.auth import get_gmail_service, CREDENTIALS_FILE, SCOPES


def test_uses_existing_token(mock_gmail_dependencies):
    """Should use token.json if it exists and credentials are valid"""
    mocks = mock_gmail_dependencies

    mocks["mock_exists"].return_value = True
    mock_creds = mocks["mock_creds"]
    mock_creds.valid = True

    service = get_gmail_service()

    mocks["mock_credentials"].from_authorized_user_info.assert_called_once()
    mocks["mock_build"].assert_called_once_with("gmail", "v1", credentials=mock_creds)
    assert service == "mocked_gmail_service"


def test_refreshes_expired_token(mock_gmail_dependencies):
    """Should refresh credentials if expired and refresh token available"""
    mocks = mock_gmail_dependencies

    mocks["mock_exists"].return_value = True
    mock_creds = mocks["mock_creds"]
    mock_creds.valid = False
    mock_creds.expired = True
    mock_creds.refresh_token = "refresh"

    service = get_gmail_service()

    mock_creds.refresh.assert_called_once()
    mocks["mock_build"].assert_called_once_with("gmail", "v1", credentials=mock_creds)
    assert service == "mocked_gmail_service"


def test_runs_oauth_flow_when_no_valid_token(mock_gmail_dependencies):
    """Should run OAuth flow when no valid credentials exist"""
    mocks = mock_gmail_dependencies

    mocks["mock_exists"].return_value = False

    service = get_gmail_service()

    mocks["mock_flow"].from_client_secrets_file.assert_called_once_with(
        CREDENTIALS_FILE, SCOPES
    )
    mocks["mock_instance"].run_local_server.assert_called_once()
    mocks["mock_build"].assert_called_once_with(
        "gmail", "v1", credentials=mocks["mock_creds"]
    )
    assert service == "mocked_gmail_service"
