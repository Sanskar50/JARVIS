from agent.observability.tracing import logger
from agent.tools.weather import get_weather
from agent.tools.db import execute_query
from agent.tools.web import search_web

class AgentController:
    def __init__(self):
        self.tools = {
            "get_weather": get_weather,
            "execute_query": execute_query,
            "search_web": search_web
        }
        self.system_prompt = self._load_system_prompt()

    def _load_system_prompt(self):
        try:
            with open("agent/prompts/system.txt", "r") as f:
                return f.read()
        except FileNotFoundError:
            logger.warning("System prompt file not found, using default.")
            return "You are a helpful assistant."

    def process_request(self, user_input: str):
        logger.info(f"Processing request: {user_input}")
        # Here you would integrate with an LLM to decide which tool to call
        # For boilerplate, we'll just return a mock response
        return f"Processed: {user_input}"

    def run(self):
        logger.info("Agent Controller started.")
