import os
import uvicorn
import logging
from telegram_utils import telegram_webhook, send_message
from agent import ask_agent
from fastapi import FastAPI, Request

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Initialize FastAPI app
app = FastAPI(title="JARVIS LangChain Webhook")


@app.post("/webhook")
async def agent_handler(req: Request):
    """Entry point for incoming Telegram webhook requests."""
    chat_id, text = await telegram_webhook(req)
    logger.info(f"chat_id={chat_id} text={text!r}")
    response = ask_agent(text, chat_id=chat_id)
    logger.info(f"agent response: {response}")

    # Send the final text summary back to the user.
    await send_message(chat_id, response)
    return {"ok": True}


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "JARVIS Agent is online."}


def test_run():
    """Test the JARVIS agent in an interactive CLI loop (no Telegram sends)."""
    print("Welcome to JARVIS Test Mode. Type 'exit' to quit.")
    print("Note: Telegram sends are skipped in test mode (no chat_id).\n")
    while True:
        query = input("Enter your query: ").strip()
        if query.lower() in ["exit", "quit", "q"]:
            break
        if not query:
            continue
        print(f"\nJARVIS: {ask_agent(query)}\n")


if __name__ == "__main__":
    if os.getenv("TEST_MODE", "true") == "true":
        test_run()
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
