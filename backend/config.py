import os
from typing import List
from dotenv import load_dotenv

load_dotenv()

def _parse_cors_origins() -> List[str]:
    """
    Parse CORS_ORIGINS env var and always include the full set of local dev
    origins (ports 3000 and 3001 for both localhost and 127.0.0.1) so that
    Next.js can land on any available port without triggering CORS rejections.
    """
    env_val = os.getenv("CORS_ORIGINS", "")
    origins: List[str] = [o.strip() for o in env_val.split(",") if o.strip()]

    # Always allow the local Next.js dev server on ports 3000–3002
    local_defaults = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
    ]
    for origin in local_defaults:
        if origin not in origins:
            origins.append(origin)
    return origins


class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./menu_app.db")
    CORS_ORIGINS: List[str] = _parse_cors_origins()
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    APP_ENV: str = os.getenv("APP_ENV", "development")
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "AI-Powered Personalized Restaurant Menu API"
    VERSION: str = "1.0.0"

settings = Settings()

