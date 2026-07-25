import base64
import re
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from config import config
from sources.template import SUBJECT, BODY
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.exceptions import RefreshError

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
]


def get_gmail_service():
    """Helper to get an authorized Gmail API service instance."""
    refresh_token = config.GMAIL_REFRESH_TOKEN if config.GMAIL_REFRESH_TOKEN else None
    client_id = config.GMAIL_CLIENT_ID if config.GMAIL_CLIENT_ID else None
    client_secret = config.GMAIL_CLIENT_SECRET if config.GMAIL_CLIENT_SECRET else None

    creds = Credentials(
        token=None,
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
    logger.info(f"gmail_read called with: max_results={max_results}")
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
        logger.info(f"gmail_read returned {len(email_data)} emails")
        return email_data
    except HttpError as error:
        logger.error(f"gmail_read error: {error}")
        return f"An error occurred: {error}"
    except RefreshError as error:
        logger.error(f"gmail_read RefreshError: {error}")
        return "Gmail Authentication Error: Your token has expired or been revoked. Please re-authenticate."


def gmail_send(to: str, subject: str, body: str):
    """
    Send an email message.
    """
    logger.info(f"gmail_send called with: to='{to}', subject='{subject}'")
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
        result = f'Message Id: {send_message["id"]} sent successfully.'
        logger.info(f"gmail_send result: {result}")
        return result
    except HttpError as error:
        logger.error(f"gmail_send error: {error}")
        return f"An error occurred: {error}"
    except RefreshError as error:
        logger.error(f"gmail_send RefreshError: {error}")
        return "Gmail Authentication Error: Your token has expired or been revoked. Please re-authenticate."


def gmail_send_with_resume(to: str, company_name: str, first_name: str):
    """
    Send an email with the resume attached using the predefined template.
    """
    logger.info(f"gmail_send_with_resume called with: to='{to}', company_name='{company_name}', first_name='{first_name}'")
    try:
        service = get_gmail_service()
        send_as_results = (
            service.users().settings().sendAs().list(userId="me").execute()
        )
        send_as_info = next(
            (
                info
                for info in send_as_results.get("sendAs", [])
                if info.get("isDefault")
            ),
            send_as_results.get("sendAs", [{}])[0],
        )
        signature = send_as_info.get("signature", "")

        message = MIMEMultipart()
        message["To"] = to
        message["From"] = "me"
        message["Subject"] = SUBJECT.format(
            company_name=company_name, first_name=first_name
        )

        # Combine body and signature
        formatted_body = BODY.format(first_name=first_name)
        if signature:
            if "<" in signature or "&" in signature:  # Simple check for HTML
                html_body = formatted_body.replace("\n", "<br>")
                full_body = f"<div>{html_body}</div><br>{signature}"
                message.attach(MIMEText(full_body, "html"))
            else:
                full_body = f"{formatted_body}\n\n{signature}"
                message.attach(MIMEText(full_body, "plain"))
        else:
            message.attach(MIMEText(formatted_body, "plain"))

        # Attach the resume
        file_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "sources",
            "Sanskar_Suri_Resume.pdf",
        )
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                part = MIMEApplication(f.read(), Name="Sanskar_Suri_Resume.pdf")
            part["Content-Disposition"] = (
                'attachment; filename="Sanskar_Suri_Resume.pdf"'
            )
            message.attach(part)
        else:
            return f"Error: Resume file not found at {file_path}."

        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {"raw": encoded_message}

        send_message = (
            service.users().messages().send(userId="me", body=create_message).execute()
        )
        result = f'Message Id: {send_message["id"]} sent successfully with resume.'
        logger.info(f"gmail_send_with_resume result: {result}")
        return result
    except HttpError as error:
        logger.error(f"gmail_send_with_resume error: {error}")
        return f"An error occurred: {error}"
    except RefreshError as error:
        logger.error(f"gmail_send_with_resume RefreshError: {error}")
        return "Gmail Authentication Error: Your token has expired or been revoked. Please re-authenticate."


def gmail_draft(to: str, subject: str, body: str):
    """
    Create a draft email.
    """
    logger.info(f"gmail_draft called with: to='{to}', subject='{subject}'")
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
        result = f'Draft Id: {draft["id"]} created successfully.'
        logger.info(f"gmail_draft result: {result}")
        return result
    except HttpError as error:
        logger.error(f"gmail_draft error: {error}")
        return f"An error occurred: {error}"
    except RefreshError as error:
        logger.error(f"gmail_draft RefreshError: {error}")
        return "Gmail Authentication Error: Your token has expired or been revoked. Please re-authenticate."


def gmail_read_by_label(label_id: str, max_results: int = 20):
    """
    List the user's emails from a specific label (e.g., 'IMPORTANT', 'SENT', 'INBOX').
    Returns: A list of dicts with subject and snippet.
    """
    logger.info(f"gmail_read_by_label called with: label_id='{label_id}', max_results={max_results}")
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
        logger.info(f"gmail_read_by_label returned {len(email_data)} emails")
        return email_data
    except HttpError as error:
        logger.error(f"gmail_read_by_label error: {error}")
        return f"An error occurred: {error}"
    except RefreshError as error:
        logger.error(f"gmail_read_by_label RefreshError: {error}")
        return "Gmail Authentication Error: Your token has expired or been revoked. Please re-authenticate."


def gmail_get_email_addresses(max_results: int = 20):
    """
    Extract unique email addresses from the most recent emails.
    """
    logger.info(f"gmail_get_email_addresses called with: max_results={max_results}")
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

        result = list(addresses)
        logger.info(f"gmail_get_email_addresses returned {len(result)} email addresses")
        return result
    except HttpError as error:
        logger.error(f"gmail_get_email_addresses error: {error}")
        return f"An error occurred: {error}"
    except RefreshError as error:
        logger.error(f"gmail_get_email_addresses RefreshError: {error}")
        return "Gmail Authentication Error: Your token has expired or been revoked. Please re-authenticate."
