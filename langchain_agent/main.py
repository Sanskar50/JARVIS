from fastapi import FastAPI, Request
import uvicorn
import logging
from telegram_webhook import telegram_webhook, send_message
from agent import ask_agent

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Initialize FastAPI app
app = FastAPI(title="JARVIS LangChain Webhook")


@app.post("/webhook")
async def agent_handler(req: Request):
    """Entry point for incoming Telegram webhook requests."""
    chat_id, text = await telegram_webhook(req)
    logger.info(f"chat_id is {chat_id} and text is {text}")
    response = ask_agent(text)
    logger.info(f"response is {response}")
    await send_message(chat_id, response)
    return {"ok": True}


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "JARVIS Agent is online."}


if __name__ == "__main__":
    uvicorn.run(app, port=8000)
