from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "PET"
    APP_VERSION: str = "0.1.0"
    CORS_ORIGINS: str = "*"

    DATABASE_URL: str = "sqlite+aiosqlite:///./pet_dev.db"

    UPLOAD_DIR: Path = Path("uploads")

    OPENAI_API_KEY: str = ""
    GOOGLE_API_KEY: str = ""
    OLLAMA_API_KEY: str = ""
    OLLAMA_BASE_URL: str = ""
    OPENROUTER_API_KEY: str = ""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
