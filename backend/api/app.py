"""
Application
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from .database import init_db
from .routes import conversation_router
from data import import_stations
from prediction import get_prediction_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown."""
    init_db()
    import_stations()
    prediction_service = get_prediction_service()
    app.state.prediction_service = prediction_service
    yield


def create_app() -> FastAPI:
    """Create a FastAPI application instance."""

    app = FastAPI(
        title=settings.API_TITLE,
        description=settings.API_DESCRIPTION,
        version=settings.API_VERSION,
        docs_url="/api/docs",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
    )

    app.include_router(conversation_router, prefix="/api")

    return app
