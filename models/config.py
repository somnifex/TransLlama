from pydantic import BaseModel, Field
from typing import List, Dict, Optional


class ModelParameters(BaseModel):
    """Model inference parameters"""
    n_ctx: int = Field(default=4096, description="Context window size")
    n_gpu_layers: int = Field(default=0, description="Number of layers to offload to GPU (-1 for all)")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Sampling temperature")
    top_p: float = Field(default=0.6, ge=0.0, le=1.0, description="Nucleus sampling probability")
    top_k: int = Field(default=20, ge=0, description="Top-K sampling")
    repeat_penalty: float = Field(default=1.05, ge=1.0, description="Repetition penalty")
    max_tokens: int = Field(default=2048, ge=1, description="Maximum tokens to generate")


class ModelConfig(BaseModel):
    """Configuration for a single model"""
    name: str = Field(..., description="Model identifier")
    path: str = Field(..., description="Path to GGUF model file")
    description: str = Field(default="", description="Model description")
    parameters: ModelParameters = Field(default_factory=ModelParameters)
    supported_languages: List[str] = Field(default_factory=list, description="Supported language codes")


class ModelsConfiguration(BaseModel):
    """Root configuration for all models"""
    default_model: str = Field(..., description="Default model to use")
    fallback_model: str = Field(..., description="Fallback model if default fails")
    models: List[ModelConfig] = Field(default_factory=list, description="List of available models")

    def get_model_config(self, name: str) -> Optional[ModelConfig]:
        """Get model configuration by name"""
        for model in self.models:
            if model.name == name:
                return model
        return None
