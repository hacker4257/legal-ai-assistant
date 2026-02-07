# 🎉 本地 API 配置完成！

## ✅ 已完成的配置

我已经为你配置好了使用本地 API 代理的支持。以下是修改的内容：

### 1. 后端配置更新

**文件**: `backend/app/core/config.py`
- ✅ 添加了 `ANTHROPIC_BASE_URL` 配置项
- ✅ 支持可选的自定义 API 端点

**文件**: `backend/app/services/ai_service.py`
- ✅ 更新了 Claude 客户端初始化
- ✅ 支持自定义 base_url

### 2. Docker 配置更新

**文件**: `docker-compose.yml`
- ✅ 添加了 `ANTHROPIC_BASE_URL` 环境变量
- ✅ 添加了 `extra_hosts` 配置，支持访问宿主机
- ✅ 使用 `host.docker.internal` 访问本地服务

### 3. 环境变量配置

**文件**: `.env`
```env
ANTHROPIC_API_KEY=sk-default-key
ANTHROPIC_BASE_URL=http://localhost:8080
```

**注意**: 在 Docker 容器中，需要使用 `host.docker.internal` 而不是 `localhost`

---

## 🚀 如何使用

### 方式 1: 使用 localhost:8080（推荐）

如果你的本地 API 代理运行在 `localhost:8080`：

**编辑 `.env` 文件**:
```env
ANTHROPIC_API_KEY=sk-default-key
ANTHROPIC_BASE_URL=http://host.docker.internal:8080
```

### 方式 2: 使用其他端口

如果你的代理运行在其他端口（如 8081）：

```env
ANTHROPIC_API_KEY=sk-default-key
ANTHROPIC_BASE_URL=http://host.docker.internal:8081
```

### 方式 3: 使用官方 API

如果要使用官方 Anthropic API：

```env
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
ANTHROPIC_BASE_URL=
```

（留空 `ANTHROPIC_BASE_URL` 即可）

---

## 🧪 测试步骤

### 1. 确保本地代理运行

```bash
# 检查本地代理是否运行
curl http://localhost:8080/v1/messages
# 或
curl http://localhost:8080/health
```

### 2. 更新 .env 文件

```bash
cd legal-ai-assistant

# 编辑 .env
notepad .env  # Windows
# 或
nano .env     # Linux/Mac
```

确保内容为：
```env
ANTHROPIC_API_KEY=sk-default-key
ANTHROPIC_BASE_URL=http://host.docker.internal:8080
```

### 3. 启动系统

```bash
# 停止现有服务（如果在运行）
docker-compose down

# 启动服务
./start.sh  # 或 start.bat (Windows)
```

### 4. 测试 API 连接

```bash
# 进入后端容器
docker-compose exec backend python

# 运行测试
```

```python
from anthropic import AsyncAnthropic
import asyncio

async def test():
    client = AsyncAnthropic(
        api_key="sk-default-key",
        base_url="http://host.docker.internal:8080"
    )

    try:
        response = await client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=100,
            messages=[{"role": "user", "content": "你好"}]
        )
        print("✅ 连接成功！")
        print(response.content[0].text)
    except Exception as e:
        print(f"❌ 连接失败: {e}")

asyncio.run(test())
```

按 `Ctrl+D` 退出 Python。

### 5. 测试完整功能

1. 访问 http://localhost:3000
2. 注册并登录
3. 添加测试案例（参考 TESTING_GUIDE.md 第四步）
4. 搜索案例
5. 点击"AI 智能分析"
6. 查看分析结果

---

## 🔍 验证配置

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
# 实时查看后端日志
docker-compose logs -f backend

# 查看 API 调用相关日志
docker-compose logs backend | grep -i anthropic
```

---

## ⚠️ 常见问题

### 问题 1: Connection refused

**错误**: `Connection refused to http://host.docker.internal:8080`

**解决方法**:
1. 确认本地代理正在运行：`curl http://localhost:8080`
2. 确认使用了 `host.docker.internal` 而不是 `localhost`
3. 检查防火墙设置

### 问题 2: Linux 系统不支持 host.docker.internal

**解决方法**:

使用宿主机 IP 地址：

```bash
# 获取 Docker 网桥 IP
ip addr show docker0 | grep inet

# 通常是 172.17.0.1
```

在 `.env` 中配置：
```env
ANTHROPIC_BASE_URL=http://172.17.0.1:8080
```

### 问题 3: 认证失败

**错误**: `Authentication failed`

**解决方法**:
1. 检查本地代理是否需要特定的 API Key
2. 确认 API Key 格式正确
3. 查看代理服务的日志

---

## 📚 相关文档

- `LOCAL_API_SETUP.md` - 详细的本地 API 配置指南
- `TESTING_GUIDE.md` - 完整的测试流程
- `QUICKSTART.md` - 快速启动指南

---

## 🎊 配置完成

你现在可以使用本地 API 代理了！

**下一步**:
1. 确保本地代理运行在 `localhost:8080`
2. 更新 `.env` 文件
3. 运行 `docker-compose down && ./start.sh`
4. 测试 AI 分析功能

如有问题，查看 `LOCAL_API_SETUP.md` 获取详细帮助。

祝使用愉快！🚀
