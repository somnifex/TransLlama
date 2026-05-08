from pydantic import BaseModel, Field
from typing import List, Optional, Dict


class Usage(BaseModel):
    """Token usage information"""
    prompt_tokens: int = Field(default=0, description="Number of tokens in the prompt")
    completion_tokens: int = Field(default=0, description="Number of tokens in the completion")
    total_tokens: int = Field(default=0, description="Total number of tokens")


class ChatMessageResponse(BaseModel):
    """Chat message in response"""
    role: str = Field(default="assistant", description="Message role")
    content: str = Field(..., description="Message content")


class ChatCompletionChoice(BaseModel):
    """Single choice in chat completion response"""
    index: int = Field(default=0, description="Choice index")
    message: ChatMessageResponse = Field(..., description="Generated message")
    finish_reason: str = Field(default="stop", description="Reason for completion finish")


class ChatCompletionResponse(BaseModel):
    """OpenAI-compatible chat completion response"""
    id: str = Field(..., description="Unique completion ID")
    object: str = Field(default="chat.completion", description="Object type")
    created: int = Field(..., description="Unix timestamp")
    model: str = Field(..., description="Model used")
    choices: List[ChatCompletionChoice] = Field(..., description="List of completion choices")
    usage: Usage = Field(..., description="Token usage")


class ChatCompletionChunk(BaseModel):
    """Streaming chunk for chat completion"""
    id: str = Field(..., description="Unique completion ID")
    object: str = Field(default="chat.completion.chunk", description="Object type")
    created: int = Field(..., description="Unix timestamp")
    model: str = Field(..., description="Model used")
    choices: List[Dict] = Field(..., description="List of delta choices")


class TranslateResponse(BaseModel):
    """Translation response"""
    translation: str = Field(..., description="Translated text")
    source_lang: str = Field(..., description="Source language")
    target_lang: str = Field(..., description="Target language")
    model: str = Field(..., description="Model used")
    usage: Dict[str, int] = Field(default_factory=dict, description="Usage statistics")


class ModelInfo(BaseModel):
    """Model information"""
    id: str = Field(..., description="Model ID")
    object: str = Field(default="model", description="Object type")
    created: int = Field(..., description="Unix timestamp")
    owned_by: str = Field(default="transllama", description="Owner")
    description: str = Field(default="", description="Model description")
    supported_languages: List[str] = Field(default_factory=list, description="Supported languages")


class ModelsListResponse(BaseModel):
    """List of available models"""
    object: str = Field(default="list", description="Object type")
    data: List[ModelInfo] = Field(..., description="List of models")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Health status")
    models_loaded: int = Field(default=0, description="Number of loaded models")
    uptime_seconds: float = Field(default=0.0, description="Server uptime in seconds")
