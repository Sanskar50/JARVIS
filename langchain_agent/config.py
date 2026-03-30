import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME")
    WEATHER_API_BASE_URL = os.getenv("WEATHER_API_BASE_URL")
    API_KEY = os.getenv("API_KEY")
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


config = Config()
