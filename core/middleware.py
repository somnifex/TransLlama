import logging
import time
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from core.exceptions import (
    TransLlamaException,
    ModelNotFoundException,
    ModelLoadException,
    InvalidLanguageException,
    AuthenticationException,
    RateLimitException,
    TranslationException,
)

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging requests and responses"""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Log request
        logger.info(f"{request.method} {request.url.path}")

        # Process request
        response = await call_next(request)

        # Log response time
        process_time = time.time() - start_time
        logger.info(f"Completed in {process_time:.3f}s - Status: {response.status_code}")

        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for handling exceptions and returning appropriate responses"""

    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except ModelNotFoundException as e:
            logger.error(f"Model not found: {e}")
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"error": "Model not found", "detail": str(e)},
            )
        except ModelLoadException as e:
            logger.error(f"Model load error: {e}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"error": "Failed to load model", "detail": str(e)},
            )
        except InvalidLanguageException as e:
            logger.error(f"Invalid language: {e}")
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": "Invalid language", "detail": str(e)},
            )
        except AuthenticationException as e:
            logger.error(f"Authentication error: {e}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"error": "Authentication failed", "detail": str(e)},
            )
        except RateLimitException as e:
            logger.error(f"Rate limit exceeded: {e}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"error": "Rate limit exceeded", "detail": str(e)},
            )
        except TranslationException as e:
            logger.error(f"Translation error: {e}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"error": "Translation failed", "detail": str(e)},
            )
        except TransLlamaException as e:
            logger.error(f"TransLlama error: {e}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"error": "Internal error", "detail": str(e)},
            )
        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"error": "Internal server error", "detail": "An unexpected error occurred"},
            )


def setup_cors(app):
    """Setup CORS middleware"""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
