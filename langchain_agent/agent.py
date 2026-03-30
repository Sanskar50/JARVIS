import os
from langchain.tools import tool
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from config import config
from tools.gmail import gmail_read, gmail_send, gmail_draft, gmail_read_by_label

# Load system prompt from file
prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "system_prompt.txt")
with open(prompt_path, "r", encoding="utf-8") as f:
    system_prompt = f.read().strip()


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


model = ChatGoogleGenerativeAI(
    model=config.GEMINI_MODEL_NAME,
    google_api_key=config.GEMINI_API_KEY,
    temperature=0,
)

agent = create_agent(
    model,
    tools=[read_emails, send_emails, draft_email, read_emails_by_label],
    system_prompt=system_prompt,
)


def ask_agent(user_input: str) -> str:
    """Gets a response from the JARVIS agent for the given input."""
    res = agent.invoke({"messages": [("user", user_input)]})
    ai_message = res["messages"][-1].content
    return ai_message[0]["text"]
