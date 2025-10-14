import json

RULES_PREDICATE_VALUES = {"all", "any"}
STRING_FIELD_PREDICATES = {"contains", "does_not_contain", "equals", "does_not_equal"}
DATE_FIELD_PREDICATES = {"less_than", "greater_than"}
ALLOWED_ACTIONS = {"mark_as_read", "mark_as_unread", "move_message"}
SYSTEM_ALLOWED_FOLDERS = {"INBOX", "SPAM", "TRASH", "IMPORTANT", "DRAFT", "STARRED"}
CUSTOM_ALLOWED_FOLDERS = {}
ALLOWED_FOLDERS = SYSTEM_ALLOWED_FOLDERS.union(CUSTOM_ALLOWED_FOLDERS)
FIELD_TYPES = {
    "sender": "string",
    "recipient": "string",
    "subject": "string",
    "body": "string",
    "snippet": "string",
    "received_at": "date",
}

class RuleValidationError(Exception):
    pass

def validate_rule(rule):
    if "field" not in rule or "predicate" not in rule or "value" not in rule:
        raise RuleValidationError(f"Rule missing required keys: {rule}")

    field = rule["field"].lower()
    predicate = rule["predicate"]

    if field not in FIELD_TYPES:
        raise RuleValidationError(f"Unknown field: {field}")

    field_type = FIELD_TYPES[field]
    if field_type == "string" and predicate not in STRING_FIELD_PREDICATES:
        raise RuleValidationError(f"Invalid predicate '{predicate}' for string field '{field}'")
    if field_type == "date" and predicate not in DATE_FIELD_PREDICATES:
        raise RuleValidationError(f"Invalid predicate '{predicate}' for date field '{field}'")

def validate_actions(actions):
    for action in actions:
        if ":" in action:
            left, right = action.split(":", 1)
            left = left.strip()
            right = right.strip()
            if left not in ALLOWED_ACTIONS:
                raise RuleValidationError(f"Invalid action: {left}")
            if right not in ALLOWED_FOLDERS:
                raise RuleValidationError(f"Invalid folder: {right}")
        else:
            if action not in ALLOWED_ACTIONS:
                raise RuleValidationError(f"Invalid action: {action}")

def validate_rules_json(rules_json):
    if "rules_predicate" not in rules_json or "rules" not in rules_json or "actions" not in rules_json:
        raise RuleValidationError("Missing top-level keys: 'rules_predicate', 'rules', or 'actions'")

    if rules_json["rules_predicate"] not in RULES_PREDICATE_VALUES:
        raise RuleValidationError(f"Invalid rules_predicate: {rules_json['rules_predicate']}")

    for rule in rules_json["rules"]:
        validate_rule(rule)

    validate_actions(rules_json["actions"])

    return True

def load_and_validate_rules(file_path):
    with open(file_path, "r") as f:
        rules_json = json.load(f)
    validate_rules_json(rules_json)
    return rules_json
