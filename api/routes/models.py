import time
from fastapi import APIRouter, Depends, Request

from models.responses import ModelsListResponse, ModelInfo
from api.dependencies import get_api_key_with_rate_limit

router = APIRouter()


@router.get("/v1/models", response_model=ModelsListResponse, tags=["Models"])
async def list_models(
    request: Request,
    api_key: str = Depends(get_api_key_with_rate_limit)
):
    """
    List all available translation models.

    Requires authentication via API key.
    """
    model_manager = request.app.state.model_manager
    models_info = model_manager.list_models()

    # Convert to ModelInfo objects
    model_data = []
    for info in models_info:
        model_data.append(
            ModelInfo(
                id=info["id"],
                object="model",
                created=int(time.time()),
                owned_by="transllama",
                description=info["description"],
                supported_languages=info["supported_languages"],
            )
        )

    return ModelsListResponse(
        object="list",
        data=model_data,
    )
