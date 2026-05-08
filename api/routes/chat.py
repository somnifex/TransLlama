from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse

from models.requests import ChatCompletionRequest
from api.dependencies import get_api_key_with_rate_limit

router = APIRouter()


@router.post("/v1/chat/completions", tags=["Chat"])
async def chat_completions(
    request: Request,
    chat_request: ChatCompletionRequest,
    api_key: str = Depends(get_api_key_with_rate_limit),
):
    """
    OpenAI-compatible chat completions endpoint.
    Supports both synchronous and streaming responses.
    """
    translation_service = request.app.state.translation_service

    if chat_request.stream:
        return StreamingResponse(
            translation_service.chat_completion_stream(chat_request),
            media_type="text/event-stream",
        )

    return await translation_service.chat_completion(chat_request)
