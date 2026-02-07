# 🚀 快速启动指南

## 前置要求

- ✅ Docker Desktop 已安装并运行
- ✅ 有 Claude API Key（从 https://console.anthropic.com/ 获取）

## 三步启动

### 第一步：配置 API Key

创建 `.env` 文件：

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

编辑 `.env` 文件，填入你的 API Key：
```
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
```

### 第二步：启动服务

**Windows 用户：**
```bash
start.bat
```

**Linux/Mac 用户：**
```bash
chmod +x start.sh
./start.sh
```

### 第三步：访问应用

- 🌐 前端界面：http://localhost:3000
- 📚 API 文档：http://localhost:8000/docs

## 首次使用

1. **注册账号**
   - 访问 http://localhost:3000/login
   - 点击"注册"标签
   - 填写用户名、邮箱、密码

2. **登录系统**
   - 使用注册的账号登录

3. **添加测试数据**（可选）
   ```bash
   docker-compose exec backend python
   ```

   然后在 Python shell 中运行：
   ```python
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
               content="原告张三与被告某公司因劳动合同纠纷一案，原告诉称：2020年1月入职被告公司，担任软件工程师。2023年3月，被告以业绩不佳为由解除劳动合同，未支付经济补偿金。请求判令被告支付经济补偿金3万元。被告辩称：原告在职期间多次违反公司规章制度，经警告无效，公司依法解除劳动合同，无需支付经济补偿金。本院认为：根据《劳动合同法》第39条规定，劳动者严重违反用人单位规章制度的，用人单位可以解除劳动合同。但被告未能提供充分证据证明原告存在严重违纪行为，且未履行合法的解除程序。因此，被告应支付经济补偿金。判决如下：被告某公司于本判决生效之日起十日内支付原告张三经济补偿金人民币30000元。",
               parties={"plaintiff": "张三", "defendant": "某公司"},
               legal_basis={"laws": ["劳动合同法第39条", "劳动合同法第46条"]}
           )
           db.add(case)
           await db.commit()
           print("✅ 测试案例添加成功！")

   asyncio.run(add_test_case())
   ```

4. **搜索案例**
   - 在首页搜索框输入"劳动合同"
   - 查看搜索结果

5. **AI 分析**
   - 点击案例进入详情页
   - 点击"AI 智能分析"按钮
   - 查看 AI 生成的分析结果

## 常用命令

```bash
# 查看日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 重置数据库
docker-compose down -v
docker-compose up -d
docker-compose exec backend alembic upgrade head
```

## 故障排除

### 问题 1：端口被占用

如果 3000 或 8000 端口被占用，修改 `docker-compose.yml`：

```yaml
frontend:
  ports:
    - "3001:80"  # 改为其他端口

backend:
  ports:
    - "8001:8000"  # 改为其他端口
```

### 问题 2：Docker 启动失败

```bash
# 检查 Docker 是否运行
docker ps

# 重启 Docker Desktop
# Windows: 右键托盘图标 -> Restart
# Mac: 点击菜单栏图标 -> Restart
```

### 问题 3：数据库初始化失败

```bash
# 手动初始化
docker-compose exec backend alembic upgrade head

# 如果还是失败，重置数据库
docker-compose down -v
docker-compose up -d postgres
sleep 10
docker-compose up -d
docker-compose exec backend alembic upgrade head
```

### 问题 4：前端无法连接后端

检查后端是否正常运行：
```bash
curl http://localhost:8000/health
```

应该返回：`{"status":"healthy"}`

## 开发模式

如果你想修改代码并实时查看效果：

### 后端开发
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env，配置数据库连接
uvicorn app.main:app --reload
```

### 前端开发
```bash
cd frontend
npm install
npm run dev
```

## 下一步

- 📖 阅读 [README.md](README.md) 了解完整功能
- 📊 查看 [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) 了解项目详情
- 🏗️ 查看 [legal-ai-assistant-architecture.md](../legal-ai-assistant-architecture.md) 了解技术架构

---

**需要帮助？** 查看 [README.md](README.md) 的故障排除部分或提交 Issue。
