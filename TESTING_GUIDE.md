# 🧪 系统测试指南

## 快速测试流程

按照以下步骤测试系统的各项功能是否正常。

---

## 前置准备

### 1. 确保 Docker 正在运行

```bash
# 检查 Docker 状态
docker --version
docker-compose --version

# 查看 Docker 是否运行
docker ps
```

### 2. 配置 API Key

```bash
cd legal-ai-assistant

# 创建 .env 文件
cp .env.example .env

# 编辑 .env 文件，填入你的 Claude API Key
# ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
```

---

## 测试步骤

### 第一步：启动系统

```bash
# Windows
start.bat

# Linux/Mac
chmod +x start.sh
./start.sh
```

**预期结果**:
- ✅ 所有容器启动成功
- ✅ 数据库初始化完成
- ✅ 显示访问地址

**验证命令**:
```bash
# 查看容器状态（应该有 4 个容器运行）
docker-compose ps

# 应该看到：
# legal-ai-postgres   running
# legal-ai-redis      running
# legal-ai-backend    running
# legal-ai-frontend   running
```

---

### 第二步：测试后端 API

#### 2.1 健康检查

```bash
# 测试后端健康状态
curl http://localhost:8000/health
```

**预期结果**:
```json
{"status":"healthy"}
```

#### 2.2 查看 API 文档

打开浏览器访问: http://localhost:8000/docs

**预期结果**:
- ✅ 看到 Swagger API 文档界面
- ✅ 显示所有 API 端点
- ✅ 可以展开查看详细信息

---

### 第三步：测试前端界面

#### 3.1 访问登录页

打开浏览器访问: http://localhost:3000

**预期结果**:
- ✅ 看到登录/注册界面
- ✅ 界面美观，无错误提示
- ✅ 有"登录"和"注册"两个标签页

#### 3.2 注册新用户

1. 点击"注册"标签
2. 填写信息：
   - 用户名: `testuser`
   - 邮箱: `test@example.com`
   - 密码: `123456`
3. 点击"注册"按钮

**预期结果**:
- ✅ 显示"注册成功！请登录"
- ✅ 自动切换到登录标签

#### 3.3 登录系统

1. 在登录标签页填写：
   - 用户名: `testuser`
   - 密码: `123456`
2. 点击"登录"按钮

**预期结果**:
- ✅ 显示"登录成功！"
- ✅ 跳转到首页
- ✅ 看到搜索界面

---

### 第四步：添加测试数据

打开新的终端窗口：

```bash
# 进入后端容器
docker-compose exec backend python

# 在 Python shell 中执行以下代码
```

```python
from app.db.database import AsyncSessionLocal
from app.models.models import Case
from datetime import date
import asyncio

async def add_test_cases():
    async with AsyncSessionLocal() as db:
        # 测试案例 1
        case1 = Case(
            case_number="(2023)京01民终1234号",
            title="张三诉某公司劳动合同纠纷案",
            court="北京市第一中级人民法院",
            case_type="民事",
            judgment_date=date(2023, 6, 15),
            content="""原告张三与被告某公司因劳动合同纠纷一案，原告诉称：2020年1月入职被告公司，担任软件工程师。2023年3月，被告以业绩不佳为由解除劳动合同，未支付经济补偿金。请求判令被告支付经济补偿金3万元。

被告辩称：原告在职期间多次违反公司规章制度，经警告无效，公司依法解除劳动合同，无需支付经济补偿金。

本院认为：根据《劳动合同法》第39条规定，劳动者严重违反用人单位规章制度的，用人单位可以解除劳动合同。但被告未能提供充分证据证明原告存在严重违纪行为，且未履行合法的解除程序。因此，被告应支付经济补偿金。

判决如下：被告某公司于本判决生效之日起十日内支付原告张三经济补偿金人民币30000元。""",
            parties={"plaintiff": "张三", "defendant": "某公司"},
            legal_basis={"laws": ["劳动合同法第39条", "劳动合同法第46条"]}
        )

        # 测试案例 2
        case2 = Case(
            case_number="(2023)沪02民初5678号",
            title="李四与王五房屋买卖合同纠纷案",
            court="上海市第二中级人民法院",
            case_type="民事",
            judgment_date=date(2023, 8, 20),
            content="""原告李四与被告王五因房屋买卖合同纠纷一案，原告诉称：2022年5月与被告签订房屋买卖合同，约定购买被告位于上海市浦东新区的房产一套，总价500万元。原告已支付定金50万元，但被告拒绝继续履行合同。请求判令被告继续履行合同或返还双倍定金。

被告辩称：签订合同后房价大幅上涨，继续履行合同将造成重大损失，且原告未按约定时间支付首付款，构成违约。

本院认为：双方签订的房屋买卖合同合法有效，应当履行。被告以房价上涨为由拒绝履行合同，不符合法律规定的合同解除条件。原告虽延迟支付首付款，但延迟时间较短，不构成根本违约。

判决如下：被告王五应继续履行房屋买卖合同，将涉案房产过户给原告李四。""",
            parties={"plaintiff": "李四", "defendant": "王五"},
            legal_basis={"laws": ["合同法第107条", "民法典第577条"]}
        )

        # 测试案例 3
        case3 = Case(
            case_number="(2023)粤03刑初9012号",
            title="人民检察院诉赵六盗窃案",
            court="广东省深圳市中级人民法院",
            case_type="刑事",
            judgment_date=date(2023, 9, 10),
            content="""公诉机关指控：被告人赵六于2023年3月至5月期间，多次在深圳市南山区某小区盗窃电动车，共计盗窃电动车8辆，价值约4万元。

被告人赵六辩称：承认盗窃事实，但部分电动车是捡来的，不是偷的。

本院认为：被告人赵六以非法占有为目的，秘密窃取他人财物，数额较大，其行为已构成盗窃罪。被告人当庭认罪，可酌情从轻处罚。

判决如下：被告人赵六犯盗窃罪，判处有期徒刑一年六个月，并处罚金人民币5000元。""",
            parties={"prosecutor": "人民检察院", "defendant": "赵六"},
            legal_basis={"laws": ["刑法第264条"]}
        )

        db.add(case1)
        db.add(case2)
        db.add(case3)
        await db.commit()
        print("✅ 成功添加 3 个测试案例！")

asyncio.run(add_test_cases())
```

