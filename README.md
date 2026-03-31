# 🧠 脑力锻炼 (Brain Training)

> 一款面向全年龄段的脑力锻炼小程序/App，尤其帮助中老年人预防阿尔茨海默病。

[![CI](https://github.com/y5254y/brain-training/actions/workflows/ci.yml/badge.svg)](https://github.com/y5254y/brain-training/actions/workflows/ci.yml)

---

## 📖 项目简介

**脑力锻炼** 是一个基于 UniApp + FastAPI 的跨平台脑力训练应用，支持微信小程序、H5 网页及原生 App 等多端发布。

通过科学设计的认知训练游戏，帮助：
- 🧒 **青少年**：提升学习能力、专注力和逻辑思维
- 👴 **中老年人**：预防认知衰退，降低阿尔茨海默病风险，保持大脑活力

---

## 🎮 功能规划

### 核心训练模块

| 模块 | 游戏类型 | 训练目标 |
|------|---------|---------|
| 🃏 记忆力 | 翻牌配对 | 提升短时记忆、视觉记忆能力 |
| 🎯 注意力 | 舒尔特方格 | 提升注意力广度和眼球运动速度 |
| 🔢 计算力 | 速算挑战 | 提升心算能力和数字处理速度 |
| 🧩 逻辑推理 | 数列规律 | 提升逻辑分析和归纳推理能力 |
| 💬 语言能力 | 成语接龙 | 提升语言组织和词汇记忆能力 |

### 其他功能

- 📊 **训练报告** — 每日/每周/每月训练数据统计，认知能力雷达图
- 👨‍👩‍👧 **家人关注** — 子女远程查看父母训练情况
- 🏆 **成就系统** — 勋章、连续训练奖励（规划中）
- 🔔 **每日提醒** — 养成训练习惯（规划中）

---

## 🛠️ 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| **前端** | UniApp + Vue 3 | 一套代码，多端发布（微信小程序/H5/App） |
| **状态管理** | Pinia | Vue 3 官方推荐状态管理 |
| **后端** | FastAPI (Python) | 高性能异步 Web 框架，自动生成 API 文档 |
| **数据库** | MySQL 8.0 | 主数据库，存储用户和训练数据 |
| **ORM** | SQLAlchemy 2.0 | Python ORM，使用 pymysql 驱动 |
| **缓存** | Redis 7 | 会话缓存、排行榜等 |
| **认证** | JWT (python-jose) | 无状态 Token 认证 |
| **容器化** | Docker + Docker Compose | 一键部署所有服务 |
| **数据库迁移** | Alembic | 版本化数据库迁移管理 |

---

## 📁 目录结构

```
brain-training/
├── frontend/                  # UniApp 前端
│   ├── pages/
│   │   ├── index/             # 首页（训练入口）
│   │   ├── train/             # 训练模块
│   │   │   ├── memory/        # 记忆力训练（翻牌配对）
│   │   │   ├── attention/     # 注意力训练（舒尔特方格）
│   │   │   ├── calculation/   # 计算力训练（速算）
│   │   │   ├── logic/         # 逻辑推理（数列）
│   │   │   └── language/      # 语言能力（成语接龙）
│   │   ├── report/            # 训练报告
│   │   ├── profile/           # 个人中心
│   │   └── login/             # 登录/注册
│   ├── components/NavBar.vue  # 公共导航栏组件
│   ├── store/user.js          # Pinia 用户状态管理
│   ├── utils/
│   │   ├── request.js         # HTTP 请求封装（含 Token 拦截）
│   │   └── config.js          # 全局配置（API 地址等）
│   ├── App.vue / main.js      # 应用入口
│   ├── pages.json             # 路由配置
│   └── package.json
│
├── backend/                   # FastAPI 后端
│   ├── app/
│   │   ├── main.py            # 应用入口（CORS、路由注册）
│   │   ├── api/               # API 路由层
│   │   │   ├── auth.py        # 认证（注册、登录）
│   │   │   ├── training.py    # 训练数据
│   │   │   ├── report.py      # 训练报告
│   │   │   └── family.py      # 家人关注
│   │   ├── models/            # SQLAlchemy ORM 模型
│   │   ├── schemas/           # Pydantic 数据校验
│   │   ├── services/          # 业务逻辑层
│   │   └── core/              # 核心配置（数据库、JWT、配置）
│   ├── alembic/               # 数据库迁移
│   ├── requirements.txt
│   └── Dockerfile
│
├── alembic.ini                # Alembic 配置
├── docker-compose.yml         # Docker 编排
├── .env.example               # 环境变量示例
└── .gitignore
```

---

## 🚀 快速启动

### 方式一：Docker 一键启动（推荐）

**前提条件**：已安装 [Docker Desktop](https://www.docker.com/products/docker-desktop/)

```bash
# 1. 克隆仓库
git clone https://github.com/y5254y/brain-training.git
cd brain-training

# 2. 复制并配置环境变量
cp .env.example .env
# 编辑 .env 文件，修改数据库密码和 SECRET_KEY

# 3. 一键启动所有服务
docker compose up -d

# 4. 查看服务状态
docker compose ps

# 5. 访问 API 文档
# http://localhost:8000/docs
```

### 方式二：手动启动

#### 后端

```bash
cd backend

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 复制环境变量
cp ../.env.example .env
# 编辑 .env，配置 MySQL 连接信息

# 数据库迁移
alembic upgrade head

# 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API 文档地址：http://localhost:8000/docs

#### 前端

```bash
cd frontend

# 安装依赖
npm install

# 开发调试（H5 模式）
npm run dev:h5

# 开发调试（微信小程序）
npm run dev:mp-weixin
# 然后用微信开发者工具打开 unpackage/dist/dev/mp-weixin 目录
```

---

## 🔧 数据库迁移

```bash
cd backend

# 生成新的迁移脚本
alembic revision --autogenerate -m "描述"

# 执行迁移
alembic upgrade head

# 回滚
alembic downgrade -1
```

---

## 📡 API 接口

后端启动后，访问以下地址查看完整的 Swagger API 文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

主要接口：

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/auth/register` | 用户注册 |
| POST | `/api/v1/auth/login` | 用户登录 |
| GET | `/api/v1/auth/me` | 获取当前用户信息 |
| POST | `/api/v1/training/submit` | 提交训练成绩 |
| GET | `/api/v1/training/list` | 获取训练记录列表 |
| GET | `/api/v1/report/weekly` | 获取本周训练报告 |
| GET | `/api/v1/report/radar` | 获取认知能力雷达图数据 |

---

## 🤝 贡献

欢迎提 Issue 和 PR！

---

## 📄 License

MIT License