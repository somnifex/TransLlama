import asyncio
import logging
from typing import Dict, Optional, List
from pathlib import Path
import yaml

from llama_cpp import Llama

from models.config import ModelsConfiguration, ModelConfig
from core.exceptions import ModelNotFoundException, ModelLoadException
from core.config import settings

logger = logging.getLogger(__name__)


class ModelManager:
    """Manages loading, caching, and routing of GGUF models"""

    def __init__(self, config_path: str = None):
        """
        Initialize ModelManager.

        Args:
            config_path: Path to models.yaml configuration file
        """
        self.config_path = config_path or settings.models_config_path
        self.config: Optional[ModelsConfiguration] = None
        self.loaded_models: Dict[str, Llama] = {}
        self.model_locks: Dict[str, asyncio.Lock] = {}
        self._load_config()

    def _load_config(self):
        """Load models configuration from YAML file"""
        try:
            config_file = Path(self.config_path)
            if not config_file.exists():
                raise FileNotFoundError(f"Models config file not found: {self.config_path}")

            with open(config_file, "r", encoding="utf-8") as f:
                config_data = yaml.safe_load(f)

            self.config = ModelsConfiguration(**config_data)
            logger.info(f"Loaded configuration for {len(self.config.models)} models")
        except Exception as e:
            logger.error(f"Failed to load models configuration: {e}")
            raise ModelLoadException(f"Failed to load models configuration: {e}")

    async def load_model(self, model_name: str) -> Llama:
        """
        Load a model by name.

        Args:
            model_name: Name of the model to load

        Returns:
            Loaded Llama model instance

        Raises:
            ModelNotFoundException: If model not found in config
            ModelLoadException: If model fails to load
        """
        # Get model config
        model_config = self.config.get_model_config(model_name)
        if not model_config:
            raise ModelNotFoundException(f"Model '{model_name}' not found in configuration")

        # Create lock for this model if it doesn't exist
        if model_name not in self.model_locks:
            self.model_locks[model_name] = asyncio.Lock()

        # Use lock to prevent concurrent loading of the same model
        async with self.model_locks[model_name]:
            # Check if already loaded
            if model_name in self.loaded_models:
                logger.info(f"Model '{model_name}' already loaded")
                return self.loaded_models[model_name]

            # Load the model
            try:
                logger.info(f"Loading model '{model_name}' from {model_config.path}")

                # Check if model file exists
                model_path = Path(model_config.path)
                if not model_path.exists():
                    raise ModelLoadException(
                        f"Model file not found: {model_config.path}. "
                        f"Please download the model and place it in the correct location."
                    )

                # Load model with llama-cpp-python
                llm = await asyncio.to_thread(
                    Llama,
                    model_path=str(model_path),
                    n_ctx=model_config.parameters.n_ctx,
                    n_gpu_layers=model_config.parameters.n_gpu_layers,
                    use_mmap=True,
                    verbose=False,
                )

                self.loaded_models[model_name] = llm
                logger.info(f"Successfully loaded model '{model_name}'")
                return llm

            except Exception as e:
                logger.error(f"Failed to load model '{model_name}': {e}")
                raise ModelLoadException(f"Failed to load model '{model_name}': {e}")

    async def get_model(self, model_name: Optional[str] = None) -> tuple[Llama, ModelConfig]:
        """
        Get a model instance, loading it if necessary.

        Args:
            model_name: Name of the model (uses default if None)

        Returns:
            Tuple of (model instance, model config)
        """
        # Use default model if none specified
        if not model_name:
            model_name = self.config.default_model

        # Try to load the requested model
        try:
            model = await self.load_model(model_name)
            config = self.config.get_model_config(model_name)
            return model, config
        except (ModelNotFoundException, ModelLoadException) as e:
            # Try fallback model if available
            if model_name != self.config.fallback_model:
                logger.warning(f"Failed to load '{model_name}', trying fallback model")
                model = await self.load_model(self.config.fallback_model)
                config = self.config.get_model_config(self.config.fallback_model)
                return model, config
            else:
                raise e

    def list_models(self) -> List[Dict]:
        """
        List all available models.

        Returns:
            List of model information dictionaries
        """
        models_info = []
        for model_config in self.config.models:
            models_info.append({
                "id": model_config.name,
                "description": model_config.description,
                "supported_languages": model_config.supported_languages,
                "loaded": model_config.name in self.loaded_models,
            })
        return models_info

    async def unload_model(self, model_name: str):
        """
        Unload a model from memory.

        Args:
            model_name: Name of the model to unload
        """
        if model_name in self.loaded_models:
            del self.loaded_models[model_name]
            logger.info(f"Unloaded model '{model_name}'")

    def get_default_model_name(self) -> str:
        """Get the default model name"""
        return self.config.default_model

    def get_loaded_models_count(self) -> int:
        """Get the number of currently loaded models"""
        return len(self.loaded_models)
