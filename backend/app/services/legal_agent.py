"""
Legal Analysis Agent - 法律分析智能体

这是一个真正的 Agent，不仅仅是提示词！
它能主动使用工具、多步骤执行、自主决策。
"""

from typing import Dict, List, Optional
from anthropic import AsyncAnthropic
from app.core.config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from app.models.models import Case
import json


class LegalAnalysisAgent:
    """法律分析智能体

    这是一个真正的 Agent，具备：
    1. 工具使用能力（搜索、查询、分析）
    2. 多步骤执行能力
    3. 自主决策能力
    4. 记忆和状态管理
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
            'search_similar_cases': self._search_similar_cases,
            'extract_legal_elements': self._extract_legal_elements,
            'find_legal_basis': self._find_legal_basis,
            'analyze_judgment': self._analyze_judgment,
        }

        # Agent 的记忆（状态）
        self.memory = {
            'case_content': None,
            'extracted_elements': None,
            'similar_cases': [],
            'legal_basis': [],
            'analysis_steps': [],
        }

    async def analyze_case(self, case_content: str) -> Dict:
        """主分析流程 - Agent 的决策循环

        这是 Agent 的核心：它会自主决定执行哪些步骤
        """
        print("🤖 Legal Analysis Agent 启动...")

        # 保存案例内容到记忆
        self.memory['case_content'] = case_content

        # Step 1: 提取关键要素
        print("📊 Step 1: 提取案例关键要素...")
        elements = await self.tools['extract_legal_elements'](case_content)
        self.memory['extracted_elements'] = elements
        self.memory['analysis_steps'].append("提取关键要素")

        # Step 2: 搜索相似案例（使用提取的要素）
        print("🔍 Step 2: 搜索相似案例...")
        similar_cases = await self.tools['search_similar_cases'](elements)
        self.memory['similar_cases'] = similar_cases
        self.memory['analysis_steps'].append(f"找到 {len(similar_cases)} 个相似案例")

        # Step 3: 查找法律依据
        print("📚 Step 3: 查找相关法律依据...")
        legal_basis = await self.tools['find_legal_basis'](elements)
        self.memory['legal_basis'] = legal_basis
        self.memory['analysis_steps'].append(f"找到 {len(legal_basis)} 条法律依据")

        # Step 4: 综合分析（使用所有收集的信息）
        print("🧠 Step 4: 综合分析判决...")
        final_analysis = await self.tools['analyze_judgment'](
            case_content=case_content,
            elements=elements,
            similar_cases=similar_cases,
            legal_basis=legal_basis
        )

        print("✅ 分析完成！")

        # 返回完整的分析结果
        return {
            **final_analysis,
            'agent_metadata': {
                'steps_executed': self.memory['analysis_steps'],
                'similar_cases_found': len(similar_cases),
                'legal_basis_found': len(legal_basis),
            }
        }

    async def _extract_legal_elements(self, case_content: str) -> Dict:
        """工具 1: 提取案例关键要素"""
        prompt = f"""请从以下判决书中提取关键要素，以 JSON 格式返回：

{case_content[:2000]}  # 只用前2000字提取要素

请提取：
1. 案件类型（民事/刑事/行政）
2. 主要当事人
3. 核心争议点
4. 涉及的法律关系

返回 JSON 格式：
{{
  "case_type": "案件类型",
  "parties": ["当事人1", "当事人2"],
  "dispute_points": ["争议点1", "争议点2"],
  "legal_relations": ["法律关系1"]
}}
"""

        response = await self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )

        try:
            text = response.content[0].text
            # 提取 JSON
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
                "legal_relations": []
            }

    async def _search_similar_cases(self, elements: Dict) -> List[Dict]:
        """工具 2: 搜索相似案例（使用数据库）"""
        case_type = elements.get('case_type', '')
        dispute_points = elements.get('dispute_points', [])

        # 构建搜索查询
        query = select(Case).limit(5)

        # 按案件类型过滤
        if case_type and case_type != "未知":
            query = query.where(Case.case_type.ilike(f"%{case_type}%"))

        # 按争议点搜索
        if dispute_points:
            search_terms = " ".join(dispute_points)
            query = query.where(
                or_(
                    Case.title.ilike(f"%{search_terms}%"),
                    Case.content.ilike(f"%{search_terms}%")
                )
            )

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

    async def _find_legal_basis(self, elements: Dict) -> List[str]:
        """工具 3: 查找相关法律依据

        这里可以：
        1. 调用法律数据库 API
        2. 使用 AI 推断相关法律
        3. 从相似案例中提取

        目前使用 AI 推断
        """
        case_type = elements.get('case_type', '')
        legal_relations = elements.get('legal_relations', [])

        prompt = f"""根据以下信息，列出可能适用的中国法律条文：

案件类型：{case_type}
法律关系：{', '.join(legal_relations)}

请列出 3-5 条最相关的法律依据，格式：
["法律名称 第X条", "法律名称 第Y条", ...]

只返回 JSON 数组，不要其他内容。
"""

        response = await self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )

        try:
            text = response.content[0].text
            if "```json" in text:
                json_str = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                json_str = text.split("```")[1].split("```")[0].strip()
            elif "[" in text:
                json_str = text[text.find("["):text.rfind("]")+1]
            else:
                json_str = text

            return json.loads(json_str)
        except:
            return ["相关法律条文待查询"]

    async def _analyze_judgment(
        self,
        case_content: str,
        elements: Dict,
        similar_cases: List[Dict],
        legal_basis: List[str]
    ) -> Dict:
        """工具 4: 综合分析判决

        这是最终的分析步骤，整合所有之前收集的信息
        同时提供专业版和通俗版两种解读
        """

        # 构建增强的提示词（包含 Agent 收集的所有信息）
        similar_cases_text = "\n".join([
            f"- {case['title']} ({case['case_number']})"
            for case in similar_cases[:3]
        ])

        legal_basis_text = "\n".join([f"- {law}" for law in legal_basis])

        prompt = f"""你是一位资深法律专家。请深度分析以下判决书，并提供两个版本的解读。

