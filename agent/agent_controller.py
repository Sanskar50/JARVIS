from google import genai
from agent.tools.weather import get_weather
from agent.tools.temp import get_temperature
from agent.tools.aqi import get_aqi
from agent.config import config


class AgentController:
    def __init__(self):
        self.tools = {
            "get_weather": get_weather,
            "get_temperature": get_temperature,
            "get_aqi": get_aqi,
        }
        self.system_prompt = self._load_system_prompt()

    def get_weather(self, location: str):
        return self.tools.get("get_weather")({"location": location})

    def get_temperature(self, location: str):
        return self.tools.get("get_temperature")({"location": location})

    def get_aqi(self, location: str):
        return self.tools.get("get_aqi")({"location": location})

    def call_gemini(self, prompt):
        client = genai.Client(api_key=config.GEMINI_API_KEY)
        try:
            response = client.models.generate_content(
                model=config.GEMINI_MODEL_NAME,
                contents=prompt,
            )
            return response.text.strip()
        except Exception as e:
            return f"Error generating alerts: {str(e)}"

    def _load_system_prompt(self):
        try:
            with open("agent/prompts/system.txt", "r") as f:
                return f.read()
        except FileNotFoundError:
            print("System prompt file not found, using default.")
            return "You are a helpful assistant."

    def process_request(self, user_input: str):
        print(f"Processing request: {user_input}")

        return f"Processed: {user_input}"

    def run(self):
        print("Agent Controller started.")
