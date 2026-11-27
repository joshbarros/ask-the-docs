from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    openrouter_api_key: str | None
    openrouter_base: str
    openrouter_model: str
    cors_origins: tuple[str, ...]

    @property
    def llm_enabled(self) -> bool:
        return bool(self.openrouter_api_key)


def get_settings() -> Settings:
    origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,https://ai.josuebarros.com")
    return Settings(
        openrouter_api_key=os.getenv("OPENROUTER_API_KEY"),
        openrouter_base=os.getenv("OPENROUTER_BASE", "https://openrouter.ai/api/v1"),
        openrouter_model=os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-chat"),
        cors_origins=tuple(o.strip() for o in origins.split(",") if o.strip()),
    )


settings = get_settings()
