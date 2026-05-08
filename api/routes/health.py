import time
from fastapi import APIRouter, Request

from models.responses import HealthResponse

router = APIRouter()

# Store startup time
startup_time = time.time()


@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check(request: Request):
    """
    Health check endpoint.

    Returns server health status and basic metrics.
    """
    model_manager = request.app.state.model_manager
    uptime = time.time() - startup_time

    return HealthResponse(
        status="healthy",
        models_loaded=model_manager.get_loaded_models_count(),
        uptime_seconds=uptime,
    )
