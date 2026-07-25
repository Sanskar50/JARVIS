import requests
import logging
from config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def find_domain(company_name: str) -> list:
    """
    Find the domains and names of a company suggest query.
    Returns: A list of dicts with name and domain.
    """
    logger.info(f"find_domain called with: company_name='{company_name}'")
    url = f"https://autocomplete.clearbit.com/v1/companies/suggest?query={company_name}"
    response = requests.get(url)
    try:
        domain_data = response.json()
        result = []
        if isinstance(domain_data, list):
            for item in domain_data:
                if isinstance(item, dict):
                    name = item.get("name")
                    domain = item.get("domain")
                    result.append({
                        "name": name if name is not None else "",
                        "domain": domain if domain is not None else ""
                    })
    except Exception as e:
        logger.error(f"Error parsing clearbit response: {e}")
        result = []
    logger.info(f"find_domain output: {result}")
    return result
