# AI Chatbot Backend

## Installation

1. Install uv if you haven't already:

   ```bash
   pip install uv
   ```

2. Create a Python virtual environment and install dependencies:
   ```bash
   uv venv --python 3.11.11
   source .venv/bin/activate
   uv sync
   ```

## Running the Application

1. Make sure you're in the project root directory and your virtual environment is activated

2. Start the server:
   ```bash
   uv run main.py
   ```

The server will start on `http://0.0.0.0:8080` with hot-reload enabled.

## WebSocket Connection

To connect to the chatbot, use the WebSocket endpoint:

```
ws://localhost:8080/ws
```

You can test the WebSocket endpoint using Postman's WebSocket Client feature.

## Project Structure

- `api/` - FastAPI application and WebSocket handlers
- `chatbot/` - Chatbot implementation and NLP processing
- `main.py` - Application entry point
