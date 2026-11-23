# fc-server · 个人看房管理系统

> 一个为个人购房者打造的看房记录与决策辅助工具。

---

## 一、项目背景

购房是普通人一生中最大的消费决策之一。面对几十个小区、上百套房源，纯靠脑子记或零散的笔记很难做出理性对比。本系统旨在用结构化的方式，把每一次看房的关键信息、照片、评分和 Checklist 都沉淀下来，最终通过横向对比帮你快速锁定最优解。

**解决的核心痛点：**

- 看房太多记混了？→ 统一管理所有小区和房源档案
- 想对比两套房源？→ 一键横向对比，字段一目了然
- 看房时不知道看什么？→ 内置可自定义的问答 Checklist
- 凭感觉选房？→ 多维度加权评分，量化决策依据
- 每个人关注点不同？→ 字段模板可自由增删改

---

## 二、功能一览

| 模块 | 说明 |
|------|------|
| 🏘️ 小区管理 | 记录开发商、建成年代、绿化率、容积率、物业费、车位类型、对口学校等 |
| 🏠 房源管理 | 关联小区，记录价格、面积、户型、楼层、朝向、装修等 |
| 📷 照片上传 | 支持多图上传，自动压缩原图 + 生成缩略图，按小区/房源分类存储 |
| ⭐ 多维评分 | 预设地段交通、物业管理、房屋品质三大维度，支持自定义权重和问题 |
| ✅ 问答 Checklist | 看房时的结构化检查表，涵盖环境、物业、装修、电器、采光等类别 |
| 📊 横向对比 | 选择多个小区或房源，关键字段并排展示，直观 diff |
| ⚙️ 自定义字段 | 小区和房源的字段模板完全可配置，适配不同买房阶段的需求 |

---

## 三、技术架构

```
┌─────────────────────────────────────────────────────┐
│                    前端 (Vite Dev Server)            │
│         Vue 3 + Vue Router + Vant 4 (移动端优先)      │
│                   Axios 调用后端 API                  │
└──────────────────────┬──────────────────────────────┘
                       │ HTTP / JSON
                       ▼
┌─────────────────────────────────────────────────────┐
│                  后端 (FastAPI + Uvicorn)             │
│          Pydantic 校验 · Pillow 图片压缩 · 种子初始化  │
│   /api/community · /api/listing · /api/score · ...   │
└──────────────────────┬──────────────────────────────┘
                       │ PyMongo
                       ▼
              ┌─────────────────┐
              │   MongoDB 数据库  │
              │  house_manager   │
              └─────────────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ 本地文件系统 /media │
              │  (图片原图+缩略图)  │
              └─────────────────┘
```

**技术栈明细：**

| 层级 | 选型 |
|------|------|
| 后端框架 | FastAPI 0.115 |
| 数据库 | MongoDB（PyMongo 驱动） |
| 数据校验 | Pydantic v2 |
| 图片处理 | Pillow |
| 前端框架 | Vue 3.5 + Vue Router 4 |
| UI 组件库 | Vant 4（移动端） |
| HTTP 客户端 | Axios |
| 构建工具 | Vite 6 |

---

## 四、快速开始

### 4.1 前置条件

- **Python 3.10+**（后端）
- **Node.js 18+**（前端）
- **MongoDB 5+**（数据库，默认 `mongodb://localhost:27017`）

### 4.2 安装后端

```bash
cd backend

# 创建虚拟环境并激活
python3 -m venv .venv
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 4.3 安装前端

```bash
cd frontend

# 安装依赖（国内建议用 npmmirror）
npm install --registry=https://registry.npmmirror.com
```

### 4.4 配置环境变量（可选）

项目使用环境变量覆盖默认配置，所有变量都有合理默认值，**不改也能跑**：

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `MONGO_URI` | `mongodb://localhost:27017` | MongoDB 连接串 |
| `MONGO_DB` | `house_manager` | 数据库名 |
| `MEDIA_ROOT` | `/home/admin/house-media` | 图片存储目录 |
| `HOST` | `0.0.0.0` | 后端监听地址 |
| `PORT` | `8000` | 后端监听端口 |

```bash
# 示例：自定义数据库和端口
export MONGO_URI="mongodb://127.0.0.1:27017"
export MONGO_DB="house_manager"
export PORT=8000
```

### 4.5 启动服务

#### 方式一：一键重启脚本（推荐调试用）

```bash
# 在项目根目录执行
bash restart.sh
```

