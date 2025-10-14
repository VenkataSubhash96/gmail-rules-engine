import pytest
import json
from unittest.mock import mock_open, patch
from rules_engine.validator import (
    validate_rule,
    validate_actions,
    validate_rules_json,
    load_and_validate_rules,
    RuleValidationError,
)

DB_FILE = "test_emails.db"

@pytest.fixture
def valid_rules_file(tmp_path):
    """Create a valid rules JSON file for testing."""
    data = {
        "rules_predicate": "all",
        "rules": [
            {"field": "Sender", "predicate": "contains", "value": "example.com"},
            {"field": "Received_At", "predicate": "less_than", "value": "2025-01-01"},
        ],
        "actions": ["mark_as_read", "move_message:INBOX"]
    }

    file_path = tmp_path / "valid_rules.json"
    with open(file_path, "w") as f:
        json.dump(data, f)
    return file_path

@pytest.fixture
def invalid_rules_file(tmp_path):
    """Create an invalid rules JSON file (invalid field)."""
    data = {
        "rules_predicate": "all",
        "rules": [
            {"field": "InvalidField", "predicate": "contains", "value": "test"},
        ],
        "actions": ["mark_as_read"]
    }

    file_path = tmp_path / "invalid_rules.json"
    with open(file_path, "w") as f:
        json.dump(data, f)
    return file_path

@pytest.fixture
def invalid_action_file(tmp_path):
    """Create an invalid rules JSON file (invalid action)."""
    data = {
        "rules_predicate": "all",
        "rules": [
            {"field": "Subject", "predicate": "contains", "value": "invoice"},
        ],
        "actions": ["move_message:UNKNOWN_FOLDER"]
    }

    file_path = tmp_path / "invalid_action.json"
    with open(file_path, "w") as f:
        json.dump(data, f)
    return file_path

# ------------------------
# validate_rule tests
# ------------------------

def test_validate_rule_valid_string_predicate():
    rule = {"field": "Subject", "predicate": "contains", "value": "Offer"}
    assert validate_rule(rule) is None


def test_validate_rule_valid_date_predicate():
    rule = {"field": "Received_At", "predicate": "less_than", "value": "10 days"}
    assert validate_rule(rule) is None


def test_validate_rule_missing_keys():
    rule = {"field": "Subject", "predicate": "contains"}
    with pytest.raises(RuleValidationError, match="missing required keys"):
        validate_rule(rule)


def test_validate_rule_invalid_field():
    rule = {"field": "InvalidField", "predicate": "contains", "value": "test"}
    with pytest.raises(RuleValidationError, match="Unknown field"):
        validate_rule(rule)


def test_validate_rule_invalid_string_predicate():
    rule = {"field": "Subject", "predicate": "less_than", "value": "test"}
    with pytest.raises(RuleValidationError, match="Invalid predicate 'less_than' for string field 'subject'"):
        validate_rule(rule)


def test_validate_rule_invalid_date_predicate():
    rule = {"field": "Received_At", "predicate": "contains", "value": "test"}
    with pytest.raises(RuleValidationError, match="Invalid predicate 'contains' for date field 'received_at'"):
        validate_rule(rule)

# ------------------------
# validate_actions tests
# ------------------------

def test_validate_actions_valid_actions():
    actions = ["mark_as_read", "mark_as_unread", "move_message:INBOX"]
    assert validate_actions(actions) is None


def test_validate_actions_invalid_action_name():
    actions = ["delete_message"]
    with pytest.raises(RuleValidationError, match="Invalid action: delete_message"):
        validate_actions(actions)


def test_validate_actions_invalid_folder_name():
    actions = ["move_message:INVALID_FOLDER"]
    with pytest.raises(RuleValidationError, match="Invalid folder: INVALID_FOLDER"):
        validate_actions(actions)


def test_validate_actions_with_extra_whitespace():
    actions = ["move_message:  SPAM  "]
    assert validate_actions(actions) is None

# ------------------------
# validate_rules_json tests
# ------------------------

def test_validate_rules_json_valid_structure():
    rules_json = {
        "rules_predicate": "all",
        "rules": [
            {"field": "Sender", "predicate": "contains", "value": "example.com"},
            {"field": "Subject", "predicate": "does_not_contain", "value": "spam"},
        ],
        "actions": ["mark_as_read", "move_message:INBOX"],
    }

    assert validate_rules_json(rules_json) is True


def test_validate_rules_json_missing_top_level_keys():
    rules_json = {
        "rules_predicate": "all",
        "rules": [],
    }
    with pytest.raises(RuleValidationError, match="Missing top-level keys"):
        validate_rules_json(rules_json)


def test_validate_rules_json_invalid_predicate_value():
    rules_json = {
        "rules_predicate": "invalid",
        "rules": [],
        "actions": [],
    }
    with pytest.raises(RuleValidationError, match="Invalid rules_predicate"):
        validate_rules_json(rules_json)


def test_validate_rules_json_invalid_rule_inside():
    rules_json = {
        "rules_predicate": "all",
        "rules": [{"field": "Subject", "predicate": "less_than", "value": "test"}],
        "actions": ["mark_as_read"],
    }
    with pytest.raises(RuleValidationError, match="Invalid predicate 'less_than' for string field 'subject'"):
        validate_rules_json(rules_json)

# ------------------------
# load_and_validate_rules tests
# ------------------------

def test_load_and_validate_rules_reads_file_and_validates():
    mock_data = json.dumps({
        "rules_predicate": "all",
        "rules": [{"field": "Sender", "predicate": "contains", "value": "example"}],
        "actions": ["mark_as_read"]
    })

    with patch("builtins.open", mock_open(read_data=mock_data)):
        with patch("rules_engine.validator.validate_rules_json", return_value=True) as mock_validate:
            result = load_and_validate_rules("rules.json")
            mock_validate.assert_called_once()
            assert result == json.loads(mock_data)


def test_load_and_validate_rules_invalid_file_json():
    with patch("builtins.open", mock_open(read_data="invalid_json")):
        with pytest.raises(json.JSONDecodeError):
            load_and_validate_rules("rules.json")

# ------------------------
# Integration tests
# ------------------------

def test_load_and_validate_rules_success(valid_rules_file):
    result = load_and_validate_rules(valid_rules_file)

    assert isinstance(result, dict)
    assert result["rules_predicate"] == "all"
    assert len(result["rules"]) == 2
    assert result["actions"] == ["mark_as_read", "move_message:INBOX"]

def test_load_and_validate_rules_invalid_action(invalid_action_file):
    with pytest.raises(RuleValidationError) as exc_info:
        load_and_validate_rules(invalid_action_file)
    assert "Invalid folder" in str(exc_info.value)

def test_load_and_validate_rules_invalid_action(invalid_action_file):
    with pytest.raises(RuleValidationError) as exc_info:
        load_and_validate_rules(invalid_action_file)
    assert "Invalid folder" in str(exc_info.value)

def test_missing_top_level_keys(tmp_path):
    bad_data = {
        "rules": [
            {"field": "Subject", "predicate": "contains", "value": "test"}
        ]
    }
    file_path = tmp_path / "missing_keys.json"
    with open(file_path, "w") as f:
        json.dump(bad_data, f)

    with pytest.raises(RuleValidationError) as exc_info:
        load_and_validate_rules(file_path)
    assert "Missing top-level keys" in str(exc_info.value)
