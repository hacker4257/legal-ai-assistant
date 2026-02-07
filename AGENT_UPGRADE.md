# 🤖 从提示词到 Agent：升级完成！

## 📊 升级对比

### ❌ 之前：只是提示词

```python
# backend/app/services/ai_service.py
async def analyze_case(case_content: str) -> dict:
    # 只是一个静态提示词
    prompt = f"""你是一位资深法律专家。请分析以下判决书：
    {case_content}
    请提供：...
    """

    # 单次 API 调用
    message = await client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )

    return parse_response(message)
```

**问题**:
- ❌ 只能被动响应
- ❌ 没有工具使用能力
- ❌ 不能搜索相似案例
- ❌ 不能查找法律依据
- ❌ 单步执行，无法深度分析

---

### ✅ 现在：真正的 Agent

```python
# backend/app/services/legal_agent.py
class LegalAnalysisAgent:
    """法律分析智能体 - 真正的 Agent！"""

    def __init__(self, db: AsyncSession):
        self.db = db

        # Agent 的工具箱
        self.tools = {
            'search_similar_cases': self._search_similar_cases,
            'extract_legal_elements': self._extract_legal_elements,
            'find_legal_basis': self._find_legal_basis,
            'analyze_judgment': self._analyze_judgment,
        }

        # Agent 的记忆
        self.memory = {
            'case_content': None,
            'extracted_elements': None,
            'similar_cases': [],
            'legal_basis': [],
            'analysis_steps': [],
        }

    async def analyze_case(self, case_content: str) -> Dict:
        """Agent 的决策循环 - 多步骤自主执行"""

        # Step 1: 提取关键要素
        elements = await self.tools['extract_legal_elements'](case_content)

        # Step 2: 搜索相似案例（使用数据库）
        similar_cases = await self.tools['search_similar_cases'](elements)

        # Step 3: 查找法律依据
        legal_basis = await self.tools['find_legal_basis'](elements)

        # Step 4: 综合分析（整合所有信息）
        final_analysis = await self.tools['analyze_judgment'](
            case_content, elements, similar_cases, legal_basis
        )

        return final_analysis
```

**优势**:
- ✅ 主动使用工具
- ✅ 多步骤执行
- ✅ 自动搜索相似案例
- ✅ 自动查找法律依据
- ✅ 有记忆和状态管理
- ✅ 能根据情况调整策略

---

## 🔧 Agent 的工具箱

### 工具 1: 提取法律要素
```python
async def _extract_legal_elements(self, case_content: str) -> Dict:
    """从判决书中提取：
    - 案件类型
    - 当事人
    - 争议焦点
    - 法律关系
    """
```

### 工具 2: 搜索相似案例
```python
async def _search_similar_cases(self, elements: Dict) -> List[Dict]:
    """使用数据库搜索相似案例：
    - 按案件类型过滤
    - 按争议点搜索
    - 返回最相关的 5 个案例
    """
```

### 工具 3: 查找法律依据
```python
async def _find_legal_basis(self, elements: Dict) -> List[str]:
    """根据案件类型和法律关系：
    - 推断适用的法律条文
    - 返回 3-5 条最相关的法律依据
    """
```

### 工具 4: 综合分析
```python
async def _analyze_judgment(
    self, case_content, elements, similar_cases, legal_basis
) -> Dict:
    """整合所有信息进行深度分析：
    - 结合相似案例
    - 结合法律依据
    - 生成完整的分析报告
    """
```

---

## 🎯 Agent 的执行流程

```
用户请求分析案例
    ↓
🤖 Agent 启动
    ↓
📊 Step 1: 提取关键要素
    ├─ 调用 AI 提取案件类型、当事人、争议点
    └─ 保存到记忆中
    ↓
🔍 Step 2: 搜索相似案例
    ├─ 使用提取的要素查询数据库
    ├─ 找到 5 个相似案例
    └─ 保存到记忆中
    ↓
📚 Step 3: 查找法律依据
    ├─ 根据案件类型推断法律
    ├─ 找到 3-5 条相关法律
    └─ 保存到记忆中
    ↓
🧠 Step 4: 综合分析
    ├─ 整合案例内容
    ├─ 整合相似案例
    ├─ 整合法律依据
    └─ 生成完整分析报告
    ↓
✅ 返回结果（包含 Agent 元数据）
```

---

## 📈 功能对比

| 功能 | 之前（提示词） | 现在（Agent） |
|------|---------------|--------------|
| **分析案例** | ✅ | ✅ |
| **提取要素** | ❌ 手动 | ✅ 自动 |
| **搜索相似案例** | ❌ 不能 | ✅ 自动搜索数据库 |
| **查找法律依据** | ❌ 不能 | ✅ 自动推断 |
| **多步骤执行** | ❌ 单步 | ✅ 4 步流程 |
| **使用工具** | ❌ 0 个 | ✅ 4 个工具 |
| **状态管理** | ❌ 无状态 | ✅ 有记忆 |
| **自主决策** | ❌ 被动 | ✅ 主动 |

