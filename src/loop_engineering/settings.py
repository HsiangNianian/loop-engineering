"""Environment-backed runtime configuration."""

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Load OpenAI settings from process variables or a local .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    openai_api_key: SecretStr | None = None
    openai_model: str = "gpt-5.6"

    def require_api_key(self) -> str:
        value = self.openai_api_key.get_secret_value() if self.openai_api_key else ""
        if not value:
            raise ValueError("OPENAI_API_KEY is required unless scripted actions are used")
        return value
