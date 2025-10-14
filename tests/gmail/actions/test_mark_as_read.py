import pytest
from unittest import mock
from gmail.actions.mark_as_read import mark_as_read


@pytest.mark.usefixtures("mock_gmail_dependencies")
@mock.patch("gmail.actions.mark_as_read.sqlite3.connect")
@mock.patch("gmail.actions.mark_as_read.api_mark_as_read")
def test_mark_as_read_updates_db_and_calls_gmail_api(mock_api_mark_as_read, mock_connect, mock_gmail_dependencies):
    """
    Test that mark_as_read:
      - Uses get_gmail_service() (mocked via mock_gmail_dependencies)
      - Calls Gmail API
      - Updates DB with is_read = 1
    """

    fake_service = "mocked_gmail_service"
    message_id = "abc123"

    mock_conn = mock.Mock()
    mock_cursor = mock.Mock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    mark_as_read(message_id)

    mock_api_mark_as_read.assert_called_once_with(fake_service, message_id)

    mock_cursor.execute.assert_called_once_with(
        "UPDATE emails SET is_read = 1 WHERE id = ?", (message_id,)
    )
    mock_conn.commit.assert_called_once()
    mock_conn.close.assert_called_once()

@pytest.mark.usefixtures("mock_gmail_dependencies")
@mock.patch("gmail.actions.mark_as_read.api_mark_as_read")
@mock.patch("gmail.actions.mark_as_read.sqlite3.connect")
def test_mark_as_read_handles_gmail_api_failure(mock_connect, mock_api_mark_as_read, mock_gmail_dependencies):
    """
    Negative Test:
    Ensures mark_as_read:
      - Raises exception if Gmail API fails
      - Does not commit changes to DB
    """
    message_id = "abc123"

    mock_api_mark_as_read.side_effect = Exception("Gmail API failure")

    mock_conn = mock.Mock()
    mock_cursor = mock.Mock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    with pytest.raises(Exception, match="Gmail API failure"):
        mark_as_read(message_id)

    mock_cursor.execute.assert_not_called()
    mock_conn.commit.assert_not_called()
    mock_conn.close.assert_not_called()
