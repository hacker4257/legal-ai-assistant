# 法律 AI 助手 🤖⚖️

一个基于 Claude AI 的智能法律案例分析系统，提供**双视角解读**（专业版 + 普通人版），让法律判决书人人都能看懂。

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![React](https://img.shields.io/badge/react-18.2-blue.svg)

## ✨ 核心特性

### 🎯 双视角 AI 分析
- **专业视角**：使用法律术语，适合律师和法律专业人士
- **普通人视角**：用大白话解释，让普通人也能看懂判决书
  - 法律条文 + 通俗解释
  - 生活化的建议
  - Markdown 格式渲染

### 🤖 智能 Agent 系统
不是简单的提示词调用，而是真正的 AI Agent：
1. 自动提取案例关键要素
2. 主动搜索相似案例
3. 查找相关法律依据
4. 综合所有信息进行深度分析

### 📚 真实案例 + 教学示例
- ✅ 真实案例来自最高人民法院公报、指导性案例
- ✅ 明确标注数据来源
- ✅ 教学示例用于功能演示

### 🎨 优秀的用户体验
- 响应式设计，支持移动端
- 视角切换流畅，交互友好
- 美观的渐变色按钮和卡片设计

## 技术栈

**后端：**
- Python 3.11
- FastAPI
- PostgreSQL
- SQLAlchemy (异步)
- Redis
- Claude API (Anthropic)

**前端：**
- React 18 + TypeScript
- Ant Design
- Vite
- Zustand (状态管理)
- React Router

**部署：**
- Docker
- Docker Compose

## 快速开始

### 前置要求

- Docker & Docker Compose
- Claude API Key (从 https://console.anthropic.com/ 获取)

### 安装步骤

1. **克隆项目**
```bash
cd legal-ai-assistant
```

2. **配置环境变量**
```bash
# 创建 .env 文件
echo "ANTHROPIC_API_KEY=your-api-key-here" > .env
```

3. **启动服务**
```bash
docker-compose up -d
```

4. **初始化数据库**
```bash
docker-compose exec backend alembic upgrade head
```

5. **访问应用**
- 前端：http://localhost:3000
- 后端 API 文档：http://localhost:8000/docs

## 开发模式

### 后端开发

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的配置

# 运行开发服务器
uvicorn app.main:app --reload
```

### 前端开发

```bash
cd frontend

# 安装依赖
npm install

# 运行开发服务器
npm run dev
```

## API 文档

启动后端后，访问 http://localhost:8000/docs 查看完整的 API 文档。

### 主要端点

**认证：**
- `POST /api/v1/auth/register` - 用户注册
- `POST /api/v1/auth/login` - 用户登录
- `GET /api/v1/auth/me` - 获取当前用户信息

**案例：**
- `POST /api/v1/cases/search` - 搜索案例
- `GET /api/v1/cases/{id}` - 获取案例详情
- `POST /api/v1/cases/{id}/analyze` - AI 分析案例
- `POST /api/v1/cases/` - 创建案例（管理员）

## 项目结构

```
legal-ai-assistant/
├── backend/                 # 后端代码
│   ├── app/
│   │   ├── api/            # API 路由
│   │   ├── core/           # 核心配置
│   │   ├── db/             # 数据库
│   │   ├── models/         # 数据模型
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # 业务逻辑
│   │   └── main.py         # 应用入口
│   ├── alembic/            # 数据库迁移
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/               # 前端代码
│   ├── src/
│   │   ├── api/           # API 客户端
│   │   ├── pages/         # 页面组件
│   │   ├── store/         # 状态管理
│   │   └── App.tsx        # 应用入口
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml      # Docker 编排
└── README.md
```

## 使用说明

### 1. 注册账号

访问 http://localhost:3000/login，点击"注册"标签页，填写用户名、邮箱和密码。

### 2. 登录系统

使用注册的账号登录。

### 3. 搜索案例

在首页搜索框输入关键词，例如"劳动合同纠纷"。

### 4. 查看案例详情

点击搜索结果中的案例，查看详细信息。

### 5. AI 分析

在案例详情页点击"AI 智能分析"按钮，系统会使用 Claude API 分析案例并提供：
- 案情摘要
- 关键要素
- 判决理由
- 法律依据
- 裁判结果

## 添加测试数据

```bash
# 进入后端容器
docker-compose exec backend python

# 在 Python shell 中
from app.db.database import AsyncSessionLocal
from app.models.models import Case
from datetime import date
import asyncio

async def add_test_case():
    async with AsyncSessionLocal() as db:
        case = Case(
            case_number="(2023)京01民终1234号",
            title="张三诉某公司劳动合同纠纷案",
            court="北京市第一中级人民法院",
            case_type="民事",
            judgment_date=date(2023, 6, 15),
            content="原告张三与被告某公司因劳动合同纠纷一案...",
            parties={"plaintiff": "张三", "defendant": "某公司"},
            legal_basis={"laws": ["劳动合同法第39条"]}
        )
        db.add(case)
        await db.commit()
        print("测试案例添加成功！")

asyncio.run(add_test_case())
```

## 下一步开发计划

- [ ] 向量检索（语义搜索）
- [ ] 相似案例推荐
- [ ] 法律文书生成
- [ ] 用户文档管理
- [ ] 数据采集爬虫
- [ ] 高级筛选功能
- [ ] 搜索历史记录

## 故障排除

### 数据库连接失败

确保 PostgreSQL 容器正常运行：
```bash
docker-compose ps
docker-compose logs postgres
```

### API 调用失败

检查 Claude API Key 是否正确配置：
```bash
docker-compose exec backend env | grep ANTHROPIC
```

### 前端无法连接后端

检查 CORS 配置和 API URL：
```bash
# 查看后端日志
docker-compose logs backend
```

## 许可证

MIT

## 联系方式

如有问题，请提交 Issue。
