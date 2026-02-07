@echo off
echo ======================================
echo 法律 AI 助手 - 启动脚本
echo ======================================

REM 检查 Docker
where docker >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo 错误: Docker 未安装
    exit /b 1
)

where docker-compose >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo 错误: Docker Compose 未安装
    exit /b 1
)

REM 检查 .env 文件
if not exist .env (
    echo 创建 .env 文件...
    echo ANTHROPIC_API_KEY=your-api-key-here > .env
    echo 警告: 请编辑 .env 文件，填入你的 Claude API Key
    echo 获取 API Key: https://console.anthropic.com/
    exit /b 1
)

REM 启动服务
echo 启动 Docker 容器...
docker-compose up -d

REM 等待数据库就绪
echo 等待数据库启动...
timeout /t 10 /nobreak >nul

REM 初始化数据库
echo 初始化数据库...
docker-compose exec -T backend alembic upgrade head

echo.
echo ======================================
echo 启动完成！
echo ======================================
echo 前端: http://localhost:3000
echo 后端 API 文档: http://localhost:8000/docs
echo.
echo 查看日志: docker-compose logs -f
echo 停止服务: docker-compose down
echo ======================================
pause
