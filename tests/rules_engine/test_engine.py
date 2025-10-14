import pytest
import sqlite3
from unittest import mock
from rules_engine import engine


@pytest.fixture
def mock_actions():
    """Mock all action functions."""
    with mock.patch.dict(engine.ACTIONS_MAP, {
        "mark_as_read": mock.Mock(),
        "mark_as_unread": mock.Mock(),
        "move_message": mock.Mock(),
    }) as mock_map:
        yield mock_map


# ------------------ TESTS FOR execute_actions ------------------

def test_execute_actions_calls_correct_action(mock_actions):
    email = {"id": "123"}
    actions = ["mark_as_read", "move_message:Inbox"]

    engine.execute_actions(email, actions)

    mock_actions["mark_as_read"].assert_called_once_with("123")
    mock_actions["move_message"].assert_called_once_with("123", "Inbox")


def test_execute_actions_skips_unknown_action(mock_actions):
    email = {"id": "999"}
    actions = ["unknown_action"]

    engine.execute_actions(email, actions)

    for action in mock_actions.values():
        action.assert_not_called()


# ------------------ TESTS FOR execute_query ------------------

def test_execute_query_returns_emails(tmp_path):
    db_file = tmp_path / "emails.db"
    conn = sqlite3.connect(db_file)
    conn.execute("CREATE TABLE emails (id TEXT, subject TEXT)")
    conn.execute("INSERT INTO emails VALUES ('1', 'test')")
    conn.commit()
    conn.close()

    query = "SELECT * FROM emails WHERE subject = ?"
    params = ["test"]

    result = engine.execute_query(query, params, db_path=db_file)
    assert result == [{"id": "1", "subject": "test"}]


def test_execute_query_with_no_results(tmp_path):
    db_file = tmp_path / "emails.db"
    conn = sqlite3.connect(db_file)
    conn.execute("CREATE TABLE emails (id TEXT, subject TEXT)")
    conn.commit()
    conn.close()

    result = engine.execute_query("SELECT * FROM emails", [], db_path=db_file)
    assert result == []


# ------------------ TESTS FOR run_rules ------------------

@mock.patch("rules_engine.engine.execute_actions")
@mock.patch("rules_engine.engine.execute_query")
@mock.patch("rules_engine.engine.rules_to_sql_query")
@mock.patch("rules_engine.engine.load_and_validate_rules")
def test_run_rules_executes_actions(
    mock_load_rules,
    mock_rules_to_sql,
    mock_execute_query,
    mock_execute_actions,
):
    mock_load_rules.return_value = {
        "rules_predicate": "all",
        "rules": [{"field": "subject", "predicate": "contains", "value": "test"}],
        "actions": ["mark_as_read"],
    }
    mock_rules_to_sql.return_value = ("SELECT * FROM emails;", [])
    mock_execute_query.return_value = [{"id": "1", "subject": "Test email"}]

    engine.run_rules("fake_rules.json")

    mock_load_rules.assert_called_once_with("fake_rules.json")
    mock_rules_to_sql.assert_called_once()
    mock_execute_query.assert_called_once()
    mock_execute_actions.assert_called_once_with(
        {"id": "1", "subject": "Test email"},
        ["mark_as_read"],
    )


@mock.patch("rules_engine.engine.load_and_validate_rules")
@mock.patch("rules_engine.engine.rules_to_sql_query")
@mock.patch("rules_engine.engine.execute_query")
@mock.patch("rules_engine.engine.execute_actions")
def test_run_rules_with_no_emails(
    mock_execute_actions,
    mock_execute_query,
    mock_rules_to_sql,
    mock_load_rules,
):
    mock_load_rules.return_value = {"rules": [], "actions": ["mark_as_read"]}
    mock_rules_to_sql.return_value = ("SELECT * FROM emails;", [])
    mock_execute_query.return_value = []

    engine.run_rules("fake_rules.json")

    mock_execute_actions.assert_not_called()
