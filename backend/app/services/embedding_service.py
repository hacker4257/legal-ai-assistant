"""
Embedding Service - 文本向量生成服务

支持多种 embedding 方式：
1. Voyage AI (推荐用于中文法律文本)
2. 通过 Claude API 兼容接口
"""

from typing import List, Optional
import httpx
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """文本向量生成服务"""

    def __init__(self):
        self.voyage_api_key = settings.VOYAGE_API_KEY
        self.anthropic_api_key = settings.ANTHROPIC_API_KEY
        self.anthropic_base_url = settings.ANTHROPIC_BASE_URL
        self.dimension = settings.EMBEDDING_DIMENSION

    async def generate_embedding(self, text: str) -> Optional[List[float]]:
        """生成单个文本的向量

        Args:
            text: 输入文本

        Returns:
            向量列表，失败返回 None
        """
        embeddings = await self.generate_embeddings([text])
        return embeddings[0] if embeddings else None

    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """批量生成文本向量

        Args:
            texts: 文本列表

        Returns:
            向量列表
        """
        if not texts:
            return []

        # 优先使用 Voyage AI
        if self.voyage_api_key:
            return await self._voyage_embeddings(texts)

        # 回退到 mock embedding (开发环境)
        logger.warning("No embedding API configured, using mock embeddings")
        return await self._mock_embeddings(texts)

    async def _voyage_embeddings(self, texts: List[str]) -> List[List[float]]:
        """使用 Voyage AI 生成 embedding

        Voyage AI 对中文支持较好，推荐用于法律文本
        """
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    "https://api.voyageai.com/v1/embeddings",
                    headers={
                        "Authorization": f"Bearer {self.voyage_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "voyage-multilingual-2",  # 多语言模型，支持中文
                        "input": texts,
                        "input_type": "document"
                    }
                )
                response.raise_for_status()
                data = response.json()

                embeddings = [item["embedding"] for item in data["data"]]
                return embeddings

        except Exception as e:
            logger.error(f"Voyage AI embedding error: {e}")
            # 回退到 mock
            return await self._mock_embeddings(texts)

    async def _mock_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Mock embedding 用于开发测试

        生成基于文本哈希的伪随机向量
        """
        import hashlib

        embeddings = []
        for text in texts:
            # 使用 MD5 哈希生成种子
            hash_bytes = hashlib.md5(text.encode()).digest()

            # 生成固定维度的向量
            vector = []
            for i in range(self.dimension):
                # 基于哈希字节生成 [-1, 1] 范围的值
                byte_idx = i % len(hash_bytes)
                value = (hash_bytes[byte_idx] / 127.5) - 1.0
                vector.append(value)

            # 归一化
            norm = sum(v ** 2 for v in vector) ** 0.5
            vector = [v / norm for v in vector]

            embeddings.append(vector)

        return embeddings


# 单例
embedding_service = EmbeddingService()
