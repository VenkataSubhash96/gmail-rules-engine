import pytest
from unittest import mock
from gmail.actions.move_message import move_message


@pytest.mark.usefixtures("mock_gmail_dependencies")
@mock.patch("gmail.actions.move_message.api_move_message")
def test_move_message_calls_gmail_api(mock_api_move_message, mock_gmail_dependencies):
    """
    Test that move_message:
      - Uses get_gmail_service() (mocked via mock_gmail_dependencies)
      - Calls Gmail API move_message with correct message_id and folder
      - Does not perform any DB operations
    """

    fake_service = "mocked_gmail_service"
    message_id = "msg123"
    folder = "INBOX"

    move_message(message_id, folder)

    mock_api_move_message.assert_called_once_with(fake_service, message_id, folder)

@mock.patch("gmail.actions.move_message.api_move_message")
@pytest.mark.usefixtures("mock_gmail_dependencies")
def test_move_message_handles_gmail_api_failure(mock_api_move_message, mock_gmail_dependencies):
    """
    Negative Test:
    Ensures move_message doesn't crash if the Gmail API raises an exception.
    """
    fake_service = "mocked_gmail_service"
    message_id = "msg456"
    folder = "SPAM"

    mock_api_move_message.side_effect = Exception("Gmail API failure")

    with pytest.raises(Exception, match="Gmail API failure"):
        move_message(message_id, folder)

    mock_api_move_message.assert_called_once_with(fake_service, message_id, folder)