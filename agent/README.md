# JARVIS Agent

This is the core agent logic for JAMVIS.

## Setup Instructions

To set up the development environment, follow these steps:

### 1. Create a Virtual Environment
It is recommended to use a virtual environment to manage dependencies.

**On Windows:**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies
Once the virtual environment is activated, install the required packages:

```bash
pip install -r requirements.txt
```

### 3. Configuration
Create a `.env` file in this directory and add your API keys:

```env
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL_NAME=gemini-2.5-flash
```

### 4. Running the Agent
You can run the agent using:

```bash
python main.py
```
