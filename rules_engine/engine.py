import json
import logging
import os
import sqlite3
from pathlib import Path
from db.rules_to_sql import rules_to_sql_query
from rules_engine.validator import load_and_validate_rules
from gmail.actions.mark_as_read import mark_as_read
from gmail.actions.mark_as_unread import mark_as_unread
from gmail.actions.move_message import move_message

USE_MOCK_ACTIONS = os.environ.get("USE_MOCK_ACTIONS", "true").lower() == "true"
if USE_MOCK_ACTIONS:
    from gmail.actions import mock_actions as actions_module
else:
    actions_module = None

logger = logging.getLogger(__name__)

ACTIONS_MAP = {
    "mark_as_read": getattr(actions_module, "mark_as_read", mark_as_read),
    "mark_as_unread": getattr(actions_module, "mark_as_unread", mark_as_unread),
    "move_message": getattr(actions_module, "move_message", move_message),
}

def execute_actions(email, actions):
    """Executes all actions for a matching email."""
    for action_str in actions:
        if ":" in action_str:
            action_name, folder = action_str.split(":", 1)
        else:
            action_name, folder = action_str, None

        action_func = ACTIONS_MAP.get(action_name)
        if not action_func:
            continue

        if folder:
            action_func(email["id"], folder)
        else:
            action_func(email["id"])

def execute_query(query, params, db_path="emails.db"):
    """Fetch emails matching the SQL query and execute actions."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute(query, params)
    emails = [dict(row) for row in cur.fetchall()]
    conn.close()
    return emails

def run_rules(rules_file=None):
    """Run all rules defined in the JSON file against stored emails."""
    if rules_file is None:
        rules_file = Path(__file__).parent / "rules.json"
    rules_config = load_and_validate_rules(rules_file)

    query, params = rules_to_sql_query(rules_config)
    emails = execute_query(query, params)
    for email in emails:
        execute_actions(email, rules_config.get("actions", []))

if __name__ == "__main__":
    run_rules()