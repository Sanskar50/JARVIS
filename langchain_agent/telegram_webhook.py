import logging
from config import Config
from fastapi import FastAPI, Request
from httpx import AsyncClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

BOT_TOKEN = Config.TELEGRAM_BOT_TOKEN
BASE = f"https://api.telegram.org/bot{BOT_TOKEN}"


async def telegram_webhook(req: Request):
    data = await req.json()
    chat_id = data["message"]["chat"]["id"]
    text = data["message"].get("text", "")
    return chat_id, text


async def send_message(chat_id: int, text: str):
    url = f"{BASE}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": str(text),
    }
    async with AsyncClient() as client:
        await client.post(url, json=payload)
