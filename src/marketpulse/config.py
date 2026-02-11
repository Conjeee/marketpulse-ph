from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr

class Settings(BaseSettings):
    GEMINI_API_KEY: SecretStr
    SUPABASE_URL: str
    SUPABASE_KEY: SecretStr
    ENVIRONMENT: str = "local"
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()