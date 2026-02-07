# 🧪 本地 API 测试指南

## 使用本地 API 代理

如果你有本地的 Claude API 代理服务（如 localhost:8080），可以按照以下步骤配置。

---

## 配置步骤

### 1. 修改 .env 文件

```bash
cd legal-ai-assistant

# 编辑 .env 文件
nano .env  # 或使用其他编辑器
```

添加以下配置：

```env
ANTHROPIC_API_KEY=sk-default-key
ANTHROPIC_BASE_URL=http://localhost:8080
```

### 2. 确保本地代理服务运行

```bash
# 检查本地代理是否运行
curl http://localhost:8080/v1/messages

# 或者检查健康状态
curl http://localhost:8080/health
```

### 3. 启动系统

```bash
# 启动服务
./start.sh  # 或 start.bat (Windows)
```

---

## Docker 网络配置

如果你的本地代理运行在宿主机上，需要配置 Docker 网络访问：

### Windows/Mac (Docker Desktop)

使用 `host.docker.internal` 访问宿主机：

```env
ANTHROPIC_BASE_URL=http://host.docker.internal:8080
```

### Linux

使用宿主机 IP 地址：

```bash
# 获取宿主机 IP
ip addr show docker0 | grep inet

# 在 .env 中配置
ANTHROPIC_BASE_URL=http://172.17.0.1:8080
```

或者使用 host 网络模式（修改 docker-compose.yml）：

```yaml
backend:
  network_mode: "host"
  environment:
    - ANTHROPIC_BASE_URL=http://localhost:8080
```

---

## 测试配置

### 1. 测试后端连接

```bash
# 进入后端容器
docker-compose exec backend python

# 测试 API 连接
```

```python
from anthropic import AsyncAnthropic
import asyncio

async def test_connection():
    client = AsyncAnthropic(
        api_key="sk-default-key",
        base_url="http://host.docker.internal:8080"  # 或你的配置
    )

    try:
        response = await client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=100,
            messages=[{"role": "user", "content": "Hello"}]
        )
        print("✅ 连接成功！")
        print(response.content[0].text)
    except Exception as e:
        print(f"❌ 连接失败: {e}")

asyncio.run(test_connection())
```

### 2. 测试完整流程

1. 访问 http://localhost:3000
2. 注册并登录
3. 添加测试案例（参考 TESTING_GUIDE.md）
4. 点击"AI 智能分析"
5. 查看是否正常返回结果

---

## 常见问题

### 问题 1: 连接被拒绝

**错误信息**: `Connection refused` 或 `Cannot connect to host`

**解决方法**:
1. 确认本地代理服务正在运行
2. 检查端口是否正确（8080）
3. 使用 `host.docker.internal` 而不是 `localhost`

```env
# Windows/Mac
ANTHROPIC_BASE_URL=http://host.docker.internal:8080

# Linux
ANTHROPIC_BASE_URL=http://172.17.0.1:8080
```

### 问题 2: 认证失败

**错误信息**: `Authentication failed` 或 `Invalid API key`

**解决方法**:
1. 检查本地代理是否需要认证
2. 确认 API Key 配置正确
3. 查看代理服务日志

### 问题 3: 超时

**错误信息**: `Timeout` 或 `Request timeout`

**解决方法**:
1. 检查网络连接
2. 增加超时时间（修改 ai_service.py）
3. 检查代理服务性能

---

## 高级配置

### 自定义超时时间

编辑 `backend/app/services/ai_service.py`：

```python
client = AsyncAnthropic(
    api_key=settings.ANTHROPIC_API_KEY,
    base_url=settings.ANTHROPIC_BASE_URL,
    timeout=60.0  # 60 秒超时
)
```

### 添加请求日志

```python
import logging

logging.basicConfig(level=logging.DEBUG)

# 在 analyze_case 函数中添加
print(f"Sending request to: {settings.ANTHROPIC_BASE_URL}")
print(f"Using API key: {settings.ANTHROPIC_API_KEY[:10]}...")
```

### 使用不同的模型

如果你的本地代理支持其他模型：

```python
message = await client.messages.create(
    model="your-local-model-name",  # 修改模型名称
    max_tokens=4096,
    messages=[{...}]
)
```

---

## 验证配置

### 检查环境变量

```bash
# 查看后端容器的环境变量
docker-compose exec backend env | grep ANTHROPIC

# 应该看到：
# ANTHROPIC_API_KEY=sk-default-key
# ANTHROPIC_BASE_URL=http://host.docker.internal:8080
```

### 查看日志

```bash
# 查看后端日志
docker-compose logs -f backend

# 查看 API 调用日志
docker-compose logs backend | grep -i anthropic
```

---

## 性能优化

### 1. 使用连接池

如果频繁调用 API，可以配置连接池：

```python
from anthropic import AsyncAnthropic
import httpx

# 创建自定义 HTTP 客户端
http_client = httpx.AsyncClient(
    limits=httpx.Limits(max_connections=10, max_keepalive_connections=5)
)

client = AsyncAnthropic(
    api_key=settings.ANTHROPIC_API_KEY,
    base_url=settings.ANTHROPIC_BASE_URL,
    http_client=http_client
)
```

### 2. 启用缓存

对于相同的案例分析，可以使用 Redis 缓存结果：

```python
import hashlib
import json
from redis import asyncio as aioredis

async def analyze_case_with_cache(case_content: str) -> dict:
    # 生成缓存键
    cache_key = f"analysis:{hashlib.md5(case_content.encode()).hexdigest()}"

    # 尝试从缓存获取
    redis = await aioredis.from_url(settings.REDIS_URL)
    cached = await redis.get(cache_key)

    if cached:
        return json.loads(cached)

    # 调用 API
    result = await analyze_case(case_content)

    # 缓存结果（24小时）
    await redis.setex(cache_key, 86400, json.dumps(result))

    return result
```

---

## 安全建议

1. **不要在生产环境使用默认 API Key**
2. **使用 HTTPS** 如果代理支持
3. **限制访问** 使用防火墙规则
4. **监控使用** 记录 API 调用日志

---

## 示例配置

### 完整的 .env 文件

```env
# 数据库配置
DATABASE_URL=postgresql+asyncpg://legal_user:legal_pass@postgres:5432/legal_ai

# Redis
REDIS_URL=redis://redis:6379/0

# JWT
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Claude API - 本地代理
ANTHROPIC_API_KEY=sk-default-key
ANTHROPIC_BASE_URL=http://host.docker.internal:8080

# 应用配置
APP_NAME=Legal AI Assistant
DEBUG=True
```

---

## 故障排查清单

- [ ] 本地代理服务正在运行
- [ ] 端口 8080 可访问
- [ ] .env 文件配置正确
- [ ] Docker 容器可以访问宿主机
- [ ] API Key 正确
- [ ] 模型名称正确
- [ ] 网络连接正常

---

**配置完成后，重启服务**:

```bash
docker-compose down
docker-compose up -d
```

然后按照 TESTING_GUIDE.md 进行测试。

如有问题，查看日志：
```bash
docker-compose logs -f backend
```
