"""
RAG Service - 检索增强生成服务

核心功能：
1. 多源检索（法条 + 案例 + 司法解释）
2. 重排序（Reranking）提高精度
3. 上下文构建（Context Building）
4. 引用追踪（Citation Tracking）
"""

from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, field
from anthropic import AsyncAnthropic
import logging
import json

from app.core.config import settings
from app.services.knowledge_service import knowledge_service, KnowledgeType, RetrievalResult
from app.services.embedding_service import embedding_service

logger = logging.getLogger(__name__)


@dataclass
class Citation:
    """引用信息"""
    source_type: str  # statute, case, interpretation
    source_id: int
    title: str  # 法律名称+条款号 或 案例标题
    content: str  # 引用内容
    relevance_score: float


@dataclass
class RAGContext:
    """RAG 检索上下文"""
    query: str
    statutes: List[RetrievalResult] = field(default_factory=list)
    cases: List[RetrievalResult] = field(default_factory=list)
    interpretations: List[RetrievalResult] = field(default_factory=list)
    citations: List[Citation] = field(default_factory=list)
    context_text: str = ""


class RAGService:
    """RAG 检索增强服务

    流程：
    1. 提取查询关键信息
    2. 多源检索
    3. 重排序
    4. 构建上下文
    5. 追踪引用
    """

    def __init__(self):
        # Claude 客户端（用于重排序和查询理解）
        client_kwargs = {"api_key": settings.ANTHROPIC_API_KEY}
        if settings.ANTHROPIC_BASE_URL:
            client_kwargs["base_url"] = settings.ANTHROPIC_BASE_URL
        self.client = AsyncAnthropic(**client_kwargs)

    async def retrieve(
        self,
        query: str,
        case_content: Optional[str] = None,
        top_k: int = 5,
        include_cases: bool = True,
        include_statutes: bool = True,
        include_interpretations: bool = True
    ) -> RAGContext:
        """执行 RAG 检索

        Args:
            query: 检索查询（通常是案件的关键要素）
            case_content: 原始案例内容（用于提取更多上下文）
            top_k: 每类知识返回数量
            include_cases: 是否包含案例
            include_statutes: 是否包含法条
            include_interpretations: 是否包含司法解释

        Returns:
            RAG 上下文
        """
        context = RAGContext(query=query)

        # 检查服务可用性
        if not await knowledge_service.is_available():
            logger.warning("Knowledge service unavailable, returning empty context")
            return context

        # 1. 扩展查询（基于案例内容提取更精确的检索词）
        enhanced_query = await self._enhance_query(query, case_content)
        logger.info(f"Enhanced query: {enhanced_query}")

        # 2. 多源检索
        knowledge_types = []
        if include_statutes:
            knowledge_types.append(KnowledgeType.STATUTE)
        if include_cases:
            knowledge_types.append(KnowledgeType.CASE)
        if include_interpretations:
            knowledge_types.append(KnowledgeType.INTERPRETATION)

        results = await knowledge_service.search(
            query=enhanced_query,
            knowledge_types=knowledge_types,
            top_k=top_k * 2  # 获取更多用于重排序
        )

        # 3. 按类型分组
        for r in results:
            if r.knowledge_type == KnowledgeType.STATUTE:
                context.statutes.append(r)
            elif r.knowledge_type == KnowledgeType.CASE:
                context.cases.append(r)
            elif r.knowledge_type == KnowledgeType.INTERPRETATION:
                context.interpretations.append(r)

        # 4. 重排序（如果有足够的结果）
        if len(context.statutes) > top_k:
            context.statutes = await self._rerank(query, context.statutes, top_k)
        else:
            context.statutes = context.statutes[:top_k]

        if len(context.cases) > top_k:
            context.cases = await self._rerank(query, context.cases, top_k)
        else:
            context.cases = context.cases[:top_k]

        # 5. 构建引用列表
        context.citations = self._build_citations(context)

        # 6. 构建上下文文本
        context.context_text = self._build_context_text(context)

        return context

    async def _enhance_query(self, query: str, case_content: Optional[str]) -> str:
        """使用 AI 增强检索查询

        从案例内容中提取法律关键词，构建更精确的检索查询
        """
        if not case_content:
            return query

        try:
            prompt = f"""从以下法律案例中提取最关键的法律检索词，用于检索相关法条和判例。

案例摘要：
{case_content[:1500]}

原始查询：{query}

请提取 3-5 个最相关的法律关键词，用空格分隔。只返回关键词，不要其他内容。
例如：劳动合同解除 经济补偿 违法辞退"""

            response = await self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=100,
                messages=[{"role": "user", "content": prompt}]
            )

            keywords = response.content[0].text.strip()
            # 合并原始查询和提取的关键词
            enhanced = f"{query} {keywords}"
            return enhanced

        except Exception as e:
            logger.warning(f"Query enhancement failed: {e}")
            return query

    async def _rerank(
        self,
        query: str,
        results: List[RetrievalResult],
        top_k: int
    ) -> List[RetrievalResult]:
        """使用 AI 重排序检索结果

        通过 Claude 评估每个结果与查询的相关性
        """
        if len(results) <= top_k:
            return results

        try:
            # 构建重排序提示
            candidates = []
            for i, r in enumerate(results):
                candidates.append(f"[{i}] {r.content[:300]}...")

            prompt = f"""评估以下法律条文与查询的相关性。

查询：{query}

候选条文：
{chr(10).join(candidates)}

请按相关性从高到低排序，返回序号列表（如：[2, 0, 4, 1, 3]）。
只返回 JSON 数组，不要其他内容。"""

            response = await self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=100,
                messages=[{"role": "user", "content": prompt}]
            )

            text = response.content[0].text.strip()
            # 解析排序结果
            if "[" in text:
                ranking = json.loads(text[text.find("["):text.rfind("]")+1])
                # 按排序重组结果
                reranked = []
                for idx in ranking[:top_k]:
                    if 0 <= idx < len(results):
                        reranked.append(results[idx])
                return reranked

        except Exception as e:
            logger.warning(f"Reranking failed: {e}")

        # 回退：按原始分数排序
        return sorted(results, key=lambda x: x.score, reverse=True)[:top_k]

    def _build_citations(self, context: RAGContext) -> List[Citation]:
        """构建引用列表"""
        citations = []

        # 法条引用
        for r in context.statutes:
            citations.append(Citation(
                source_type="statute",
                source_id=r.id,
                title=f"{r.metadata.get('law_name', '')} {r.metadata.get('article_number', '')}",
                content=r.content[:500],
                relevance_score=r.score
            ))

        # 案例引用
        for r in context.cases:
            citations.append(Citation(
                source_type="case",
                source_id=r.id,
                title=r.metadata.get('title', ''),
                content=r.content[:500],
                relevance_score=r.score
            ))

        # 司法解释引用
        for r in context.interpretations:
            citations.append(Citation(
                source_type="interpretation",
                source_id=r.id,
                title=r.metadata.get('title', ''),
                content=r.content[:500],
                relevance_score=r.score
            ))

        return citations

    def _build_context_text(self, context: RAGContext) -> str:
        """构建注入 LLM 的上下文文本"""
        sections = []

        # 法律条文部分
        if context.statutes:
            statute_texts = []
            for r in context.statutes:
                law_name = r.metadata.get('law_name', '')
                article = r.metadata.get('article_number', '')
                content = r.content
                statute_texts.append(f"【{law_name} {article}】\n{content}")

            sections.append("【相关法律条文】\n" + "\n\n".join(statute_texts))

        # 相似案例部分
        if context.cases:
            case_texts = []
            for r in context.cases:
                title = r.metadata.get('title', '')
                case_number = r.metadata.get('case_number', '')
                preview = r.content[:300]
                case_texts.append(f"【{title}】({case_number})\n{preview}...")

            sections.append("【相似案例参考】\n" + "\n\n".join(case_texts))

        # 司法解释部分
        if context.interpretations:
            interp_texts = []
            for r in context.interpretations:
                title = r.metadata.get('title', '')
                content = r.content[:300]
                interp_texts.append(f"【{title}】\n{content}...")

            sections.append("【相关司法解释】\n" + "\n\n".join(interp_texts))

        return "\n\n".join(sections)

    def format_citations_for_response(self, citations: List[Citation]) -> List[Dict]:
        """格式化引用信息用于 API 响应"""
        return [
            {
                "type": c.source_type,
                "id": c.source_id,
                "title": c.title,
                "content_preview": c.content[:200] + "..." if len(c.content) > 200 else c.content,
                "relevance_score": round(c.relevance_score, 3)
            }
            for c in citations
        ]


# 单例
rag_service = RAGService()
