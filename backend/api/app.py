"""
Application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from chatbot.chatbot import ChatBot
from .websocket import router as websocket_router


def create_app() -> FastAPI:
    """Create a FastAPI application instance."""

    app = FastAPI(
        title="AI Chatbot API",
        description="API for interacting with an AI chatbot through WebSocket connections",
        version="1.0.0",
    )

    app.state.chatbot = ChatBot()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(websocket_router)

    return app
