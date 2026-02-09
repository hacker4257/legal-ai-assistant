"""
Vector Service - Qdrant 向量数据库服务

提供案例向量的存储、检索和混合搜索功能
"""

from typing import List, Dict, Optional, Any
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.exceptions import UnexpectedResponse
import logging
from app.core.config import settings
from app.services.embedding_service import embedding_service

logger = logging.getLogger(__name__)


class VectorService:
    """Qdrant 向量数据库服务"""

    def __init__(self):
        self.client: Optional[QdrantClient] = None
        self.collection_name = settings.QDRANT_COLLECTION
        self.dimension = settings.EMBEDDING_DIMENSION
        self._initialized = False

    async def _get_client(self) -> QdrantClient:
        """获取 Qdrant 客户端（懒加载）

        支持本地 Qdrant 和 Qdrant Cloud
        """
        if self.client is None:
            try:
                # Qdrant Cloud 需要 API Key
                if settings.QDRANT_API_KEY:
                    self.client = QdrantClient(
                        url=settings.QDRANT_URL,
                        api_key=settings.QDRANT_API_KEY
                    )
                    logger.info(f"Connected to Qdrant Cloud at {settings.QDRANT_URL}")
                else:
                    # 本地 Qdrant（Docker）
                    self.client = QdrantClient(url=settings.QDRANT_URL)
                    logger.info(f"Connected to local Qdrant at {settings.QDRANT_URL}")
            except Exception as e:
                logger.error(f"Failed to connect to Qdrant: {e}")
                raise
        return self.client

    async def init_collection(self) -> bool:
        """初始化 Qdrant collection

        Returns:
            是否初始化成功
        """
        try:
            client = await self._get_client()

            # 检查 collection 是否存在
            collections = client.get_collections().collections
            exists = any(c.name == self.collection_name for c in collections)

            if not exists:
                # 创建 collection
                client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=self.dimension,
                        distance=models.Distance.COSINE
                    )
                )

                # 创建全文搜索索引（用于混合搜索）
                client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name="content",
                    field_schema=models.TextIndexParams(
                        type="text",
                        tokenizer=models.TokenizerType.MULTILINGUAL,
                        min_token_len=2,
                        max_token_len=20
                    )
                )

                # 创建过滤索引
                client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name="case_type",
                    field_schema=models.PayloadSchemaType.KEYWORD
                )

                logger.info(f"Created collection: {self.collection_name}")
            else:
                logger.info(f"Collection {self.collection_name} already exists")

            self._initialized = True
            return True

        except Exception as e:
            logger.error(f"Failed to initialize collection: {e}")
            return False

    async def upsert_case(
        self,
        case_id: int,
        title: str,
        content: str,
        case_type: Optional[str] = None,
        court: Optional[str] = None,
        case_number: Optional[str] = None
    ) -> bool:
        """添加或更新案例向量

        Args:
            case_id: 案例 ID（数据库主键）
            title: 案例标题
            content: 案例内容
            case_type: 案件类型
            court: 法院
            case_number: 案号

        Returns:
            是否成功
        """
        try:
            client = await self._get_client()

            # 确保 collection 已初始化
            if not self._initialized:
                await self.init_collection()

            # 生成文本向量（标题 + 内容摘要）
            text_for_embedding = f"{title}\n\n{content[:2000]}"
            embedding = await embedding_service.generate_embedding(text_for_embedding)

            if embedding is None:
                logger.error(f"Failed to generate embedding for case {case_id}")
                return False

            # 存储到 Qdrant
            client.upsert(
                collection_name=self.collection_name,
                points=[
                    models.PointStruct(
                        id=case_id,
                        vector=embedding,
                        payload={
                            "case_id": case_id,
                            "title": title,
                            "content": content[:5000],  # 存储部分内容用于全文搜索
                            "case_type": case_type or "",
                            "court": court or "",
                            "case_number": case_number or ""
                        }
                    )
                ]
            )

            logger.info(f"Upserted case {case_id} to vector database")
            return True

        except Exception as e:
            logger.error(f"Failed to upsert case {case_id}: {e}")
            return False

    async def delete_case(self, case_id: int) -> bool:
        """删除案例向量

        Args:
            case_id: 案例 ID

        Returns:
            是否成功
        """
        try:
            client = await self._get_client()
            client.delete(
                collection_name=self.collection_name,
                points_selector=models.PointIdsList(points=[case_id])
            )
            logger.info(f"Deleted case {case_id} from vector database")
            return True
        except Exception as e:
            logger.error(f"Failed to delete case {case_id}: {e}")
            return False

    async def search_similar(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict]:
        """语义搜索相似案例

        Args:
            query: 搜索查询
            top_k: 返回数量
            filters: 过滤条件 {"case_type": "民事"}

        Returns:
            相似案例列表 [{"id": 1, "score": 0.95, "title": "...", ...}]
        """
        try:
            client = await self._get_client()

            # 确保 collection 已初始化
            if not self._initialized:
                await self.init_collection()

            # 生成查询向量
            query_embedding = await embedding_service.generate_embedding(query)
            if query_embedding is None:
                logger.error("Failed to generate query embedding")
                return []

            # 构建过滤条件
            filter_conditions = None
            if filters:
                conditions = []
                if filters.get("case_type"):
                    conditions.append(
                        models.FieldCondition(
                            key="case_type",
                            match=models.MatchValue(value=filters["case_type"])
                        )
                    )
                if filters.get("court"):
                    conditions.append(
                        models.FieldCondition(
                            key="court",
                            match=models.MatchText(text=filters["court"])
                        )
                    )
                if conditions:
                    filter_conditions = models.Filter(must=conditions)

            # 执行搜索
            results = client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                query_filter=filter_conditions,
                limit=top_k,
                with_payload=True
            )

            # 格式化结果
            return [
                {
                    "id": result.id,
                    "score": result.score,
                    "title": result.payload.get("title", ""),
                    "case_type": result.payload.get("case_type", ""),
                    "court": result.payload.get("court", ""),
                    "case_number": result.payload.get("case_number", ""),
                    "content_preview": result.payload.get("content", "")[:200] + "..."
                }
                for result in results
            ]

        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []

    async def hybrid_search(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        semantic_weight: float = 0.7
    ) -> List[Dict]:
        """混合搜索（语义 + 关键词）

        Args:
            query: 搜索查询
            top_k: 返回数量
            filters: 过滤条件
            semantic_weight: 语义搜索权重 (0-1)，默认 0.7

        Returns:
            混合搜索结果列表
        """
        try:
            client = await self._get_client()

            # 确保 collection 已初始化
            if not self._initialized:
                await self.init_collection()

            # 生成查询向量
            query_embedding = await embedding_service.generate_embedding(query)
            if query_embedding is None:
                logger.error("Failed to generate query embedding")
                return []

            # 构建过滤条件
            filter_conditions = None
            if filters:
                conditions = []
                if filters.get("case_type"):
                    conditions.append(
                        models.FieldCondition(
                            key="case_type",
                            match=models.MatchValue(value=filters["case_type"])
                        )
                    )
                if conditions:
                    filter_conditions = models.Filter(must=conditions)

            # 使用 Qdrant 的混合搜索（需要 Qdrant >= 1.4）
            # 语义搜索结果
            semantic_results = client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                query_filter=filter_conditions,
                limit=top_k * 2,  # 获取更多结果用于融合
                with_payload=True
            )

            # 关键词搜索结果
            keyword_results = client.scroll(
                collection_name=self.collection_name,
                scroll_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="content",
                            match=models.MatchText(text=query)
                        )
                    ] + (filter_conditions.must if filter_conditions else [])
                ),
                limit=top_k * 2,
                with_payload=True
            )[0]

            # 结果融合（RRF - Reciprocal Rank Fusion）
            scores = {}
            payloads = {}

            # 语义搜索分数
            for rank, result in enumerate(semantic_results):
                case_id = result.id
                rrf_score = semantic_weight / (rank + 60)  # RRF with k=60
                scores[case_id] = scores.get(case_id, 0) + rrf_score
                payloads[case_id] = result.payload

            # 关键词搜索分数
            keyword_weight = 1 - semantic_weight
            for rank, result in enumerate(keyword_results):
                case_id = result.id
                rrf_score = keyword_weight / (rank + 60)
                scores[case_id] = scores.get(case_id, 0) + rrf_score
                if case_id not in payloads:
                    payloads[case_id] = result.payload

            # 按分数排序
            sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]

            return [
                {
                    "id": case_id,
                    "score": score,
                    "title": payloads[case_id].get("title", ""),
                    "case_type": payloads[case_id].get("case_type", ""),
                    "court": payloads[case_id].get("court", ""),
                    "case_number": payloads[case_id].get("case_number", ""),
                    "content_preview": payloads[case_id].get("content", "")[:200] + "..."
                }
                for case_id, score in sorted_results
            ]

        except Exception as e:
            logger.error(f"Hybrid search failed: {e}")
            # 回退到纯语义搜索
            return await self.search_similar(query, top_k, filters)

    async def is_available(self) -> bool:
        """检查 Qdrant 服务是否可用

        Returns:
            是否可用
        """
        try:
            client = await self._get_client()
            client.get_collections()
            return True
        except Exception as e:
            logger.warning(f"Qdrant service unavailable: {e}")
            return False

    async def get_collection_info(self) -> Optional[Dict]:
        """获取 collection 信息

        Returns:
            collection 统计信息
        """
        try:
            client = await self._get_client()
            info = client.get_collection(self.collection_name)
            return {
                "name": self.collection_name,
                "vectors_count": info.vectors_count,
                "points_count": info.points_count,
                "status": info.status.value
            }
        except Exception as e:
            logger.error(f"Failed to get collection info: {e}")
            return None


# 单例
vector_service = VectorService()
