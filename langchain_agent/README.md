# JARVIS: Agentic AI Framework

JARVIS is a modular Agentic AI system built on **LangChain** and **Google Gemini**. It leverages a multi-tool architecture to bridge the gap between Large Language Models and real-world enterprise integrations, including Google Workspace, professional data APIs, and real-time web intelligence.

## 🏗️ Core Architecture

The system is designed with a **decoupled tool-calling architecture**, allowing the LLM to act as a reasoning engine that orchestrates complex workflows across multiple external services.

### 1. Reasoning & Orchestration (`agent.py`)
- **Model Agnostic Framework**: Uses LangChain's `create_agent` to manage state and tool execution.
- **Resilient Model Fallback**: Implements an automated failover strategy using `.with_fallbacks()`. If the primary model encounters a `503 Service Unavailable` or `429 Rate Limit`, the system automatically re-routes the request to a secondary model without losing context.
- **Dynamic Prompting**: System instructions are externalized in `prompts/system_prompt.txt`, allowing for rapid iteration of agent behavior.

### 2. Service Integrations (`tools/`)
The agent's capabilities are extended via a suite of specialized Python-based tools:

#### 📬 Google Workspace Integration (`gmail.py`)
- **OAuth2 Lifecycle**: Managed via `generate_token.py`, supporting automated token refreshing to prevent `invalid_grant` errors.
- **Bi-Directional Communication**: Support for listing, reading, drafting, and sending emails.
- **Advanced MIME Support**: Programmatically handles attachments (PDF/Images) and constructs multi-part messages.
- **Contextual Awareness**: Dynamically fetches the user's authentic Gmail signature (HTML/Plain) via `service.users().settings()` to ensure outgoing communications match the user's professional identity.

#### 🔍 Professional Intelligence (`find_email.py`)
- **Hunter.io Integration**: Programmatic lookup of professional contact information using domain-based discovery patterns.
- **Data Verification**: Extracts verified email addresses, confidence scores, and source tracking.

#### 🌐 Web Intelligence (`web_search.py`)
- **Tavily API**: Real-time web crawling and search optimization.
- **Context Injection**: Allows the agent to research real-time data (LinkedIn profiles, company domains, news) to inform subsequent tool calls.

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
└── .env                    # Secrets (API Keys, Models)
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

## 🔄 Integration Flow Example

1. **Query**: User provides a high-level task requiring external data.
2. **Step A (Research)**: Agent uses `web_search` to find domains or identifiers.
3. **Step B (Discovery)**: Agent uses `find_email` to resolve identities to contact endpoints.
4. **Step C (Action)**: Agent uses `gmail_send` or `gmail_draft` to finalize the workflow, automatically injecting the user's signature and any requested attachments.

---
*Built with ❤️ for Advanced Agentic Coding.*
