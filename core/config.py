from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # API Configuration
    api_keys: str = "test_key_1,test_key_2,test_key_3"
    default_model: str = "hy-mt-general"
    fallback_model: str = "hy-mt-general"

    # Rate Limiting
    rate_limit_requests_per_minute: int = 60

    # Model Storage
    model_storage_path: str = "./storage/models"
    models_config_path: str = "./models.yaml"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1

    # Logging
    log_level: str = "INFO"

    @property
    def api_keys_list(self) -> List[str]:
        """Parse API keys from comma-separated string"""
        return [key.strip() for key in self.api_keys.split(",") if key.strip()]


# Global settings instance
settings = Settings()
