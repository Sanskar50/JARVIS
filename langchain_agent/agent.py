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
    ],
    system_prompt=system_prompt,
)


def ask_agent(user_input: str) -> str:
    """Gets a response from the JARVIS agent for the given input."""
    res = agent.invoke({"messages": [("user", user_input)]})
    ai_message = res["messages"][-1].content
    return ai_message[0]["text"]
