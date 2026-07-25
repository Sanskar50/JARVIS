import logging
from tavily import TavilyClient
from config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def web_search(query: str):
    """
    Search the web for the given query.
    Returns: A list of dicts with title, url, and snippet.
    """
    logger.info(f"web_search called with: query='{query}'")
    client = TavilyClient(config.TAVILY_API_KEY)
    response = client.search(query=query, search_depth="advanced")
    logger.info(f"web_search output length: {len(response.get('results', [])) if isinstance(response, dict) else 'unknown'}")
    return response
