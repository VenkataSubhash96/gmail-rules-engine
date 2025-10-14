import pytest
from db.rules_to_sql import rules_to_sql_query

def test_contains_predicate():
    rules_data = {
        "rules_predicate": "all",
        "rules": [
            {"field": "Subject", "predicate": "contains", "value": "invoice"}
        ]
    }
    query, params = rules_to_sql_query(rules_data)
    assert query == "SELECT * FROM emails WHERE subject LIKE ?;"
    assert params == ["%invoice%"]

def test_does_not_contain_predicate():
    rules_data = {
        "rules_predicate": "all",
        "rules": [
            {"field": "Body", "predicate": "does_not_contain", "value": "promo"}
        ]
    }
    query, params = rules_to_sql_query(rules_data)
    assert "body NOT LIKE ?" in query
    assert params == ["%promo%"]

def test_equals_predicate():
    rules_data = {
        "rules": [{"field": "Sender", "predicate": "equals", "value": "test@example.com"}]
    }
    query, params = rules_to_sql_query(rules_data)
    assert query == "SELECT * FROM emails WHERE sender = ?;"
    assert params == ["test@example.com"]

def test_does_not_equal_predicate():
    rules_data = {
        "rules": [{"field": "Recipient", "predicate": "does_not_equal", "value": "no-reply@example.com"}]
    }
    query, params = rules_to_sql_query(rules_data)
    assert query == "SELECT * FROM emails WHERE recipient != ?;"
    assert params == ["no-reply@example.com"]

def test_multiple_conditions_with_any_predicate():
    rules_data = {
        "rules_predicate": "any",
        "rules": [
            {"field": "Subject", "predicate": "contains", "value": "invoice"},
            {"field": "Sender", "predicate": "equals", "value": "accounts@example.com"}
        ]
    }
    query, params = rules_to_sql_query(rules_data)
    assert " OR " in query
    assert len(params) == 2
    assert params == ["%invoice%", "accounts@example.com"]

def test_received_less_than_days():
    rules_data = {
        "rules": [{"field": "received_at", "predicate": "less_than", "value": "10 days"}]
    }
    query, params = rules_to_sql_query(rules_data)
    assert "received_at >= datetime('now', ?)" in query
    assert params == ["-10 days"]

def test_received_greater_than_months():
    rules_data = {
        "rules": [{"field": "received_at", "predicate": "greater_than", "value": "2 months"}]
    }
    query, params = rules_to_sql_query(rules_data)
    assert "received_at <= datetime('now', ?)" in query
    assert params == ["-60 days"]

def test_unknown_string_predicate_raises():
    rules_data = {
        "rules": [{"field": "subject", "predicate": "starts_with", "value": "Re:"}]
    }
    with pytest.raises(ValueError, match="Unknown string predicate"):
        rules_to_sql_query(rules_data)

def test_unknown_date_predicate_raises():
    rules_data = {
        "rules": [{"field": "received_at", "predicate": "between", "value": "5 days"}]
    }
    with pytest.raises(ValueError, match="Unknown date predicate"):
        rules_to_sql_query(rules_data)

def test_unknown_field_raises():
    rules_data = {
        "rules": [{"field": "priority", "predicate": "equals", "value": "high"}]
    }
    with pytest.raises(ValueError, match="Unknown field"):
        rules_to_sql_query(rules_data)
