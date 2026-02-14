# 🤖 JARVIS Agent

**JARVIS** (Just A Rather Very Intelligent System) is a modular, agentic AI assistant powered by Google's Gemini models. It is designed to process natural language queries, autonomously decide on tool usage, fetch real-time data, and present information in a polished, human-readable format.

---

## 🚀 Key Features

-   **Multi-Step Reasoning**: Uses an iterative agentic loop to process complex user requests.
-   **Autonomous Tool Use**: Dynamically decides when to call external APIs (Weather, Temperature, AQI).
-   **Rich Terminal UI**: Beautifully formatted tables and console output using the `rich` library.
-   **Modular Architecture**: Easily extensible tool system and prompt management.
-   **Prompt Engineering**: Decoupled system, function-calling, and output prompts for fine-grained control.

---

## 🛠️ Tech Stack

-   **Core**: Python 3.9+
-   **LLM Engine**: [Google Gemini Pro / Flash](https://ai.google.dev/)
-   **SDK**: `google-generativeai`
-   **Environment**: `python-dotenv` for secure secret management.
-   **API Clients**: `requests` for RESTful interactions.
-   **UI/Observability**: `rich` (formatting) & standard `logging`.

---

## 🏗️ Technical Architecture

JARVIS follows a **Controller-Tool-Prompt** architecture pattern, optimized for agentic workflows.

### 1. Request Lifecycle
1.  **Intent Discovery**: The LLM receives the user input along with a `function_calling` prompt to determine if any external data is needed.
2.  **Tool Execution**: The `AgentController` parses the LLM's JSON request and executes the corresponding local function from the `agent.tools` module.
3.  **Data Synthesis**: The results from the tool execution are passed back to the LLM (along with the `output` prompt) to synthesize a final natural language response.
4.  **Formatting**: The final output is parsed into structured data and rendered as an interactive table or styled block using `rich`.

### 2. File Structure
```text
agent/
├── tools/             # Modular API integration functions
├── prompts/           # System, tool-choice, and formatting prompts
├── schemas/           # Data models for validation
├── observability/     # Logging and tracing utilities
├── agent_controller.py# The "Brain" - Orchestrates LLM and tool logic
└── main.py            # CLI Entry point
```

---

## ⚙️ Setup Instructions

### 1. Prerequisites
- Python 3.8 or higher installed.
- A Google AI Studio API Key ([Get one here](https://aistudio.google.com/)).

### 2. Installation
Clone the repository and navigate to the `agent` directory:

```powershell
# Create a virtual environment
python -m venv venv

# Activate on Windows
.\venv\Scripts\activate

# Activate on macOS/Linux
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration
Create a `.env` file in the `agent/` directory:

```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL_NAME=gemma-3-27b-it # or gemini models
# Optional API keys for tools
WEATHER_API_BASE_URL=https://api.weatherapi.com/v1
API_KEY=your_weather_api_key
```

### 4. Usage
Launch the agent via the terminal:

```bash
python main.py
```

---

### 5. Inference

<img width="714" height="219" alt="image" src="https://github.com/user-attachments/assets/29e6938f-c8f0-421e-b7d0-0cd5db60eaaa" />
<img width="1620" height="626" alt="image" src="https://github.com/user-attachments/assets/6f191580-5db3-44ad-80a7-8d7f7b5ed4b7" />




## 🛣️ Roadmap
- [ ] Add support for persistent memory/history.
- [ ] Implement more tools (Calendar, Email, Search).
- [ ] Add a Web-based interface.
- [ ] Full Pydantic validation for tool outputs.
