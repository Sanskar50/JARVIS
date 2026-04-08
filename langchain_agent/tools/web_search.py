from tavily import TavilyClient
from config import config


def web_search(query: str):
    """
    Search the web for the given query.
    Returns: A list of dicts with title, url, and snippet.
    """
    client = TavilyClient(config.TAVILY_API_KEY)
    response = client.search(query=query, search_depth="advanced")
    return response
