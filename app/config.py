import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_flash_model: str = os.getenv("GEMINI_FLASH_MODEL", "gemini-2.0-flash-exp")
    gemini_pro_model: str = os.getenv("GEMINI_PRO_MODEL", "gemini-2.5-pro")
    index_dir: str = os.getenv("INDEX_DIR", "data/indices")
    guides_path: str = os.getenv("GUIDES_PATH", "data/guides.yaml")
    allowed_origins: tuple[str, ...] = tuple(
        o.strip() for o in os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",") if o.strip()
    )
    log_level: str = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()
