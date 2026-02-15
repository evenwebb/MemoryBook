from pydantic import ConfigDict
from pydantic_settings import BaseSettings
from typing import Optional, Tuple
import os


class Settings(BaseSettings):
    model_config = ConfigDict(
        env_file=".env.dev" if os.path.exists(".env.dev") else ".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Database - SQLite for local development
    DATABASE_URL: str = "sqlite:///./memorybook.db"

    # Storage
    UPLOAD_DIR: str = "/app/storage/images"
    THUMBNAIL_DIR: str = "/app/storage/thumbnails"
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS: set = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff", ".pdf", ".heic", ".heif"}

    # OCR
    TESSERACT_CMD: Optional[str] = None
    OCR_LANGUAGES: str = "eng"

    # Image Processing
    THUMBNAIL_SIZE: Tuple[int, int] = (300, 300)
    MAX_IMAGE_SIZE: Tuple[int, int] = (4000, 4000)

    # API
    API_V1_STR: str = "/api/v1"
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173,http://localhost:8088"

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"


settings = Settings()

# Override paths for local development
if os.path.exists(".env.dev"):
    # Use relative paths for local dev
    # Get the project root (one level up from backend/app/core/)
    # __file__ is backend/app/core/config.py, so go up 3 levels to project root
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
    settings.UPLOAD_DIR = os.path.join(project_root, "storage", "images")
    settings.THUMBNAIL_DIR = os.path.join(project_root, "storage", "thumbnails")
    # Use SQLite for local dev - ensure absolute path
    db_path = os.path.join(project_root, "memorybook.db")
    settings.DATABASE_URL = f"sqlite:///{db_path}"
