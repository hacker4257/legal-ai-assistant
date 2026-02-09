"""
Legal Analysis Agent - 法律分析智能体 (RAG 增强版)

这是一个真正的 Agent，使用 RAG 技术增强分析能力：
1. 从知识库检索真实法条（非 AI 推断）
2. 检索相似案例作为参考
3. 所有引用可追溯验证
"""

from typing import Dict, List, Optional
from anthropic import AsyncAnthropic
from app.core.config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from app.models.models import Case
from app.services.vector_service import vector_service
from app.services.rag_service import rag_service, RAGContext
from app.services.knowledge_service import knowledge_service, KnowledgeType
import json
import logging

logger = logging.getLogger(__name__)


class LegalAnalysisAgent:
    """法律分析智能体 (RAG 增强版)

    核心改进：
    1. 法条来自真实知识库检索，非 AI 推断
    2. 相似案例使用语义搜索
    3. 所有引用带溯源信息
    4. 分析结果更可靠
    """

    def __init__(self, db: AsyncSession):
        self.db = db

        # 初始化 Claude 客户端
        client_kwargs = {"api_key": settings.ANTHROPIC_API_KEY}
        if settings.ANTHROPIC_BASE_URL:
            client_kwargs["base_url"] = settings.ANTHROPIC_BASE_URL
        self.client = AsyncAnthropic(**client_kwargs)

        # Agent 的工具箱
        self.tools = {
            'extract_legal_elements': self._extract_legal_elements,
            'rag_retrieve': self._rag_retrieve,  # 新增：RAG 检索
            'search_similar_cases': self._search_similar_cases,
            'analyze_judgment': self._analyze_judgment,
        }

        # Agent 的记忆（状态）
        self.memory = {
            'case_content': None,
            'extracted_elements': None,
            'rag_context': None,  # 新增：RAG 上下文
            'similar_cases': [],
            'legal_basis': [],
            'citations': [],  # 新增：引用追踪
            'analysis_steps': [],
        }

    async def analyze_case(self, case_content: str) -> Dict:
        """主分析流程 - RAG 增强版

        流程：
        1. 提取关键要素
        2. RAG 检索（法条 + 案例 + 司法解释）
        3. 综合分析（基于检索结果）
        """
        print("🤖 Legal Analysis Agent (RAG Enhanced) 启动...")

        # 保存案例内容到记忆
        self.memory['case_content'] = case_content

        # Step 1: 提取关键要素
        print("📊 Step 1: 提取案例关键要素...")
        elements = await self.tools['extract_legal_elements'](case_content)
        self.memory['extracted_elements'] = elements
        self.memory['analysis_steps'].append("提取关键要素")

        # Step 2: RAG 检索（核心改进！）
        print("🔍 Step 2: RAG 知识库检索...")
        rag_context = await self.tools['rag_retrieve'](elements, case_content)
        self.memory['rag_context'] = rag_context
        self.memory['citations'] = rag_context.citations if rag_context else []

        # 统计检索结果
        statutes_count = len(rag_context.statutes) if rag_context else 0
        cases_count = len(rag_context.cases) if rag_context else 0
        self.memory['analysis_steps'].append(
            f"RAG 检索: {statutes_count} 条法条, {cases_count} 个案例"
        )
        print(f"   📚 检索到 {statutes_count} 条相关法条")
        print(f"   📁 检索到 {cases_count} 个相似案例")

        # Step 3: 提取法律依据（从 RAG 结果）
        legal_basis = self._extract_legal_basis_from_rag(rag_context)
        self.memory['legal_basis'] = legal_basis

        # Step 4: 提取相似案例（从 RAG 结果）
        similar_cases = self._extract_cases_from_rag(rag_context)
        self.memory['similar_cases'] = similar_cases

        # Step 5: 综合分析（使用 RAG 上下文）
        print("🧠 Step 3: 综合分析判决...")
        final_analysis = await self.tools['analyze_judgment'](
            case_content=case_content,
            elements=elements,
            rag_context=rag_context,
            similar_cases=similar_cases,
            legal_basis=legal_basis
        )

        print("✅ 分析完成！")

        # 返回完整的分析结果（包含引用信息）
        return {
            **final_analysis,
            'citations': [
                {
                    'type': c.source_type,
                    'id': c.source_id,
                    'title': c.title,
                    'relevance_score': round(c.relevance_score, 3)
                }
                for c in self.memory['citations']
            ],
            'agent_metadata': {
                'steps_executed': self.memory['analysis_steps'],
                'similar_cases_found': len(similar_cases),
                'legal_basis_found': len(legal_basis),
                'rag_enabled': True,
                'statutes_retrieved': statutes_count,
            }
        }

    async def _extract_legal_elements(self, case_content: str) -> Dict:
        """工具 1: 提取案例关键要素"""
        prompt = f"""请从以下判决书中提取关键要素，以 JSON 格式返回：

{case_content[:2000]}

请提取：
1. 案件类型（民事/刑事/行政）
2. 主要当事人
3. 核心争议点
4. 涉及的法律关系
5. 关键法律关键词（用于检索法条）

返回 JSON 格式：
{{
  "case_type": "案件类型",
  "parties": ["当事人1", "当事人2"],
  "dispute_points": ["争议点1", "争议点2"],
  "legal_relations": ["法律关系1"],
  "search_keywords": ["关键词1", "关键词2", "关键词3"]
}}
"""

        response = await self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )

        try:
            text = response.content[0].text
            if "```json" in text:
                json_str = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                json_str = text.split("```")[1].split("```")[0].strip()
            else:
                json_str = text

            return json.loads(json_str)
        except:
            return {
                "case_type": "未知",
                "parties": [],
                "dispute_points": [],
                "legal_relations": [],
                "search_keywords": []
            }

    async def _rag_retrieve(self, elements: Dict, case_content: str) -> Optional[RAGContext]:
        """工具 2: RAG 知识库检索

        从法条库、案例库、司法解释库中检索相关内容
        """
        # 构建检索查询
        case_type = elements.get('case_type', '')
        dispute_points = elements.get('dispute_points', [])
        legal_relations = elements.get('legal_relations', [])
        search_keywords = elements.get('search_keywords', [])

        # 组合检索词
        query_parts = [case_type] + dispute_points + legal_relations + search_keywords
        query = ' '.join([p for p in query_parts if p and p != '未知'])

        if not query:
            query = case_content[:500]  # 回退到案例内容

        try:
            # 使用 RAG 服务检索
            rag_context = await rag_service.retrieve(
                query=query,
                case_content=case_content,
                top_k=5,
                include_cases=True,
                include_statutes=True,
                include_interpretations=True
            )
            return rag_context
        except Exception as e:
            logger.error(f"RAG retrieval failed: {e}")
            return RAGContext(query=query)

    def _extract_legal_basis_from_rag(self, rag_context: Optional[RAGContext]) -> List[Dict]:
        """从 RAG 结果中提取法律依据"""
        if not rag_context or not rag_context.statutes:
            return []

        return [
            {
                'id': r.id,
                'law_name': r.metadata.get('law_name', ''),
                'article_number': r.metadata.get('article_number', ''),
                'content': r.content,
                'score': r.score
            }
            for r in rag_context.statutes
        ]

    def _extract_cases_from_rag(self, rag_context: Optional[RAGContext]) -> List[Dict]:
        """从 RAG 结果中提取相似案例"""
        if not rag_context or not rag_context.cases:
            return []

        return [
            {
                'id': r.id,
                'title': r.metadata.get('title', ''),
                'case_number': r.metadata.get('case_number', ''),
                'court': r.metadata.get('court', ''),
                'summary': r.content[:200] + '...',
                'similarity_score': r.score
            }
            for r in rag_context.cases
        ]

    async def _search_similar_cases(self, elements: Dict) -> List[Dict]:
        """工具 3: 搜索相似案例（备用，当 RAG 不可用时）"""
        case_type = elements.get('case_type', '')
        dispute_points = elements.get('dispute_points', [])
        search_text = f"{case_type} {' '.join(dispute_points)}"

        try:
            if await vector_service.is_available():
                filters = {}
                if case_type and case_type != "未知":
                    filters["case_type"] = case_type

                vector_results = await vector_service.search_similar(
                    query=search_text,
                    top_k=5,
                    filters=filters if filters else None
                )

                if vector_results:
                    case_ids = [r["id"] for r in vector_results]
                    query = select(Case).where(Case.id.in_(case_ids))
                    result = await self.db.execute(query)
                    cases_map = {case.id: case for case in result.scalars().all()}

                    return [
                        {
                            'id': r["id"],
                            'title': cases_map[r["id"]].title if r["id"] in cases_map else r["title"],
                            'case_number': cases_map[r["id"]].case_number if r["id"] in cases_map else r["case_number"],
                            'court': cases_map[r["id"]].court if r["id"] in cases_map else r["court"],
                            'summary': (cases_map[r["id"]].content[:200] + "...") if r["id"] in cases_map else r["content_preview"],
                            'similarity_score': r["score"]
                        }
                        for r in vector_results
                        if r["id"] in cases_map
                    ]
        except Exception as e:
            logger.warning(f"Vector search failed: {e}")

        # 回退：关键词搜索
        query = select(Case).limit(5)
        if case_type and case_type != "未知":
            query = query.where(Case.case_type.ilike(f"%{case_type}%"))

        result = await self.db.execute(query)
        cases = result.scalars().all()

        return [
            {
                'id': case.id,
                'title': case.title,
                'case_number': case.case_number,
                'court': case.court,
                'summary': case.content[:200] + "..."
            }
            for case in cases
        ]

    async def _analyze_judgment(
        self,
        case_content: str,
        elements: Dict,
        rag_context: Optional[RAGContext],
        similar_cases: List[Dict],
        legal_basis: List[Dict]
    ) -> Dict:
        """工具 4: 综合分析判决 (RAG 增强版)

        关键改进：使用 RAG 检索的真实法条，而非 AI 推断
        """

        # 构建法条引用文本（来自真实检索）
        if legal_basis:
            legal_basis_text = "\n".join([
                f"【{lb['law_name']} {lb['article_number']}】\n{lb['content']}"
                for lb in legal_basis[:5]
            ])
        else:
            legal_basis_text = "（未检索到相关法条，请基于法律知识分析）"

        # 构建相似案例文本
        similar_cases_text = "\n".join([
            f"- {case['title']} ({case.get('case_number', '')})"
            for case in similar_cases[:3]
        ])

        # RAG 上下文
        rag_context_text = rag_context.context_text if rag_context else ""

        prompt = f"""你是一位资深法律专家。请深度分析以下判决书，并提供两个版本的解读。

【重要】你必须提供两个完全不同的版本：
1. 专业版：给律师看的，使用法律术语
2. 通俗版：给普通老百姓看的，用大白话解释

【判决书内容】
{case_content}

【RAG 检索到的相关知识】
{rag_context_text if rag_context_text else '暂无检索结果'}

【案件要素分析】
案件类型：{elements.get('case_type')}
争议焦点：{', '.join(elements.get('dispute_points', []))}
法律关系：{', '.join(elements.get('legal_relations', []))}

【⚠️ 重要：以下法条来自知识库检索，请优先引用这些真实法条】
{legal_basis_text}

【相似案例参考】
{similar_cases_text if similar_cases_text else '暂无'}

【分析要求】
1. **法律依据必须优先使用上面检索到的真实法条**
2. 如果检索到的法条不够，可以补充其他相关法条，但要标注"（补充）"
3. 提供专业版和通俗版两种解读

请严格按照以下 JSON 格式返回：

```json
{{
  "summary": "案情摘要（专业版，使用法律术语）",
  "summary_plain": "这个案子说的是什么？（通俗版，用大白话，就像给朋友讲故事）",

  "key_elements": {{
    "parties": "当事人信息（专业版）",
    "case_cause": "案由（专业版）",
    "dispute_focus": "争议焦点（专业版）"
  }},

  "key_elements_plain": {{
    "who": "谁告谁？为什么告？（用大白话）",
    "what_happened": "发生了什么事？（讲故事的方式）",
    "what_they_want": "原告想要什么？被告怎么说？（简单明了）"
  }},

  "legal_reasoning": "判决理由分析（专业版，法律术语）",
  "legal_reasoning_plain": "法院为什么这么判？（通俗版，用简单的逻辑解释）",

  "legal_basis": ["《法律名称》第X条：【条文内容】", "..."],
  "legal_basis_plain": [
    "《法律名称》第X条：【条文内容】\\n\\n这条说的是XXX：【大白话解释】",
    "..."
  ],

  "judgment_result": "裁判结果（专业版）",
  "judgment_result_plain": "最终结果：谁赢了？要赔多少钱？（通俗版）",

  "similar_cases_reference": "相似案例的参考价值",

  "plain_language_tips": "给普通人的建议：从这个案子能学到什么？"
}}
```
"""

        response = await self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=8192,
            messages=[{"role": "user", "content": prompt}]
        )

        try:
            text = response.content[0].text
            print(f"AI 原始响应长度: {len(text)}")

            # JSON 提取
            if "```json" in text:
                json_str = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                json_str = text.split("```")[1].split("```")[0].strip()
            else:
                start = text.find('{')
                end = text.rfind('}')
                if start != -1 and end != -1:
                    json_str = text[start:end+1]
                else:
                    json_str = text

            result = json.loads(json_str)

            # 确保所有必需字段都存在
            self._ensure_required_fields(result, elements, legal_basis, similar_cases)

            return result

        except Exception as e:
            logger.error(f"JSON 解析失败: {e}")
            return self._fallback_result(text if 'text' in dir() else str(e), elements, legal_basis, similar_cases)

    def _ensure_required_fields(self, result: Dict, elements: Dict, legal_basis: List, similar_cases: List):
        """确保结果包含所有必需字段"""
        if 'summary_plain' not in result or not result['summary_plain']:
            result['summary_plain'] = result.get('summary', '')
        if 'key_elements_plain' not in result:
            result['key_elements_plain'] = {}
        if 'legal_reasoning_plain' not in result:
            result['legal_reasoning_plain'] = result.get('legal_reasoning', '')
        if 'legal_basis_plain' not in result:
            result['legal_basis_plain'] = result.get('legal_basis', [])
        if 'judgment_result_plain' not in result:
            result['judgment_result_plain'] = result.get('judgment_result', '')
        if 'plain_language_tips' not in result:
            result['plain_language_tips'] = ''

    def _fallback_result(self, text: str, elements: Dict, legal_basis: List, similar_cases: List) -> Dict:
        """解析失败时的回退结果"""
        return {
            "summary": text[:200] if text else "分析失败",
            "summary_plain": "抱歉，AI 返回的格式有问题，无法解析",
            "key_elements": elements,
            "key_elements_plain": {
                "who": "解析失败",
                "what_happened": "解析失败",
                "what_they_want": "解析失败"
            },
            "legal_reasoning": text if text else "解析失败",
            "legal_reasoning_plain": "抱歉，分析结果解析失败",
            "legal_basis": [f"{lb['law_name']} {lb['article_number']}" for lb in legal_basis] if legal_basis else [],
            "legal_basis_plain": ["解析失败"],
            "judgment_result": "",
            "judgment_result_plain": "解析失败",
            "similar_cases_reference": f"找到 {len(similar_cases)} 个相似案例",
            "plain_language_tips": ""
        }
