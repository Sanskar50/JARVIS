import base64
import re
from email.message import EmailMessage
from config import config
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
]


def get_gmail_service():
    """Helper to get an authorized Gmail API service instance."""
    token = config.GMAIL_TOKEN if config.GMAIL_TOKEN else None
    refresh_token = config.GMAIL_REFRESH_TOKEN if config.GMAIL_REFRESH_TOKEN else None
    client_id = config.GMAIL_CLIENT_ID if config.GMAIL_CLIENT_ID else None
    client_secret = config.GMAIL_CLIENT_SECRET if config.GMAIL_CLIENT_SECRET else None

    creds = Credentials(
        token=token,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=SCOPES,
    )

    if not creds.valid and creds.refresh_token:
        try:
            creds.refresh(Request())
        except Exception as e:
            print(f"Warning: Token refresh failed: {e}")

    return build("gmail", "v1", credentials=creds)


def gmail_read(max_results: int = 20):
    """
    List the user's most recent emails.
    Returns: A list of dicts with subject and snippet.
    """
    try:
        service = get_gmail_service()
        results = (
            service.users()
            .messages()
            .list(userId="me", maxResults=max_results)
            .execute()
        )
        messages = results.get("messages", [])

        email_data = []
        for msg in messages:
            txt = service.users().messages().get(userId="me", id=msg["id"]).execute()
            payload = txt.get("payload", {})
            headers = payload.get("headers", [])
            subject = next(
                (h["value"] for h in headers if h["name"].lower() == "subject"),
                "No Subject",
            )
            sender = next(
                (h["value"] for h in headers if h["name"].lower() == "from"),
                "Unknown",
            )
            email_data.append(
                {
                    "id": msg["id"],
                    "subject": subject,
                    "sender": sender,
                    "snippet": txt.get("snippet", ""),
                }
            )
        return email_data
    except HttpError as error:
        return f"An error occurred: {error}"


def gmail_send(to: str, subject: str, body: str):
    """
    Send an email message.
    """
    try:
        service = get_gmail_service()
        message = EmailMessage()
        message.set_content(body)
        message["To"] = to
        message["From"] = "me"
        message["Subject"] = subject

        # encoded message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {"raw": encoded_message}

        send_message = (
            service.users().messages().send(userId="me", body=create_message).execute()
        )
        return f'Message Id: {send_message["id"]} sent successfully.'
    except HttpError as error:
        return f"An error occurred: {error}"


def gmail_draft(to: str, subject: str, body: str):
    """
    Create a draft email.
    """
    try:
        service = get_gmail_service()
        message = EmailMessage()
        message.set_content(body)
        message["To"] = to
        message["From"] = "me"
        message["Subject"] = subject

        # encoded message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_draft = {"message": {"raw": encoded_message}}

        draft = (
            service.users().drafts().create(userId="me", body=create_draft).execute()
        )
        return f'Draft Id: {draft["id"]} created successfully.'
    except HttpError as error:
        return f"An error occurred: {error}"


def gmail_read_by_label(label_id: str, max_results: int = 20):
    """
    List the user's emails from a specific label (e.g., 'IMPORTANT', 'SENT', 'INBOX').
    Returns: A list of dicts with subject and snippet.
    """
    try:
        service = get_gmail_service()
        results = (
            service.users()
            .messages()
            .list(userId="me", labelIds=[label_id], maxResults=max_results)
            .execute()
        )
        messages = results.get("messages", [])

        email_data = []
        for msg in messages:
            txt = service.users().messages().get(userId="me", id=msg["id"]).execute()
            payload = txt.get("payload", {})
            headers = payload.get("headers", [])
            subject = next(
                (h["value"] for h in headers if h["name"].lower() == "subject"),
                "No Subject",
            )
            sender = next(
                (h["value"] for h in headers if h["name"].lower() == "from"),
                "Unknown",
            )
            email_data.append(
                {
                    "id": msg["id"],
                    "subject": subject,
                    "sender": sender,
                    "snippet": txt.get("snippet", ""),
                }
            )
        return email_data
    except HttpError as error:
        return f"An error occurred: {error}"


def gmail_get_email_addresses(max_results: int = 20):
    """
    Extract unique email addresses from the most recent emails.
    """
    try:
        service = get_gmail_service()
        results = (
            service.users()
            .messages()
            .list(userId="me", maxResults=max_results)
            .execute()
        )
        messages = results.get("messages", [])

        email_regex = r"[\w\.-]+@[\w\.-]+\.\w+"
        addresses = set()
        for msg in messages:
            txt = (
                service.users()
                .messages()
                .get(userId="me", id=msg["id"], format="metadata")
                .execute()
            )
            headers = txt.get("payload", {}).get("headers", [])
            sender = next(
                (h["value"] for h in headers if h["name"].lower() == "from"),
                "",
            )
            found = re.findall(email_regex, sender)
            for addr in found:
                addresses.add(addr)

        return list(addresses)
    except HttpError as error:
        return f"An error occurred: {error}"
