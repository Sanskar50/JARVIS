import os.path
import base64
from email.message import EmailMessage

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
]

# Relative paths to auth files (assuming we are in tools/ directory)
TOKEN_PATH = os.path.join(os.path.dirname(__file__), "..", "token.json")
CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), "..", "credentials.json")


def get_gmail_service():
    """Helper to get an authorized Gmail API service instance."""
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, "w") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def gmail_read(max_results: int = 10):
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
            email_data.append(
                {"id": msg["id"], "subject": subject, "snippet": txt.get("snippet", "")}
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


def gmail_read_by_label(label_id: str, max_results: int = 10):
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
            email_data.append(
                {"id": msg["id"], "subject": subject, "snippet": txt.get("snippet", "")}
            )
        return email_data
    except HttpError as error:
        return f"An error occurred: {error}"
