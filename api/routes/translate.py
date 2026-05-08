from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse

from models.requests import TranslateRequest
from models.responses import TranslateResponse
from api.dependencies import get_api_key_with_rate_limit

router = APIRouter()


@router.post("/v1/translate", response_model=TranslateResponse, tags=["Translation"])
async def translate(
    request: Request,
    translate_request: TranslateRequest,
    api_key: str = Depends(get_api_key_with_rate_limit)
):
    """
    Translate text from source language to target language.

    Supports:
    - Custom terminology injection
    - Context-aware translation
    - Format preservation
    - Streaming output

    Requires authentication via API key.
    """
    translation_service = request.app.state.translation_service

    # Handle streaming
    if translate_request.stream:
        return StreamingResponse(
            translation_service.translate_stream(translate_request),
            media_type="text/event-stream",
        )

    # Synchronous translation
    result = await translation_service.translate(translate_request)

    return TranslateResponse(**result)
