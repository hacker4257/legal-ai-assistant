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

    # Qdrant 向量数据库
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: Optional[str] = None  # Qdrant Cloud 需要
    QDRANT_COLLECTION: str = "legal_cases"
    EMBEDDING_DIMENSION: int = 1024

    # Voyage AI (用于 embedding，可选)
    VOYAGE_API_KEY: Optional[str] = None

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

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
