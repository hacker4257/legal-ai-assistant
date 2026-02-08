# 部署指南

本项目使用 GitHub Actions 自动部署到 GitHub Pages（前端）和 Render（后端）。

## 🚀 快速部署

### 前提条件

1. GitHub 账号
2. Render 账号（免费）：https://render.com
3. Anthropic API Key：https://console.anthropic.com

---

## 📦 前端部署（GitHub Pages）

### 1. 启用 GitHub Pages

1. 进入你的 GitHub 仓库
2. 点击 **Settings** → **Pages**
3. 在 **Source** 下选择 **GitHub Actions**

### 2. 配置环境变量（可选）

如果后端不在 `https://legal-ai-assistant.onrender.com`，需要设置：

1. 进入 **Settings** → **Secrets and variables** → **Actions**
2. 点击 **New repository secret**
3. 添加：
   - Name: `VITE_API_URL`
   - Value: 你的后端 URL（如 `https://your-backend.onrender.com`）

### 3. 触发部署

推送代码到 `main` 分支，或者：

1. 进入 **Actions** 标签
2. 选择 **Deploy Frontend to GitHub Pages**
3. 点击 **Run workflow**

部署完成后，访问：`https://hacker4257.github.io/legal-ai-assistant/`

---

## 🔧 后端部署（Render）

### 方式一：使用 render.yaml（推荐）

1. 登录 [Render Dashboard](https://dashboard.render.com/)
2. 点击 **New** → **Blueprint**
3. 连接你的 GitHub 仓库
4. Render 会自动检测 `render.yaml` 并创建服务
5. 在 **Environment** 中设置 `ANTHROPIC_API_KEY`

### 方式二：手动创建

#### 1. 创建 PostgreSQL 数据库

1. 点击 **New** → **PostgreSQL**
2. 填写：
   - Name: `legal-ai-db`
   - Database: `legal_ai_assistant`
   - User: `legal_ai_user`
   - Region: Oregon
   - Plan: **Free**
3. 点击 **Create Database**
4. 复制 **Internal Database URL**

#### 2. 创建 Web Service

1. 点击 **New** → **Web Service**
2. 连接 GitHub 仓库
3. 填写：
   - Name: `legal-ai-assistant`
   - Region: Oregon
   - Branch: `main`
   - Root Directory: `backend`
   - Runtime: **Python 3**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Plan: **Free**

#### 3. 设置环境变量

在 **Environment** 标签添加：

| Key | Value |
|-----|-------|
| `DATABASE_URL` | （粘贴数据库 Internal URL） |
| `SECRET_KEY` | （随机生成，如 `openssl rand -hex 32`） |
| `ALGORITHM` | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` |
| `ANTHROPIC_API_KEY` | （你的 Anthropic API Key） |
| `ANTHROPIC_BASE_URL` | `https://api.anthropic.com` |
| `APP_NAME` | `Legal AI Assistant` |
| `DEBUG` | `false` |
| `BACKEND_CORS_ORIGINS` | `["https://hacker4257.github.io"]` |

#### 4. 运行数据库迁移

部署完成后，在 Render Shell 中运行：

```bash
cd backend
alembic upgrade head
```

---

## 🔄 更新部署

### 前端

推送代码到 `main` 分支，GitHub Actions 会自动部署。

### 后端

推送代码到 `main` 分支，Render 会自动重新部署。

---

## 🐛 故障排查

### 前端无法访问后端

1. 检查 `VITE_API_URL` 是否正确
2. 检查后端 CORS 配置是否包含前端域名
3. 打开浏览器控制台查看错误信息

### 后端启动失败

1. 检查 Render 日志：Dashboard → 你的服务 → Logs
2. 确认所有环境变量都已设置
3. 确认数据库连接正常
4. 检查 `ANTHROPIC_API_KEY` 是否有效

### 数据库连接失败

1. 确认 `DATABASE_URL` 使用的是 **Internal Database URL**
2. 确认数据库和 Web Service 在同一 Region
3. 运行 `alembic upgrade head` 初始化数据库

---

## 💰 费用说明

- **GitHub Pages**: 完全免费
- **Render Free Plan**:
  - Web Service: 750 小时/月（足够一个应用）
  - PostgreSQL: 90 天免费，之后需要重新创建或升级
  - 服务会在 15 分钟无活动后休眠，首次访问需要 30-60 秒唤醒

---

## 🔐 安全建议

1. **不要**将 API Key 提交到 Git
2. 使用强随机 `SECRET_KEY`
3. 生产环境设置 `DEBUG=false`
4. 定期更新依赖包
5. 限制 CORS 只允许你的前端域名

---

## 📚 相关链接

- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [Render 文档](https://render.com/docs)
- [Vite 部署指南](https://vitejs.dev/guide/static-deploy.html)
- [FastAPI 部署指南](https://fastapi.tiangolo.com/deployment/)
