# JARVIS: Agentic AI Recruitment Assistant

JARVIS is a state-of-the-art AI agent designed to automate the professional recruitment outreach process. Built using **LangChain** and powered by **Google Gemini**, JARVIS can autonomously search the web, identify professional contact information, and send personalized recruitment emails with resume attachments.

## 🚀 Key Features

- **Autonomous Contact Discovery**: Converts LinkedIn URLs into verified professional email addresses using a combination of web search and the Hunter.io API.
- **Smart Gmail Integration**: 
    - Full inbox management (Read, Send, Draft).
    - **Resume Attachment**: Sends a predefined resume PDF with one command.
    - **Dynamic Templates**: Uses HSL-tailored email templates with automatic name and company population.
    - **Auto-Signature**: Fetches your real Gmail signature (HTML or Plain) and appends it to outgoing emails.
- **Resilient Architecture**: Implements a robust fallback mechanism that automatically switches to a secondary model (e.g., Gemini Flash) if the primary model (Gemini Pro) experiences downtime (503) or rate limits.
- **Interactive Interface**: Supports both a FastAPI-powered web backend and a local CLI test mode.

## 🏗️ Architecture Overview

The system is modularized into several core components:

### 1. Agent Orchestration (`agent.py`)
The "brain" of JARVIS. It initializes the **Gemini 3.1** models and binds them to a suite of specialized tools. It uses LangChain's `create_agent` for complex reasoning and tool selection.

### 2. Tool Suite (`tools/`)
- **`gmail.py`**: A high-level wrapper around the Google Gmail API. It handles OAuth2 token refreshing and complex MIME message construction for attachments and signatures.
- **`find_email.py`**: Interfaces with the **Hunter.io API** to perform professional email lookups based on name and domain.
- **`web_search.py`**: Powered by **Tavily**, allowing the agent to research companies and LinkedIn profiles in real-time.

### 3. Core Logic & API (`main.py`)
A **FastAPI** application that serves as the entry point. It handles asynchronous requests and provides a `test_run` loop for developers to interact with the agent locally.

### 4. Configuration (`config.py` & `.env`)
Centralized management of secrets (API Keys, OAuth Tokens) and model parameters.

## 📂 File Structure

```text
langchain_agent/
├── tools/                  # Specialized tool implementations
│   ├── gmail.py            # Gmail API logic (Read/Send/Signature)
│   ├── find_email.py       # Hunter.io integration
│   └── web_search.py       # Tavily search integration
├── prompts/                # System instructions & personality
│   └── system_prompt.txt   # Detailed agent behavior guidelines
├── sources/                # Assets & Templates
│   ├── template.py         # Email body/subject templates
│   └── Sanskar_Suri_Resume.pdf # Default attachment
├── agent.py                # Agent initialization & tool binding
├── main.py                 # FastAPI app & CLI entry point
├── config.py               # Env var management
├── .env                    # Secrets (API Keys, Models)
└── generate_token.py       # Helper script for Gmail OAuth2
```

## 🛠️ Setup & Installation

1. **Prerequisites**: Python 3.11+
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Gmail Authentication**:
   - Ensure you have `credentials.json` from the Google Cloud Console.
   - Run the token generation script:
     ```bash
     python generate_token.py
     ```
   - Follow the instructions in the terminal to update your `.env` file with the generated tokens.

4. **Environment Variables**: Create a `.env` file with the following:
   - `GEMINI_API_KEY`: Your Google AI Studio key.
   - `GEMINI_MODEL_NAME`: e.g., `gemini-3.1-pro-preview`
   - `HUNTER_API_KEY`: For email lookups.
   - `TAVILY_API_KEY`: For web searching.
   - `GMAIL_TOKEN` & `GMAIL_REFRESH_TOKEN`: OAuth2 credentials.

## 🤖 Usage Example

**Query**: *"Find the email of Shikha Solankey who works at Databricks from her LinkedIn url [URL] and send her my resume."*

**JARVIS Execution Flow**:
1. Extracts "Shikha Solankey" and "Databricks" from the query/URL.
2. Uses `web_search` to find the `databricks.com` domain.
3. Calls `find_email` via Hunter.io to get the verified address.
4. Loads the resume template and attaches the local PDF.
5. Fetches your Gmail signature.
6. Sends the email and confirms the **Message ID** and status to you.

---
*Built with ❤️ for Advanced Agentic Coding.*
