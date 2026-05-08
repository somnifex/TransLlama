import time
import uuid
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse

from models.requests import ChatCompletionRequest
from models.responses import (
    ChatCompletionResponse,
    ChatCompletionChoice,
    ChatMessageResponse,
    Usage,
)
from api.dependencies import get_api_key_with_rate_limit

router = APIRouter()


@router.post("/v1/chat/completions", tags=["Chat"])
async def chat_completions(
    request: Request,
    chat_request: ChatCompletionRequest,
    api_key: str = Depends(get_api_key_with_rate_limit)
):
    """
    OpenAI-compatible chat completions endpoint.

    Supports both synchronous and streaming responses.
    Can be used for translation by providing appropriate prompts.

    Requires authentication via API key.
    """
    translation_service = request.app.state.translation_service

    # Handle streaming
    if chat_request.stream:
        return StreamingResponse(
            translation_service.chat_completion_stream(chat_request),
            media_type="text/event-stream",
        )

    # Synchronous completion
    result = await translation_service.chat_completion(chat_request)

    # Convert to our response format if needed
    if isinstance(result, dict) and "choices" in result:
        # Already in correct format from llama-cpp-python
        return result

    # Fallback: construct response
    completion_id = f"chatcmpl-{uuid.uuid4().hex[:8]}"
    created = int(time.time())

    return ChatCompletionResponse(
        id=completion_id,
        object="chat.completion",
        created=created,
        model=chat_request.model or "hy-mt-general",
        choices=[
            ChatCompletionChoice(
                index=0,
                message=ChatMessageResponse(
                    role="assistant",
                    content=result.get("content", ""),
                ),
                finish_reason="stop",
            )
        ],
        usage=Usage(
            prompt_tokens=result.get("usage", {}).get("prompt_tokens", 0),
            completion_tokens=result.get("usage", {}).get("completion_tokens", 0),
            total_tokens=result.get("usage", {}).get("total_tokens", 0),
        ),
    )