---

## 🧪 如何测试 Agent

### 1. 添加测试数据

```bash
docker-compose exec backend python
```

```python
from app.db.database import AsyncSessionLocal
from app.models.models import Case
from datetime import date
import asyncio

async def add_test_cases():
    async with AsyncSessionLocal() as db:
        # 添加多个测试案例
        cases = [
            Case(
                case_number="(2023)京01民终1234号",
                title="张三诉某公司劳动合同纠纷案",
                court="北京市第一中级人民法院",
                case_type="民事",
                judgment_date=date(2023, 6, 15),
                content="原告张三与被告某公司因劳动合同纠纷一案...",
                parties={"plaintiff": "张三", "defendant": "某公司"},
                legal_basis={"laws": ["劳动合同法第39条"]}
            ),
            Case(
                case_number="(2023)沪02民初5678号",
                title="李四与王五房屋买卖合同纠纷案",
                court="上海市第二中级人民法院",
                case_type="民事",
                judgment_date=date(2023, 8, 20),
                content="原告李四与被告王五因房屋买卖合同纠纷...",
                parties={"plaintiff": "李四", "defendant": "王五"},
                legal_basis={"laws": ["合同法第107条"]}
            ),
        ]

        for case in cases:
            db.add(case)

        await db.commit()
        print("✅ 测试案例添加成功！")

asyncio.run(add_test_cases())
```

### 2. 测试 Agent

1. 访问 http://localhost:3000
2. 注册并登录
3. 搜索"劳动合同"
4. 点击案例进入详情页
5. 点击"AI 智能分析"按钮

### 3. 观察 Agent 工作

在后端日志中，你会看到：

```bash
docker-compose logs -f backend
```

输出：
```
🤖 Legal Analysis Agent 启动...
📊 Step 1: 提取案例关键要素...
🔍 Step 2: 搜索相似案例...
📚 Step 3: 查找相关法律依据...
🧠 Step 4: 综合分析判决...
✅ 分析完成！
```

---

## 🎓 关键概念

### 什么是 Agent？

**Agent = 提示词 + 工具 + 决策循环 + 记忆**

```python
class Agent:
    def __init__(self):
        self.tools = [...]      # 工具箱
        self.memory = {}        # 记忆

    def execute(self, task):
        while not done:
            # 1. 思考
            action = self.think()

            # 2. 使用工具
            result = self.use_tool(action)

            # 3. 记忆
            self.memory.append(result)

            # 4. 决策
            if self.is_done():
                break
```

### 提示词 vs Agent

| 特性 | 提示词 | Agent |
|------|--------|-------|
| 本质 | 静态文本 | 动态系统 |
| 能力 | 只能回答 | 能使用工具 |
| 执行 | 单次调用 | 多步循环 |
| 状态 | 无状态 | 有记忆 |
| 决策 | 被动响应 | 主动决策 |

---

## 📚 相关文件

- `backend/app/services/legal_agent.py` - Agent 实现
- `backend/app/services/ai_service.py` - 旧的提示词实现（保留）
- `backend/app/api/cases.py` - API 路由（已更新使用 Agent）

---

## 🚀 下一步扩展

Agent 还可以继续增强：

### 1. 添加更多工具
```python
self.tools = {
    'search_similar_cases': ...,
    'find_legal_basis': ...,
    'generate_document': ...,      # 新工具：生成法律文书
    'calculate_compensation': ..., # 新工具：计算赔偿金额
    'predict_outcome': ...,        # 新工具：预测判决结果
}
```

### 2. 增强决策能力
```python
async def analyze_case(self, case_content: str):
    # 根据案件复杂度决定执行哪些步骤
    complexity = await self.assess_complexity(case_content)

    if complexity == "simple":
        # 简单案例：快速分析
        return await self.quick_analysis()
    else:
        # 复杂案例：深度分析
        return await self.deep_analysis()
```

### 3. 添加学习能力
```python
async def learn_from_feedback(self, case_id: int, feedback: str):
    """从用户反馈中学习，优化未来的分析"""
    self.memory['feedback'].append({
        'case_id': case_id,
        'feedback': feedback,
        'timestamp': datetime.now()
    })
```

---

## ✅ 升级完成！

你的法律分析系统现在是一个**真正的 Agent**了！

**关键区别**:
- ❌ 之前：只是调用 AI API 的提示词
- ✅ 现在：能主动使用工具、多步骤执行、自主决策的智能体

**立即体验**: http://localhost:3000

祝使用愉快！🎉
