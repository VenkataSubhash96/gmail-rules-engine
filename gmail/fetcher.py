import logging
import base64
from gmail.utils import get_header

logger = logging.getLogger(__name__)

def decode_base64(data):
    """Decode Base64 URL-encoded data from Gmail."""
    if not data:
        return ""
    return base64.urlsafe_b64decode(data.encode("ASCII")).decode("utf-8")

def get_email_body(payload):
    """
    Extract the plain text body from a Gmail message payload.
    Handles simple and multipart messages.
    """
    body = ""
    mime_type = payload.get("mimeType", "")

    if mime_type == "text/plain" or mime_type == "text/html":
        body = decode_base64(payload.get("body", {}).get("data"))
    elif mime_type.startswith("multipart"):
        for part in payload.get("parts", []):
            if part.get("mimeType") == "text/plain":
                body = decode_base64(part.get("body", {}).get("data"))
                break
    return body

def fetch_inbox_emails(service, max_results=1000, user_id="me"):
    email_list = []
    try:
        results = service.users().messages().list(userId=user_id, maxResults=max_results).execute()
        messages = results.get("messages", [])
    except Exception as e:
        logger.error(f"Failed to fetch message list: {e}")
        return email_list

    for msg in messages:
        try:
            msg_data = service.users().messages().get(userId=user_id, id=msg["id"]).execute()
            headers = msg_data.get("payload", {}).get("headers", [])
            body = get_email_body(msg_data.get("payload", {}))
            label_ids = msg_data.get("labelIds", [])
            email_list.append({
                "id": msg_data.get("id"),
                "snippet": msg_data.get("snippet"),
                "subject": get_header(headers, "Subject"),
                "from": get_header(headers, "From"),
                "to": get_header(headers, "To"),
                "received_at": get_header(headers, "Date"),
                "body": body,
                "is_read": False if "UNREAD" in label_ids else True,
                "is_starred": True if "STARRED" in label_ids else False,
                "inbox_type": (
                    "INBOX" if "INBOX" in label_ids else
                    "SENT" if "SENT" in label_ids else
                    "SPAM" if "SPAM" in label_ids else
                    "OTHER"
                )
            })
        except Exception as e:
            logger.error(f"Failed to fetch message {msg['id']}: {e}")
            continue

    logger.info(f"Fetched {len(email_list)} emails")
    return email_list
