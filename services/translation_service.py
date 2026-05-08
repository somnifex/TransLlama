import asyncio
import json
import logging
import time
import uuid
from typing import Dict, AsyncGenerator

from services.model_manager import ModelManager
from services.prompt_builder import PromptBuilder
from models.requests import TranslateRequest, ChatCompletionRequest
from core.exceptions import TranslationException, InvalidLanguageException

logger = logging.getLogger(__name__)

STOP_TOKENS = ["<|im_end|>", "<|endoftext|>"]
_LEAK_TOKENS = ("<|im_end|>", "<|endoftext|>", "<|im_start|>", "<|im_end>", '<|im_end="">')


def _clean_output(text: str) -> str:
    """Strip any leaked special tokens from model output."""
    for token in _LEAK_TOKENS:
        text = text.replace(token, "")
    return text.strip()


def _wrap_chatml(messages: list[dict]) -> str:
    """Wrap messages in ChatML template for raw completion."""
    parts = []
    for msg in messages:
        parts.append(f"<|im_start|>{msg['role']}\n{msg['content']}<|im_end|>")
    parts.append("<|im_start|>assistant\n")
    return "\n".join(parts)


class TranslationService:
    """Orchestrates translation requests using ModelManager and PromptBuilder"""

    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager
        self.prompt_builder = PromptBuilder()

    async def translate(self, request: TranslateRequest) -> Dict:
        """Perform synchronous translation."""
        try:
            model, model_config = await self.model_manager.get_model(request.model)

            self._validate_languages(
                request.source_lang,
                request.target_lang,
                model_config.supported_languages,
            )

            prompt = self.prompt_builder.build_translation_prompt(
                source_text=request.text,
                source_lang=request.source_lang,
                target_lang=request.target_lang,
                terminology=request.terminology,
                context=request.context,
                preserve_format=request.preserve_format,
            )

            logger.info(f"Translating from {request.source_lang} to {request.target_lang}")

            full_prompt = _wrap_chatml([{"role": "user", "content": prompt}])
            result = await asyncio.to_thread(
                model.create_completion,
                prompt=full_prompt,
                temperature=model_config.parameters.temperature,
                top_p=model_config.parameters.top_p,
                top_k=model_config.parameters.top_k,
                max_tokens=model_config.parameters.max_tokens,
                repeat_penalty=model_config.parameters.repeat_penalty,
                stop=STOP_TOKENS,
                stream=False,
            )

            translation = _clean_output(result["choices"][0]["text"])

            return {
                "translation": translation,
                "source_lang": request.source_lang,
                "target_lang": request.target_lang,
                "model": model_config.name,
                "usage": {
                    "characters": len(request.text),
                    "prompt_tokens": result.get("usage", {}).get("prompt_tokens", 0),
                    "completion_tokens": result.get("usage", {}).get("completion_tokens", 0),
                },
            }

        except (InvalidLanguageException, TranslationException):
            raise
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            raise TranslationException(f"Translation failed: {e}")

    async def translate_stream(self, request: TranslateRequest) -> AsyncGenerator[str, None]:
        """Perform streaming translation."""
        try:
            model, model_config = await self.model_manager.get_model(request.model)

            self._validate_languages(
                request.source_lang,
                request.target_lang,
                model_config.supported_languages,
            )

            prompt = self.prompt_builder.build_translation_prompt(
                source_text=request.text,
                source_lang=request.source_lang,
                target_lang=request.target_lang,
                terminology=request.terminology,
                context=request.context,
                preserve_format=request.preserve_format,
            )

            logger.info(f"Streaming translation from {request.source_lang} to {request.target_lang}")

            full_prompt = _wrap_chatml([{"role": "user", "content": prompt}])
            stream = await asyncio.to_thread(
                model.create_completion,
                prompt=full_prompt,
                temperature=model_config.parameters.temperature,
                top_p=model_config.parameters.top_p,
                top_k=model_config.parameters.top_k,
                max_tokens=model_config.parameters.max_tokens,
                repeat_penalty=model_config.parameters.repeat_penalty,
                stop=STOP_TOKENS,
                stream=True,
            )

            for chunk in stream:
                text = _clean_output(chunk["choices"][0].get("text", ""))
                if text:
                    data = json.dumps({"text": text})
                    yield f"data: {data}\n\n"

            yield "data: [DONE]\n\n"

        except Exception as e:
            logger.error(f"Streaming translation failed: {e}")
            error_data = json.dumps({"error": str(e)})
            yield f"data: {error_data}\n\n"

    async def chat_completion(self, request: ChatCompletionRequest) -> Dict:
        """Perform OpenAI-compatible chat completion."""
        try:
            model, model_config = await self.model_manager.get_model(request.model)

            messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]

            temperature = request.temperature if request.temperature is not None else model_config.parameters.temperature
            top_p = request.top_p if request.top_p is not None else model_config.parameters.top_p
            top_k = request.top_k if request.top_k is not None else model_config.parameters.top_k
            max_tokens = request.max_tokens if request.max_tokens is not None else model_config.parameters.max_tokens

            logger.info(f"Generating chat completion with model {model_config.name}")

            full_prompt = _wrap_chatml(messages)
            result = await asyncio.to_thread(
                model.create_completion,
                prompt=full_prompt,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                max_tokens=max_tokens,
                repeat_penalty=model_config.parameters.repeat_penalty,
                stop=STOP_TOKENS,
                stream=False,
            )

            content = _clean_output(result["choices"][0]["text"])
            usage = result.get("usage", {})

            return {
                "id": f"chatcmpl-{uuid.uuid4().hex[:8]}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": model_config.name,
                "choices": [
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": content},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {
                    "prompt_tokens": usage.get("prompt_tokens", 0),
                    "completion_tokens": usage.get("completion_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0),
                },
            }

        except Exception as e:
            logger.error(f"Chat completion failed: {e}")
            raise TranslationException(f"Chat completion failed: {e}")

    async def chat_completion_stream(self, request: ChatCompletionRequest) -> AsyncGenerator[str, None]:
        """Perform streaming chat completion."""
        try:
            model, model_config = await self.model_manager.get_model(request.model)

            messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]

            temperature = request.temperature if request.temperature is not None else model_config.parameters.temperature
            top_p = request.top_p if request.top_p is not None else model_config.parameters.top_p
            top_k = request.top_k if request.top_k is not None else model_config.parameters.top_k
            max_tokens = request.max_tokens if request.max_tokens is not None else model_config.parameters.max_tokens

            logger.info(f"Streaming chat completion with model {model_config.name}")

            completion_id = f"chatcmpl-{uuid.uuid4().hex[:8]}"
            created = int(time.time())

            full_prompt = _wrap_chatml(messages)
            stream = await asyncio.to_thread(
                model.create_completion,
                prompt=full_prompt,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                max_tokens=max_tokens,
                repeat_penalty=model_config.parameters.repeat_penalty,
                stop=STOP_TOKENS,
                stream=True,
            )

            for chunk in stream:
                text = _clean_output(chunk["choices"][0].get("text", ""))
                if text:
                    chunk_data = {
                        "id": completion_id,
                        "object": "chat.completion.chunk",
                        "created": created,
                        "model": model_config.name,
                        "choices": [
                            {
                                "index": 0,
                                "delta": {"content": text},
                                "finish_reason": None,
                            }
                        ],
                    }
                    yield f"data: {json.dumps(chunk_data)}\n\n"

            final_chunk = {
                "id": completion_id,
                "object": "chat.completion.chunk",
                "created": created,
                "model": model_config.name,
                "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
            }
            yield f"data: {json.dumps(final_chunk)}\n\n"
            yield "data: [DONE]\n\n"

        except Exception as e:
            logger.error(f"Streaming chat completion failed: {e}")
            error_data = json.dumps({"error": str(e)})
            yield f"data: {error_data}\n\n"

    def _validate_languages(self, source_lang: str, target_lang: str, supported_languages: list):
        if source_lang not in supported_languages:
            raise InvalidLanguageException(
                f"Source language '{source_lang}' is not supported. "
                f"Supported languages: {', '.join(supported_languages)}"
            )
        if target_lang not in supported_languages:
            raise InvalidLanguageException(
                f"Target language '{target_lang}' is not supported. "
                f"Supported languages: {', '.join(supported_languages)}"
            )
