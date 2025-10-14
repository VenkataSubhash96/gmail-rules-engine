import os
import json
import logging
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]
CREDENTIALS_FILE = "gmail/credentials.json"
TOKEN_FILE = "token.json"

logger = logging.getLogger(__name__)

def get_gmail_service():
    creds = None

    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            creds_data = json.load(f)
            creds = Credentials.from_authorized_user_info(creds_data, SCOPES)

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
        creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())
        logger.info(f"Saved new credentials to {TOKEN_FILE}")

    return build("gmail", "v1", credentials=creds)
