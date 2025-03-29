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

3. Start PostgreSQL database using Docker:

   ```bash
   docker run --name chatbot-db -e POSTGRES_PASSWORD=postgres -e POSTGRES_USER=postgres -e POSTGRES_DB=chatbot -p 5432:5432 -d postgres:alpine
   ```

4. Set up environment variables:

   ```bash
   cp .env.example .env
   ```

   The default values in `.env.example` are configured to work with the Docker container above. If you're using a different database setup, modify the values in `.env` accordingly.

## Running the Application

1. Make sure you're in the project root directory and your virtual environment is activated

2. Start the server:
   ```bash
   uv run main.py
   ```

The server will start on `http://0.0.0.0:8080` with hot-reload enabled.

## API Documentation

Once the server is running, you can access the interactive API documentation at:

```
http://localhost:8080/api/docs
```

This Swagger UI interface allows you to explore and test all available REST endpoints.

## WebSocket Connection

To connect to a specific conversation for real-time chat, use the WebSocket endpoint:

```
ws://localhost:8080/api/conversations/{conversation_id}
```

Replace `{conversation_id}` with the UUID of the conversation you want to connect to.

You can test the WebSocket connections using tools like:

- Postman's WebSocket Client
- WebSocket testing websites (e.g., websocket.org)
- Browser's Developer Console

## Project Structure

- `api/` - FastAPI application and WebSocket handlers
- `chatbot/` - Chatbot implementation and NLP processing
- `main.py` - Application entry point