脚本会自动停止旧进程 → 拉起后端 → 拉起前端 → 等待就绪并打印访问地址。

#### 方式二：分别启动

```bash
# 终端 1：启动后端（端口 8000）
cd backend
source .venv/bin/activate
python run.py

# 终端 2：启动前端（端口 5173）
cd frontend
npm run dev
```

### 4.6 访问

| 服务 | 地址 |
|------|------|
| 前端页面 | http://localhost:5173 |
| 后端 API | http://localhost:8000 |
| API 交互文档 | http://localhost:8000/docs |
| 健康检查 | http://localhost:8000/api/health |

> 首次启动时后端会自动向空的集合写入种子数据（小区/房源字段模板、评分类别和问题、问答 Checklist 示例），开箱即用。

---

## 五、项目结构

```
fc-server/
├── backend/                     # 后端（FastAPI + MongoDB）
│   ├── app/
│   │   ├── main.py             # FastAPI 入口，挂载所有路由
│   │   ├── config.py           # 配置（MongoDB、存储、端口等）
│   │   ├── database.py         # PyMongo 连接单例
│   │   ├── seed.py             # 种子数据（字段模板/评分/问答）
│   │   ├── models/schemas.py   # Pydantic 请求校验模型
│   │   ├── storage/            # 文件存储抽象（本地实现）
│   │   └── routers/            # API 路由模块
│   │       ├── community.py     # 小区 CRUD
│   │       ├── listing.py      # 房源 CRUD
│   │       ├── photo.py        # 照片管理
│   │       ├── score.py        # 评分提交与查询
│   │       ├── qa.py           # 问答 Checklist
│   │       ├── question.py     # 评分问题维护
│   │       ├── field_template.py # 字段模板管理
│   │       └── upload.py       # 文件上传（含压缩）
│   ├── run.py                  # 启动脚本（uvicorn）
│   └── requirements.txt
├── frontend/                    # 前端（Vue 3 + Vant）
│   ├── src/
│   │   ├── api/index.js        # Axios 实例 + 接口封装
│   │   ├── router/index.js     # 路由定义
│   │   ├── views/
│   │   │   ├── Dashboard.vue   # 首页
│   │   │   ├── community/     # 小区列表/详情/表单
│   │   │   ├── listing/        # 房源详情/表单
│   │   │   ├── score/         # 评分表单
│   │   │   ├── qa/            # 问答 Checklist
│   │   │   ├── compare/        # 横向对比
│   │   │   └── admin/         # 字段/问题维护
│   │   └── components/         # 公共组件（动态表单、图片上传）
│   ├── vite.config.js
│   └── package.json
├── scripts/                     # 辅助脚本
│   ├── start-backend.sh
│   └── start-frontend.sh
├── restart.sh                   # ⭐ 一键重启前后端
└── README.md
```

---

## 六、API 路由速览

| 前缀 | 模块 | 核心能力 |
|------|------|----------|
| `/api/community` | 小区 | CRUD、列表查询 |
| `/api/listing` | 房源 | CRUD、按小区筛选 |
| `/api/photo` | 照片 | 按 target_type + target_id 关联 |
| `/api/score` | 评分 | 提交评分、计算加权总分、查询历史 |
| `/api/field-template` | 字段模板 | 小区/房源的自定义字段管理 |
| `/api/question` | 评分问题 | 评分类别和问题的增删改 |
| `/api/qa` | 问答 Checklist | 看房检查表的问题和答案 |
| `/api/upload` | 文件上传 | 图片上传 + 自动压缩 + 缩略图 |
| `/media` | 静态文件 | 直接访问已上传的图片 |

完整接口文档在启动后访问 `/docs` 查看（FastAPI 自动生成的 Swagger UI）。

---

## 七、部署建议

### 生产环境简单方案

```bash
# 1. 前端构建静态文件
cd frontend
npm run build
# 产出在 frontend/dist/

# 2. 后端用 uvicorn 以守护进程运行
cd backend
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

推荐用 **Nginx** 反向代理，将 `/` 指向前端静态目录、`/api` 和 `/media` 代理到后端 8000 端口。

### 进阶

- 后端可以用 **systemd** 或 **supervisor** 托管进程
- 图片存储可以对接 **OSS / MinIO**（只需实现 `backend/app/storage/base.py` 的接口）
- 数据库主从、定时备份按 MongoDB 标准方案即可

---

## 八、License

MIT
