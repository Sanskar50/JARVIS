import os
from langchain.tools import tool
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from config import config
from tools.gmail import (
    gmail_read,
    gmail_send,
    gmail_draft,
    gmail_read_by_label,
    gmail_get_email_addresses,
    gmail_send_with_resume,
)
from tools.web_search import web_search as run_web_search
from tools.find_email import find_email as run_find_email
from tools.find_domain import find_domain as run_find_domain
from tools.generate_resume import generate_resume as run_generate_resume
from telegram_utils import send_message_sync, upload_document_sync

# Load system prompt from file
prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "system_prompt.txt")
with open(prompt_path, "r", encoding="utf-8") as f:
    system_prompt = f.read().strip()


@tool
def find_email(first_name: str, last_name: str, domain: str):
    """
    Find the email of a person.
    Returns: A dictionary with the email address.
    """
    return run_find_email(first_name, last_name, domain)


@tool
def web_search(query: str):
    """
    Search the web for the given query.
    Returns: A list of dicts with title, url, and snippet.
    """
    return run_web_search(query)


@tool
def read_emails(max_results: int = 5):
    """
    List the user's most recent emails.
    Returns: A list of dicts with subject and snippet.
    """
    return gmail_read(max_results)


@tool
def send_emails(to: str, subject: str, body: str):
    """
    Send an email message.
    """
    return gmail_send(to, subject, body)


@tool
def send_email_with_resume(to: str, company_name: str, first_name: str):
    """
    Send an email with the user's resume attached using a predefined template.
    Args:
        to: The recipient's email address.
        company_name: The name of the company the recipient belongs to.
        first_name: The first name of the recipient.
    """
    return gmail_send_with_resume(to, company_name, first_name)


@tool
def draft_email(to: str, subject: str, body: str):
    """
    Create a draft email.
    """
    return gmail_draft(to, subject, body)


@tool
def read_emails_by_label(label_id: str, max_results: int = 10):
    """
    List the user's emails from a specific label (e.g., 'IMPORTANT', 'SENT', 'INBOX').
    Returns: A list of dicts with subject and snippet.
    """
    return gmail_read_by_label(label_id, max_results)


@tool
def get_email_addresses(max_results: int = 20):
    """
    Extract unique email addresses from the most recent emails.
    """
    return gmail_get_email_addresses(max_results)


@tool
def find_domain(company_name: str):
    """
    Find company names and domains matching the given company name query.
    Returns: A list of dicts with company name and domain.
    """
    return run_find_domain(company_name)


@tool
def generate_resume(job_description: str):
    """
    Generate a tailored resume PDF from the base LaTeX template.
    Modifies only the editable sections (Experience, Projects, Skills, Achievements)
    based on the job_description and compiles to PDF.
    Args:
        job_description: Description of the target role or specific changes to apply to the resume.
    Returns: dict with tex_path and pdf_path (pdf_path is None if compilation failed).
    """
    return run_generate_resume(job_description)


@tool
def send_telegram_message(chat_id: int, text: str):
    """
    Send a plain-text message to a Telegram chat.
    Args:
        chat_id: The Telegram chat ID to send the message to (available from context).
        text: The message text to send.
    Returns: True if sent successfully, False otherwise.
    """
    return send_message_sync(chat_id, text)


@tool
def upload_to_telegram(chat_id: int, file_path: str, caption: str = ""):
    """
    Upload a file (PDF, document, etc.) to a Telegram chat.
    Use this after generate_resume to send the PDF to the user.
    Args:
        chat_id: The Telegram chat ID (available from context).
        file_path: Absolute path to the file to upload (use pdf_path from generate_resume).
        caption: Optional caption for the uploaded file.
    Returns: True if uploaded successfully, False otherwise.
    """
    return upload_document_sync(chat_id, file_path, caption)


model = ChatGoogleGenerativeAI(
    model=config.GEMINI_MODEL_NAME,
    google_api_key=config.GEMINI_API_KEY,
    temperature=0,
)

fallback_model = ChatGoogleGenerativeAI(
    model=config.GEMINI_FALLBACK_MODEL_NAME,
    google_api_key=config.GEMINI_API_KEY,
    temperature=0,
)

model = model.with_fallbacks([fallback_model])

agent = create_agent(
    model,
    tools=[
        web_search,
        read_emails,
        send_emails,
        draft_email,
        read_emails_by_label,
        get_email_addresses,
        find_email,
        send_email_with_resume,
        find_domain,
        generate_resume,
        send_telegram_message,
        upload_to_telegram,
    ],
    system_prompt=system_prompt,
)


def ask_agent(user_input: str, chat_id: int = 0) -> str:
    """Gets a response from the JARVIS agent for the given input."""
    # Inject chat_id so the LLM can pass it to send_telegram_message / upload_to_telegram
    if chat_id:
        augmented_input = f"[context: chat_id={chat_id}]\n{user_input}"
    else:
        augmented_input = user_input

    res = agent.invoke({"messages": [("user", augmented_input)]})

    tool_calls = []
    for msg in res.get("messages", []):
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            for tc in msg.tool_calls:
                tool_calls.append(f"Tool: {tc['name']}, Args: {tc['args']}")
        elif (
            hasattr(msg, "additional_kwargs") and "tool_calls" in msg.additional_kwargs
        ):
            for tc in msg.additional_kwargs["tool_calls"]:
                function_info = tc.get("function", {})
                tool_calls.append(
                    f"Tool: {function_info.get('name')}, Args: {function_info.get('arguments')}"
                )

    if tool_calls:
        print("\n--- Tool Calls Made in Sequence ---")
        for i, tc in enumerate(tool_calls, 1):
            print(f"{i}. {tc}")
        print("-----------------------------------\n")
    else:
        print("\n--- No Tool Calls Made ---\n")

    ai_message = res["messages"][-1].content
    if (
        isinstance(ai_message, list)
        and len(ai_message) > 0
        and isinstance(ai_message[0], dict)
        and "text" in ai_message[0]
    ):
        response_text = ai_message[0]["text"]
    elif isinstance(ai_message, str):
        response_text = ai_message
    else:
        response_text = str(ai_message)

    if tool_calls:
        tool_sequence_str = "\n\n**Tool Calls Made in Sequence:**\n" + "\n".join(
            f"{i}. {tc}" for i, tc in enumerate(tool_calls, 1)
        )
        response_text += tool_sequence_str
    else:
        response_text += "\n\n**Tool Calls Made in Sequence:**\nNone"

    return response_text
