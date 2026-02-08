from pydantic_settings import BaseSettings
from typing import Optional, List
import json


class Settings(BaseSettings):
    """应用配置"""

    # 应用信息
    APP_NAME: str = "Legal AI Assistant"
    DEBUG: bool = True
    VERSION: str = "0.1.0"

    # 数据库
    DATABASE_URL: str

    # Redis (可选)
    REDIS_URL: Optional[str] = None

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Claude API
    ANTHROPIC_API_KEY: str
    ANTHROPIC_BASE_URL: Optional[str] = None

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Parse BACKEND_CORS_ORIGINS if it's a JSON string
        if isinstance(self.BACKEND_CORS_ORIGINS, str):
            try:
                self.BACKEND_CORS_ORIGINS = json.loads(self.BACKEND_CORS_ORIGINS)
            except json.JSONDecodeError:
                # If it's not valid JSON, split by comma
                self.BACKEND_CORS_ORIGINS = [
                    origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(',')
                ]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
