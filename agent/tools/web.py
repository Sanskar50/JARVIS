from agent.schemas.tools import WebSearchInput

def search_web(input_data: WebSearchInput):
    """
    Mock function to search the web.
    """
    # In a real app, this would call a search engine API
    return [
        {"title": "Result 1", "url": "http://example.com/1", "snippet": "Description 1"},
        {"title": "Result 2", "url": "http://example.com/2", "snippet": "Description 2"}
    ]
