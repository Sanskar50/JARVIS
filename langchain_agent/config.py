import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME")
    GEMINI_FALLBACK_MODEL_NAME = os.getenv("GEMINI_FALLBACK_MODEL_NAME")
    WEATHER_API_BASE_URL = os.getenv("WEATHER_API_BASE_URL")
    API_KEY = os.getenv("API_KEY")
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    GMAIL_TOKEN = os.getenv("GMAIL_TOKEN")
    GMAIL_REFRESH_TOKEN = os.getenv("GMAIL_REFRESH_TOKEN")
    GMAIL_CLIENT_ID = os.getenv("GMAIL_CLIENT_ID")
    GMAIL_CLIENT_SECRET = os.getenv("GMAIL_CLIENT_SECRET")
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    HUNTER_API_KEY = os.getenv("HUNTER_API_KEY")


config = Config()
