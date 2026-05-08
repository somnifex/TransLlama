import asyncio
import logging
from typing import Optional, Dict, AsyncGenerator
import json

from services.model_manager import ModelManager
from services.prompt_builder import PromptBuilder
from models.requests import TranslateRequest, ChatCompletionRequest
from core.exceptions import TranslationException, InvalidLanguageException

logger = logging.getLogger(__name__)


class TranslationService:
    """Orchestrates translation requests using ModelManager and PromptBuilder"""

    def __init__(self, model_manager: ModelManager):
        """
        Initialize TranslationService.

        Args:
            model_manager: ModelManager instance for loading models
        """
        self.model_manager = model_manager
        self.prompt_builder = PromptBuilder()

    async def translate(self, request: TranslateRequest) -> Dict:
        """
        Perform synchronous translation.

        Args:
            request: Translation request

        Returns:
            Translation result dictionary
        """
        try:
            # Get model
            model, model_config = await self.model_manager.get_model(request.model)

            # Validate languages
            self._validate_languages(
                request.source_lang,
                request.target_lang,
                model_config.supported_languages
            )

            # Build prompt
            prompt = self.prompt_builder.build_translation_prompt(
                source_text=request.text,
                source_lang=request.source_lang,
                target_lang=request.target_lang,
                terminology=request.terminology,
                context=request.context,
                preserve_format=request.preserve_format,
            )

            # Generate translation
            logger.info(f"Translating from {request.source_lang} to {request.target_lang}")

            result = await asyncio.to_thread(
                model.create_chat_completion,
                messages=[{"role": "user", "content": prompt}],
                temperature=model_config.parameters.temperature,
                top_p=model_config.parameters.top_p,
                top_k=model_config.parameters.top_k,
                max_tokens=model_config.parameters.max_tokens,
                repeat_penalty=model_config.parameters.repeat_penalty,
                stream=False,
            )

            translation = result["choices"][0]["message"]["content"].strip()

            return {
                "translation": translation,
                "source_lang": request.source_lang,
                "target_lang": request.target_lang,
                "model": model_config.name,
                "usage": {
                    "characters": len(request.text),
                    "prompt_tokens": result.get("usage", {}).get("prompt_tokens", 0),
                    "completion_tokens": result.get("usage", {}).get("completion_tokens", 0),
                }
            }

        except Exception as e:
            logger.error(f"Translation failed: {e}")
            raise TranslationException(f"Translation failed: {e}")

    async def translate_stream(self, request: TranslateRequest) -> AsyncGenerator[str, None]:
        """
        Perform streaming translation.

        Args:
            request: Translation request

        Yields:
            Translation chunks in SSE format
        """
        try:
            # Get model
            model, model_config = await self.model_manager.get_model(request.model)

            # Validate languages
            self._validate_languages(
                request.source_lang,
                request.target_lang,
                model_config.supported_languages
            )

            # Build prompt
            prompt = self.prompt_builder.build_translation_prompt(
                source_text=request.text,
                source_lang=request.source_lang,
                target_lang=request.target_lang,
                terminology=request.terminology,
                context=request.context,
                preserve_format=request.preserve_format,
            )

            # Stream translation
            logger.info(f"Streaming translation from {request.source_lang} to {request.target_lang}")

            stream = await asyncio.to_thread(
                model.create_chat_completion,
                messages=[{"role": "user", "content": prompt}],
                temperature=model_config.parameters.temperature,
                top_p=model_config.parameters.top_p,
                top_k=model_config.parameters.top_k,
                max_tokens=model_config.parameters.max_tokens,
                repeat_penalty=model_config.parameters.repeat_penalty,
                stream=True,
            )

            for chunk in stream:
                delta = chunk["choices"][0].get("delta", {})
                if "content" in delta:
                    content = delta["content"]
                    # Format as SSE
                    data = json.dumps({"text": content})
                    yield f"data: {data}\n\n"

            # Send done signal
            yield "data: [DONE]\n\n"

        except Exception as e:
            logger.error(f"Streaming translation failed: {e}")
            error_data = json.dumps({"error": str(e)})
            yield f"data: {error_data}\n\n"

    async def chat_completion(self, request: ChatCompletionRequest) -> Dict:
        """
        Perform OpenAI-compatible chat completion.

        Args:
            request: Chat completion request

        Returns:
            Chat completion result dictionary
        """
        try:
            # Get model
            model, model_config = await self.model_manager.get_model(request.model)

            # Prepare messages
            messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]

            # Use request parameters or fall back to model defaults
            temperature = request.temperature if request.temperature is not None else model_config.parameters.temperature
            top_p = request.top_p if request.top_p is not None else model_config.parameters.top_p
            top_k = request.top_k if request.top_k is not None else model_config.parameters.top_k
            max_tokens = request.max_tokens if request.max_tokens is not None else model_config.parameters.max_tokens

            # Generate completion
            logger.info(f"Generating chat completion with model {model_config.name}")

            result = await asyncio.to_thread(
                model.create_chat_completion,
                messages=messages,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                max_tokens=max_tokens,
                repeat_penalty=model_config.parameters.repeat_penalty,
                stream=False,
            )

            return result

        except Exception as e:
            logger.error(f"Chat completion failed: {e}")
            raise TranslationException(f"Chat completion failed: {e}")

    async def chat_completion_stream(self, request: ChatCompletionRequest) -> AsyncGenerator[str, None]:
        """
        Perform streaming chat completion.

        Args:
            request: Chat completion request

        Yields:
            Completion chunks in SSE format
        """
        try:
            # Get model
            model, model_config = await self.model_manager.get_model(request.model)

            # Prepare messages
            messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]

            # Use request parameters or fall back to model defaults
            temperature = request.temperature if request.temperature is not None else model_config.parameters.temperature
            top_p = request.top_p if request.top_p is not None else model_config.parameters.top_p
            top_k = request.top_k if request.top_k is not None else model_config.parameters.top_k
            max_tokens = request.max_tokens if request.max_tokens is not None else model_config.parameters.max_tokens

            # Stream completion
            logger.info(f"Streaming chat completion with model {model_config.name}")

            stream = await asyncio.to_thread(
                model.create_chat_completion,
                messages=messages,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                max_tokens=max_tokens,
                repeat_penalty=model_config.parameters.repeat_penalty,
                stream=True,
            )

            for chunk in stream:
                # Format as SSE
                data = json.dumps(chunk)
                yield f"data: {data}\n\n"

            # Send done signal
            yield "data: [DONE]\n\n"

        except Exception as e:
            logger.error(f"Streaming chat completion failed: {e}")
            error_data = json.dumps({"error": str(e)})
            yield f"data: {error_data}\n\n"

    def _validate_languages(self, source_lang: str, target_lang: str, supported_languages: list):
        """
        Validate that source and target languages are supported.

        Args:
            source_lang: Source language code
            target_lang: Target language code
            supported_languages: List of supported language codes

        Raises:
            InvalidLanguageException: If languages are not supported
        """
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
