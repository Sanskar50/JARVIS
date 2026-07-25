import requests
import logging
from config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def find_email(first_name: str, last_name: str, domain: str):
    """
    Find the email of a person.
    Returns: A dictionary with the email address.
    """
    logger.info(f"find_email called with: first_name='{first_name}', last_name='{last_name}', domain='{domain}'")
    url = f"https://api.hunter.io/v2/email-finder?domain={domain}&first_name={first_name}&last_name={last_name}&api_key={config.HUNTER_API_KEY}"
    response = requests.get(url)
    email_data = response.json()
    email = email_data["data"]["email"]
    logger.info(f"find_email output: '{email}'")
    return email
