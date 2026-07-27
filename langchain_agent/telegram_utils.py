import logging
import os
from config import Config
from fastapi import FastAPI, Request
from httpx import AsyncClient
import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


def _bot_url(path: str) -> str:
    """Build Telegram API URL lazily so the token is always current."""
    token = Config.TELEGRAM_BOT_TOKEN
    return f"https://api.telegram.org/bot{token}/{path}"


async def telegram_webhook(req: Request):
    data = await req.json()
    chat_id = data["message"]["chat"]["id"]
    text = data["message"].get("text", "")
    return chat_id, text


async def send_message(chat_id: int, text: str):
    payload = {"chat_id": chat_id, "text": str(text)}
    async with AsyncClient() as client:
        await client.post(_bot_url("sendMessage"), json=payload)


def send_message_sync(chat_id: int, text: str) -> bool:
    """Send a plain-text Telegram message synchronously."""
    if not chat_id:
        logger.warning("send_message_sync called with no chat_id — skipping.")
        return False
    payload = {"chat_id": chat_id, "text": str(text)}
    resp = httpx.post(_bot_url("sendMessage"), json=payload, timeout=15)
    if resp.status_code == 200:
        logger.info(f"Telegram message sent to {chat_id}")
        return True
    logger.error(f"Telegram sendMessage failed: {resp.status_code} {resp.text[:300]}")
    return False


def upload_document_sync(chat_id: int, file_path: str, caption: str = "") -> bool:
    """Upload a file (PDF, .tex, etc.) to Telegram synchronously."""
    if not chat_id:
        logger.warning("upload_document_sync called with no chat_id — skipping.")
        return False
    if not os.path.exists(file_path):
        logger.error(f"upload_document_sync: file not found: {file_path}")
        return False
    filename = os.path.basename(file_path)
    mime = "application/pdf" if file_path.endswith(".pdf") else "application/octet-stream"
    with open(file_path, "rb") as f:
        file_bytes = f.read()
    resp = httpx.post(
        _bot_url("sendDocument"),
        data={"chat_id": chat_id, "caption": caption},
        files={"document": (filename, file_bytes, mime)},
        timeout=60,
    )
    if resp.status_code == 200:
        logger.info(f"Telegram upload OK: {filename} → chat {chat_id}")
        return True
    logger.error(f"Telegram upload failed: {resp.status_code} {resp.text[:300]}")
    return False
