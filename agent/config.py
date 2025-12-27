import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4")
    DB_CONNECTION_STRING = os.getenv("DB_CONNECTION_STRING", "sqlite:///agent.db")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

config = Config()