【重要】你必须提供两个完全不同的版本：
1. 专业版：给律师看的，使用法律术语
2. 通俗版：给普通老百姓看的，用大白话解释

【判决书内容】
{case_content}

【Agent 已收集的信息】
案件类型：{elements.get('case_type')}
争议焦点：{', '.join(elements.get('dispute_points', []))}

相似案例参考：
{similar_cases_text if similar_cases_text else '暂无'}

相关法律依据：
{legal_basis_text if legal_basis_text else '待查询'}

【分析要求】
请提供两个版本的分析。注意：通俗版必须用完全不同的语言风格！

**专业版（给律师和法律专业人士）：**
- 使用专业法律术语
- 详细的法律分析
- 引用具体法条

**通俗版（给普通人）：**
- 用大白话，像跟朋友聊天一样
- 避免法律术语，或者用括号解释
- 说明"谁赢了"、"为什么"、"结果是什么"
- 用生活化的例子类比

请严格按照以下 JSON 格式返回（不要有任何其他文字）：

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
  "legal_reasoning_plain": "法院为什么这么判？（通俗版，用简单的逻辑解释，比如：因为A做了B，所以法院认为C）",

  "legal_basis": ["《中华人民共和国民法典》第X条：【原文内容】", "《中华人民共和国民法典》第Y条：【原文内容】"],
  "legal_basis_plain": [
    "《中华人民共和国民法典》第X条：【原文内容】\n\n这条说的是XXX：用大白话解释这条法律的意思，比如'这条说的是财产怎么分：夫妻离婚时，婚后挣的钱、买的东西原则上要平分。但法院也会考虑实际情况，比如谁带孩子、谁更需要照顾等，尽量公平合理地分配。'",
    "《中华人民共和国民法典》第Y条：【原文内容】\n\n这条说的是YYY：用大白话解释..."
  ],

  "judgment_result": "裁判结果（专业版）",
  "judgment_result_plain": "最终结果：谁赢了？要赔多少钱？（通俗版，直接说结果）",

  "similar_cases_reference": "相似案例的参考价值",

  "plain_language_tips": "给普通人的建议：从这个案子能学到什么？遇到类似情况该怎么办？"
}}
```

记住：summary_plain、key_elements_plain、legal_reasoning_plain、legal_basis_plain、judgment_result_plain 这些字段必须用完全不同的语言风格，就像你在给一个完全不懂法律的朋友解释一样！

**特别注意 legal_basis_plain 的格式：**
每条法律依据必须包含：
1. 法律条文原文（完整引用）
2. 换行后加上通俗解释，格式为："这条说的是XXX：【大白话解释】"

示例：
```
"《中华人民共和国民法典》第一千零八十七条：离婚时，夫妻的共同财产由双方协议处理；协议不成的，由人民法院根据财产的具体情况，按照照顾子女、女方和无过错方权益的原则判决。

这条说的是财产怎么分：夫妻离婚时，婚后挣的钱、买的东西原则上要平分。但法院也会考虑实际情况，比如谁带孩子、谁更需要照顾等，尽量公平合理地分配。"
```
"""

        response = await self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=8192,  # 增加 token 限制
            messages=[{"role": "user", "content": prompt}]
        )

        try:
            text = response.content[0].text

            # 调试：打印原始响应
            print(f"AI 原始响应长度: {len(text)}")
            print(f"AI 响应前500字符: {text[:500]}")

            # 更强大的 JSON 提取
            if "```json" in text:
                json_str = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                json_str = text.split("```")[1].split("```")[0].strip()
            else:
                # 尝试找到 JSON 对象
                start = text.find('{')
                end = text.rfind('}')
                if start != -1 and end != -1:
                    json_str = text[start:end+1]
                else:
                    json_str = text

            result = json.loads(json_str)

            # 调试：检查关键字段
            print(f"解析成功！字段: {list(result.keys())}")
            print(f"summary_plain 存在: {'summary_plain' in result}")
            if 'summary_plain' in result:
                print(f"summary_plain 内容: {result['summary_plain'][:100]}...")

            # 确保所有必需字段都存在
            if 'summary_plain' not in result or not result['summary_plain']:
                print("⚠️ summary_plain 缺失或为空，使用 summary")
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

            return result
        except Exception as e:
            print(f"JSON 解析失败: {e}")
            print(f"原始文本: {text[:500]}...")
            return {
                "summary": text[:200] if text else "分析失败",
                "summary_plain": "抱歉，AI 返回的格式有问题，无法解析",
                "key_elements": elements,
                "key_elements_plain": {
                    "who": "解析失败",
                    "what_happened": "解析失败",
                    "what_they_want": "解析失败"
                },
                "legal_reasoning": text if text else str(e),
                "legal_reasoning_plain": "抱歉，分析结果解析失败",
                "legal_basis": legal_basis,
                "legal_basis_plain": ["解析失败"],
                "judgment_result": "",
                "judgment_result_plain": "解析失败",
                "similar_cases_reference": f"找到 {len(similar_cases)} 个相似案例",
                "plain_language_tips": ""
            }
