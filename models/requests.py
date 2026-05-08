from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Literal


class ChatMessage(BaseModel):
    """Chat message in OpenAI format"""
    role: Literal["system", "user", "assistant"] = Field(..., description="Message role")
    content: str = Field(..., description="Message content")


class ChatCompletionRequest(BaseModel):
    """OpenAI-compatible chat completion request"""
    model: Optional[str] = Field(default=None, description="Model to use")
    messages: List[ChatMessage] = Field(..., description="List of messages")
    temperature: Optional[float] = Field(default=None, ge=0.0, le=2.0, description="Sampling temperature")
    top_p: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Nucleus sampling")
    top_k: Optional[int] = Field(default=None, ge=0, description="Top-K sampling")
    max_tokens: Optional[int] = Field(default=None, ge=1, description="Maximum tokens to generate")
    stream: bool = Field(default=False, description="Enable streaming response")


class TranslateRequest(BaseModel):
    """Translation-specific request"""
    text: str = Field(..., description="Text to translate")
    source_lang: str = Field(..., description="Source language code (e.g., 'en', 'zh')")
    target_lang: str = Field(..., description="Target language code (e.g., 'en', 'zh')")
    model: Optional[str] = Field(default=None, description="Model to use")
    terminology: Optional[Dict[str, str]] = Field(default=None, description="Custom terminology mapping")
    context: Optional[str] = Field(default=None, description="Additional context for translation")
    preserve_format: bool = Field(default=False, description="Preserve text formatting")
    stream: bool = Field(default=False, description="Enable streaming response")
