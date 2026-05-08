import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from services.model_manager import ModelManager
from services.translation_service import TranslationService
from core.config import settings
from core.middleware import (
    LoggingMiddleware,
    ErrorHandlingMiddleware,
    setup_cors,
)
from api.routes import health, models, translate, chat

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    logger.info("Starting TransLlama API server...")

    # Initialize ModelManager
    model_manager = ModelManager()
    app.state.model_manager = model_manager

    # Initialize TranslationService
    translation_service = TranslationService(model_manager)
    app.state.translation_service = translation_service

    logger.info(f"Server started on {settings.host}:{settings.port}")
    logger.info(f"Configured models: {len(model_manager.config.models)}")
    logger.info(f"Default model: {model_manager.get_default_model_name()}")

    yield

    # Shutdown
    logger.info("Shutting down TransLlama API server...")


# Create FastAPI app
app = FastAPI(
    title="TransLlama",
    description="Self-hosted translation API backend with FastAPI and llama-cpp-python",
    version="0.1.0",
    lifespan=lifespan,
)

# Setup CORS
setup_cors(app)

# Add middleware
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(LoggingMiddleware)

# Register routers
app.include_router(health.router)
app.include_router(models.router)
app.include_router(translate.router)
app.include_router(chat.router)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "name": "TransLlama",
        "version": "0.1.0",
        "description": "Self-hosted translation API backend",
        "endpoints": {
            "health": "/health",
            "models": "/v1/models",
            "translate": "/v1/translate",
            "chat_completions": "/v1/chat/completions",
            "docs": "/docs",
        }
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=False,
        log_level=settings.log_level.lower(),
    )
