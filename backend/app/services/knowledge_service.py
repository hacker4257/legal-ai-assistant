"""
Knowledge Service - 法律知识库统一管理服务

管理多个 Qdrant Collection：
- legal_cases: 案例库
- legal_statutes: 法律条文库
- judicial_interpretations: 司法解释库

提供统一的知识检索接口
"""

from typing import List, Dict, Optional, Any
from enum import Enum
from dataclasses import dataclass
from qdrant_client import QdrantClient
from qdrant_client.http import models
import logging

from app.core.config import settings
from app.services.embedding_service import embedding_service

logger = logging.getLogger(__name__)


class KnowledgeType(Enum):
    """知识类型枚举"""
    CASE = "legal_cases"  # 案例
    STATUTE = "legal_statutes"  # 法律条文
    INTERPRETATION = "judicial_interpretations"  # 司法解释


@dataclass
class RetrievalResult:
    """检索结果"""
    id: int
    score: float
    knowledge_type: KnowledgeType
    content: str
    metadata: Dict[str, Any]


class KnowledgeService:
    """法律知识库服务

    统一管理法条、案例、司法解释三大知识库
    """

    # Collection 配置
    COLLECTIONS = {
        KnowledgeType.CASE: {
            "name": "legal_cases",
            "payload_fields": ["case_id", "title", "case_type", "court", "case_number", "content"]
        },
        KnowledgeType.STATUTE: {
            "name": "legal_statutes",
            "payload_fields": ["statute_id", "law_name", "law_category", "article_number", "chapter", "content", "keywords"]
        },
        KnowledgeType.INTERPRETATION: {
            "name": "judicial_interpretations",
            "payload_fields": ["interpretation_id", "title", "issuing_authority", "document_number", "category", "content"]
        }
    }

    def __init__(self):
        self._client: Optional[QdrantClient] = None
        self._initialized_collections: set = set()

    async def _get_client(self) -> QdrantClient:
        """获取 Qdrant 客户端"""
        if self._client is None:
            if settings.QDRANT_API_KEY:
                self._client = QdrantClient(
                    url=settings.QDRANT_URL,
                    api_key=settings.QDRANT_API_KEY
                )
            else:
                self._client = QdrantClient(url=settings.QDRANT_URL)
        return self._client

    async def ensure_collection(self, knowledge_type: KnowledgeType) -> bool:
        """确保 Collection 存在

        Args:
            knowledge_type: 知识类型

        Returns:
            是否成功
        """
        collection_name = self.COLLECTIONS[knowledge_type]["name"]

        if collection_name in self._initialized_collections:
            return True

        try:
            client = await self._get_client()
            collections = client.get_collections().collections
            exists = any(c.name == collection_name for c in collections)

            if not exists:
                # 创建 Collection
                client.create_collection(
                    collection_name=collection_name,
                    vectors_config=models.VectorParams(
                        size=settings.EMBEDDING_DIMENSION,
                        distance=models.Distance.COSINE
                    )
                )

                # 创建全文搜索索引
                client.create_payload_index(
                    collection_name=collection_name,
                    field_name="content",
                    field_schema=models.TextIndexParams(
                        type="text",
                        tokenizer=models.TokenizerType.MULTILINGUAL,
                        min_token_len=2,
                        max_token_len=20
                    )
                )

                logger.info(f"Created collection: {collection_name}")

            self._initialized_collections.add(collection_name)
            return True

        except Exception as e:
            logger.error(f"Failed to ensure collection {collection_name}: {e}")
            return False

    async def search(
        self,
        query: str,
        knowledge_types: List[KnowledgeType],
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[RetrievalResult]:
        """多源知识检索

        Args:
            query: 查询文本
            knowledge_types: 要搜索的知识类型列表
            top_k: 每个类型返回的数量
            filters: 过滤条件

        Returns:
            检索结果列表
        """
        # 生成查询向量
        query_embedding = await embedding_service.generate_embedding(query)
        if not query_embedding:
            logger.error("Failed to generate query embedding")
            return []

        all_results: List[RetrievalResult] = []
        client = await self._get_client()

        for knowledge_type in knowledge_types:
            await self.ensure_collection(knowledge_type)
            collection_name = self.COLLECTIONS[knowledge_type]["name"]

            try:
                # 构建过滤条件
                filter_conditions = None
                if filters:
                    conditions = []
                    for key, value in filters.items():
                        if isinstance(value, list):
                            conditions.append(
                                models.FieldCondition(
                                    key=key,
                                    match=models.MatchAny(any=value)
                                )
                            )
                        else:
                            conditions.append(
                                models.FieldCondition(
                                    key=key,
                                    match=models.MatchValue(value=value)
                                )
                            )
                    if conditions:
                        filter_conditions = models.Filter(must=conditions)

                # 执行搜索
                results = client.search(
                    collection_name=collection_name,
                    query_vector=query_embedding,
                    query_filter=filter_conditions,
                    limit=top_k,
                    with_payload=True
                )

                # 转换结果
                for r in results:
                    all_results.append(RetrievalResult(
                        id=r.id,
                        score=r.score,
                        knowledge_type=knowledge_type,
                        content=r.payload.get("content", ""),
                        metadata=r.payload
                    ))

            except Exception as e:
                logger.error(f"Search failed for {collection_name}: {e}")
                continue

        # 按分数排序
        all_results.sort(key=lambda x: x.score, reverse=True)
        return all_results

    async def search_statutes(
        self,
        query: str,
        top_k: int = 5,
        law_category: Optional[str] = None,
        law_name: Optional[str] = None
    ) -> List[RetrievalResult]:
        """专门检索法律条文

        Args:
            query: 查询文本
            top_k: 返回数量
            law_category: 法律类别过滤（民法、刑法、劳动法等）
            law_name: 法律名称过滤

        Returns:
            法条检索结果
        """
        filters = {}
        if law_category:
            filters["law_category"] = law_category
        if law_name:
            filters["law_name"] = law_name

        return await self.search(
            query=query,
            knowledge_types=[KnowledgeType.STATUTE],
            top_k=top_k,
            filters=filters if filters else None
        )

    async def search_cases(
        self,
        query: str,
        top_k: int = 5,
        case_type: Optional[str] = None
    ) -> List[RetrievalResult]:
        """专门检索案例

        Args:
            query: 查询文本
            top_k: 返回数量
            case_type: 案件类型过滤

        Returns:
            案例检索结果
        """
        filters = {}
        if case_type:
            filters["case_type"] = case_type

        return await self.search(
            query=query,
            knowledge_types=[KnowledgeType.CASE],
            top_k=top_k,
            filters=filters if filters else None
        )

    async def multi_source_search(
        self,
        query: str,
        top_k_per_source: int = 3
    ) -> Dict[str, List[RetrievalResult]]:
        """多源检索（同时搜索法条、案例、司法解释）

        Args:
            query: 查询文本
            top_k_per_source: 每个源返回的数量

        Returns:
            按类型分组的检索结果
        """
        results = {
            "statutes": [],
            "cases": [],
            "interpretations": []
        }

        # 并行搜索三个源
        all_types = [KnowledgeType.STATUTE, KnowledgeType.CASE, KnowledgeType.INTERPRETATION]

        for knowledge_type in all_types:
            try:
                type_results = await self.search(
                    query=query,
                    knowledge_types=[knowledge_type],
                    top_k=top_k_per_source
                )

                if knowledge_type == KnowledgeType.STATUTE:
                    results["statutes"] = type_results
                elif knowledge_type == KnowledgeType.CASE:
                    results["cases"] = type_results
                elif knowledge_type == KnowledgeType.INTERPRETATION:
                    results["interpretations"] = type_results
            except Exception as e:
                logger.warning(f"Failed to search {knowledge_type.value}: {e}")

        return results

    async def get_collection_stats(self) -> Dict[str, Any]:
        """获取所有 Collection 的统计信息"""
        stats = {}
        client = await self._get_client()

        for knowledge_type, config in self.COLLECTIONS.items():
            collection_name = config["name"]
            try:
                info = client.get_collection(collection_name)
                stats[collection_name] = {
                    "vectors_count": info.vectors_count,
                    "points_count": info.points_count,
                    "status": info.status.value
                }
            except Exception:
                stats[collection_name] = {"status": "not_found"}

        return stats

    async def is_available(self) -> bool:
        """检查服务是否可用"""
        try:
            client = await self._get_client()
            client.get_collections()
            return True
        except Exception:
            return False


# 单例
knowledge_service = KnowledgeService()