**预期结果**:
```
✅ 成功添加 3 个测试案例！
```

按 `Ctrl+D` 或输入 `exit()` 退出 Python shell。

---

### 第五步：测试搜索功能

回到浏览器（http://localhost:3000）：

#### 5.1 搜索"劳动合同"

1. 在搜索框输入: `劳动合同`
2. 点击"搜索"按钮

**预期结果**:
- ✅ 显示"找到 1 个相关案例"
- ✅ 看到"张三诉某公司劳动合同纠纷案"
- ✅ 显示案例基本信息（案件类型、法院、日期）

#### 5.2 搜索"房屋"

1. 在搜索框输入: `房屋`
2. 点击"搜索"按钮

**预期结果**:
- ✅ 显示"找到 1 个相关案例"
- ✅ 看到"李四与王五房屋买卖合同纠纷案"

#### 5.3 搜索"盗窃"

1. 在搜索框输入: `盗窃`
2. 点击"搜索"按钮

**预期结果**:
- ✅ 显示"找到 1 个相关案例"
- ✅ 看到"人民检察院诉赵六盗窃案"

---

### 第六步：测试案例详情

点击任意搜索结果（例如"张三诉某公司劳动合同纠纷案"）：

**预期结果**:
- ✅ 跳转到案例详情页
- ✅ 显示完整的案例信息
- ✅ 显示判决书全文
- ✅ 看到"AI 智能分析"按钮

---

### 第七步：测试 AI 分析

在案例详情页：

1. 点击"AI 智能分析"按钮
2. 等待分析完成（约 10-30 秒）

**预期结果**:
- ✅ 按钮显示"加载中"状态
- ✅ 分析完成后显示"分析完成！"
- ✅ 看到 AI 分析结果卡片，包含：
  - 📝 案情摘要
  - 🔑 关键要素（当事人、案由、争议焦点）
  - ⚖️ 判决理由分析
  - 📚 法律依据
  - ✅ 裁判结果

---

## 故障排查

### 问题 1: 容器启动失败

```bash
# 查看日志
docker-compose logs

# 重启服务
docker-compose down
docker-compose up -d
```

### 问题 2: 前端无法访问

```bash
# 检查前端容器状态
docker-compose logs frontend

# 检查端口是否被占用
netstat -ano | findstr :3000  # Windows
lsof -i :3000                 # Linux/Mac
```

### 问题 3: 后端 API 错误

```bash
# 查看后端日志
docker-compose logs backend

# 检查数据库连接
docker-compose exec backend python -c "from app.db.database import engine; print('DB OK')"
```

### 问题 4: AI 分析失败

**可能原因**:
- API Key 未配置或无效
- API 配额用完
- 网络连接问题

**解决方法**:
```bash
# 检查 API Key 配置
docker-compose exec backend env | grep ANTHROPIC

# 查看详细错误
docker-compose logs backend | grep -i error
```

### 问题 5: 数据库连接失败

```bash
# 检查 PostgreSQL 容器
docker-compose ps postgres
docker-compose logs postgres

# 重置数据库
docker-compose down -v
docker-compose up -d
sleep 10
docker-compose exec backend alembic upgrade head
```

---

## 性能测试

### 测试并发请求

```bash
# 安装 Apache Bench (可选)
# Windows: 下载 Apache 包
# Linux: sudo apt-get install apache2-utils
# Mac: brew install httpd

# 测试 API 性能
ab -n 100 -c 10 http://localhost:8000/health

# 预期结果：
# - 成功率 100%
# - 平均响应时间 < 100ms
```

---

## 测试清单

完成以下所有测试项：

- [ ] Docker 容器全部启动
- [ ] 后端健康检查通过
- [ ] API 文档可访问
- [ ] 前端登录页正常显示
- [ ] 用户注册成功
- [ ] 用户登录成功
- [ ] 添加测试数据成功
- [ ] 搜索功能正常
- [ ] 案例详情显示正常
- [ ] AI 分析功能正常
- [ ] 所有页面无报错

---

## 测试完成

如果所有测试项都通过，恭喜你！系统运行正常，可以开始使用了。🎉

如果遇到问题，请参考：
- `README.md` - 完整文档
- `QUICKSTART.md` - 快速启动指南
- 本文档的故障排查部分

---

**测试时间**: 约 15-20 分钟
**难度**: ⭐⭐ (简单)
**前置要求**: Docker、Claude API Key
