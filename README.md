# Gmail Rules Engine

A Python-based Gmail Rules Engine that fetches emails from Gmail (or sample/mock data), applies configurable rules, and executes actions such as marking emails as read/unread or moving them to folders.  

This project is designed to be **secure, modular, and reviewer-friendly**, allowing testing without exposing sensitive credentials.  

---

## Features

- Fetch emails using Gmail API (OAuth2) or load from a mock dataset.
- Apply flexible rules defined in a JSON file (`rules.json`) using predicates like `contains`, `equals`, `less_than`, `greater_than`.
- Execute multiple actions for matching emails:
  - Mark as read
  - Mark as unread
  - Move to folder
- Stores emails in a **SQLite database** for efficient querying.
- Designed with **future scalability** in mind (e.g., cron jobs for automated updates).

---

## Table of Contents

1. [Installation](#installation)  
2. [Usage](#usage)  
3. [Project Structure](#project-structure)  
4. [Rules Configuration](#rules-configuration)  
5. [Design Decisions & Thought Process](#design-decisions--thought-process)  
6. [Future Improvements](#future-improvements)
7. [Notes for Reviewers](#notes-for-reviewers)

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/VenkataSubhash96/gmail-rules-engine.git
cd gmail-rules-engine
```

### 2. Create a Python virtual environment

```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate     # On Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

## Usage

### 1. Create the database

```bash
python db/create_emails_table.py
```

### 2. Populate the database

You have two options:

#### Option A: Using mock/sample emails (safe for reviewers)

```bash
python -m db.populate_sample_emails
```
* Populates the database (emails.db) with 100 sample emails.
* Does not require Gmail credentials.

#### Option B: Using Gmail API (requires your own credentials)

1. Set up a Google Cloud Project and enable Gmail API. The guide can be found here - https://developers.google.com/identity/protocols/oauth2
2. Download credentials.json and store it under the `gmail` folder
3. Run
```bash
python -m db.populate_emails
```
* The script will fetch emails from your real Gmail account and store them in emails.db.
* OAuth2 will prompt for account authorization. Once authorized, you don't need to authorize for the next one hour. I implemented a token mechanism to implement this. 

### 3. Run the rules engine (this is the main program)

```bash
python -m rules_engine.engine
```
* Reads rules.json, queries emails, applies rules, and executes actions.
* By default, all actions are run in mock mode, meaning they do not call the real Gmail API. This allows reviewers to safely test the engine on sample/mock emails.

#### Dry-run / Mock Mode
* Controlled via the environment variable `USE_MOCK_ACTIONS`.
* Default behavior:
```bash
export USE_MOCK_ACTIONS=true  # macOS/Linux
set USE_MOCK_ACTIONS=true     # Windows
```
* This makes the engine use mock action functions that just print the action instead of modifying real emails.

To run against your own Gmail account:
```bash
export USE_MOCK_ACTIONS=false
python -m rules_engine.engine
```
* This will make real API calls to your Gmail accout like marking an email as read etc. 

### 4. Running the tests

```bash
pytest -v
```

## Project Structure

```bash
gmail-rules-engine/
│
├── db/
    ├── create_emails_table.py     # Creates a new table called emails
│   ├── populate_emails.py         # Fetch emails from Gmail API
│   ├── populate_sample_emails.py  # Generate 100 mock emails
│   └── rules_to_sql.py            # Generate SQL query from rules JSON
│
├── gmail/
    ├── auth.py                    # Gmail Authentication API client
│   ├── client.py                  # Gmail API client
│   ├── utils.py                   # Utility functions for emails
    ├── fetcher.py                 # Fetches emails from your inbox using the Gmail API
    ├── credentials.json.example   # Example of credentials.json file
│   └── actions/                   # Action functions (mark_as_read, mark_as_unread, and move_message)
│
├── rules_engine/
│   ├── engine.py                  # Main rules engine
│   ├── validator.py               # Validate rules.json
│   └── rules.json                 # Configurable rules
│
├── tests/                         # Tests
├── requirements.txt
└── README.md
```

## Rules Configuration

`rules.json` example
```bash
{
  "rules_predicate": "all",
  "rules": [
    {
      "field": "received_at",
      "predicate": "greater_than",
      "value": "5 days"
    },
    {
      "field": "subject",
      "predicate": "contains",
      "value": "Invoice"
    }
  ],
  "actions": [
    "mark_as_read",
    "move_message:STARRED"
  ]
}
```
* `rules_predicate`: `"all"` or `"any"` to combine conditions.
* Supported fields: `sender`, `recipient`, `subject`, `body`, `snippet`, `received_at`
* Supported predicates: `contains`, `does_not_contain`, `equals`, `does_not_equal`, `less_than`, `greater_than`
* Supported actions: `mark_as_read`, `mark_as_unread`, `move_message:#{folder_name}`

## Design Decisions & Thought Process

* Secure by default: No personal Gmail credentials are stored in the repo. Sample/mock emails allow reviewers to test safely.
* ISO UTC timestamps: All received_at values are normalized to UTC to simplify date-based rules.
* SQL-based filtering: Efficient queries using SQLite to handle large email datasets.
* Modular structure: Actions, evaluator, engine, and DB utilities are separate for maintainability.
* Extensibility: Easy to add new rules or actions without changing core engine logic.
* Testing mindset: Designed to work with mock datasets to allow unit tests and reviewer validation.

## Future Improvements

1. Automated database updates:
  * Set up a cron job to fetch new emails periodically.
  * Ensures the database is always fresh without manual intervention.

## Notes for Reviewers

* The database file `(emails.db)` is not included in the repo.
* Use `populate_sample_emails.py` to generate test data.
* Use your own Gmail API credentials to fetch real emails.
* All queries and rules work on UTC ISO timestamps, so date-based rules are consistent.