import pytest
from unittest import mock
from gmail.actions.mark_as_unread import mark_as_unread


@pytest.mark.usefixtures("mock_gmail_dependencies")
@mock.patch("gmail.actions.mark_as_unread.sqlite3.connect")
@mock.patch("gmail.actions.mark_as_unread.api_mark_as_unread")
def test_mark_as_unread_updates_db_and_calls_gmail_api(
    mock_api_mark_as_unread,
    mock_connect,
    mock_gmail_dependencies
):
    """
    Test that mark_as_unread:
      - Uses get_gmail_service() (mocked via mock_gmail_dependencies)
      - Calls Gmail API
      - Updates DB with is_read = 0
    """

    fake_service = "mocked_gmail_service"
    message_id = "xyz789"

    mock_conn = mock.Mock()
    mock_cursor = mock.Mock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    mark_as_unread(message_id)

    mock_api_mark_as_unread.assert_called_once_with(fake_service, message_id)

    mock_cursor.execute.assert_called_once_with(
        "UPDATE emails SET is_read = 0 WHERE id = ?", (message_id,)
    )
    mock_conn.commit.assert_called_once()
    mock_conn.close.assert_called_once()

@pytest.mark.usefixtures("mock_gmail_dependencies")
@mock.patch("gmail.actions.mark_as_unread.api_mark_as_unread")
@mock.patch("gmail.actions.mark_as_unread.sqlite3.connect")
def test_mark_as_unread_handles_gmail_api_failure(mock_connect, mock_api_mark_as_unread, mock_gmail_dependencies):
    """
    Negative Test:
    Ensures mark_as_unread:
      - Raises exception if Gmail API fails
      - Does not commit changes to DB
    """
    message_id = "xyz789"

    mock_api_mark_as_unread.side_effect = Exception("Gmail API failure")

    mock_conn = mock.Mock()
    mock_cursor = mock.Mock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    with pytest.raises(Exception, match="Gmail API failure"):
        mark_as_unread(message_id)

    mock_cursor.execute.assert_not_called()
    mock_conn.commit.assert_not_called()
    mock_conn.close.assert_not_called()
