# 实验室安全智能问答系统 (Lab Safety System)

基于 RAG（检索增强生成）和 YOLOv8 计算机视觉的实验室安全智能问答与隐患检测系统。

## 功能特性

### 📝 智能问答
- 基于 RAG（检索增强生成）的实验室安全知识问答
- 本地知识库向量检索 + LLM 生成回答
- 支持流式和非流式两种问答模式
- 自动识别打招呼/闲聊与安全相关问题
- 标准化的回答格式：隐患类型、风险等级、处置步骤、预防建议

### 🔍 图像隐患识别
- 上传实验室照片，YOLOv8 自动检测物体（设备、化学品、消防设施等）
- LLM 分析检测结果，推断潜在安全隐患
- 针对每个隐患生成处置步骤和预防建议
- 支持 80 类 COCO 数据集的物体检测，过滤实验室相关类别

### 📋 安全检查管理
- 创建和跟踪安全检查记录
- 隐患整改全流程管理（待整改 → 整改中 → 已验收）
- 指定责任人和整改期限
- 历史记录查询

### 👤 用户管理
- 用户注册和登录（JWT 认证）
- 普通用户和管理员角色
- 管理员可管理用户列表（增删改查）

## 技术栈

| 组件 | 技术 |
|------|------|
| **后端框架** | FastAPI + Uvicorn (Python 3.11+) |
| **数据库** | MySQL (SQLAlchemy ORM) |
| **向量数据库** | ChromaDB |
| **嵌入模型** | Sentence-BERT (all-MiniLM-L6-v2 / BGE-large-zh-v1.5) |
| **大语言模型** | 通过 API 调用（支持 SiliconFlow、阿里云 DashScope、OpenAI 兼容接口） |
| **视觉检测** | YOLOv8n (Ultralytics) |
| **前端框架** | Vue 3 (Composition API) + Element Plus |
| **构建工具** | Vite |
| **认证方式** | JWT (PyJWT + passlib) |
| **包管理** | Python: uv, Node.js: npm |

## 项目结构

```
lab-safety-system/
├── backend/                    # FastAPI 后端
│   ├── app/
│   │   ├── routers/            # API 路由
│   │   │   ├── qa.py           #   问答接口
│   │   │   ├── user.py         #   用户管理
│   │   │   ├── image_inspect.py #  图片检测
│   │   │   └── inspection.py   #   检查记录
│   │   ├── auth.py             # JWT 认证
│   │   ├── config.py           # 配置加载
│   │   ├── database.py         # 数据库连接
│   │   ├── dataset_loader.py   # 数据集加载/知识库构建
│   │   ├── embedding.py        # 向量嵌入模型
│   │   ├── llm_client.py       # LLM API 客户端
│   │   ├── main.py             # FastAPI 应用入口
│   │   ├── models.py           # 数据库模型
│   │   └── rag_engine.py       # RAG 检索引擎
│   ├── .env                    # 环境变量配置
│   ├── main.py                 # 启动入口
│   └── run.py                  # 启动入口（备用）
├── frontend/                   # Vue 3 前端
│   ├── src/
│   │   ├── views/              # 页面
│   │   │   ├── Home.vue             # 问答页面
│   │   │   ├── ImageInspect.vue     # 图像识别
│   │   │   ├── InspectionManage.vue # 检查管理
│   │   │   ├── UserManage.vue       # 用户管理
│   │   │   ├── Login.vue            # 登录
│   │   │   └── Register.vue         # 注册
│   │   ├── router/index.js     # 路由配置
│   │   ├── App.vue             # 根组件
│   │   └── main.js             # 入口
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
├── data/                       # 数据目录
│   ├── knowledge/              # 知识库文档（txt/pdf/docx）
│   └── vector_db/              # ChromaDB 向量数据库
├── models/                     # ML 模型文件
│   └── yolov8n.pt
├── scripts/                    # 工具脚本
│   └── build_knowledge_base.py # 知识库构建脚本
├── pyproject.toml              # Python 项目配置
├── README.md
└── .gitignore
```

## 快速开始

### 环境要求

- Python >= 3.10
- Node.js >= 18
- MySQL 数据库

### 1. 克隆项目

```bash
git clone https://github.com/RAOsam/lab-safety-system.git
cd lab-safety-system
```

### 2. 后端配置与启动

```bash
# 创建虚拟环境（使用 uv 或 venv）
uv venv
# 或: python -m venv .venv

# 激活虚拟环境
# Windows:
.venv\Scripts\activate
# Linux/Mac:
# source .venv/bin/activate

# 安装依赖
uv sync
# 或: pip install -r backend/requirements.txt

# 配置环境变量
# 编辑 backend/.env，设置以下参数：
#   MYSQL_URL=mysql+pymysql://user:password@localhost:3306/lab_safety
#   API_BASE_URL=https://api.siliconflow.cn/v1
#   API_KEY=your_api_key_here

# 创建 MySQL 数据库
mysql -u root -p -e "CREATE DATABASE lab_safety CHARACTER SET utf8mb4"

# 构建知识库（可选）
cd backend
python -c "from app.dataset_loader import DatasetLoader; loader = DatasetLoader(); loader.add_sample_data()"

# 启动后端
python main.py
# 服务运行在 http://localhost:8001
```

### 3. 前端配置与启动

```bash
cd frontend
npm install
npm run dev
# 开发服务器运行在 http://localhost:5173
# API 请求自动代理到 http://localhost:8001
```

### 4. 访问系统

- 打开浏览器访问 http://localhost:5173
- 注册新用户或使用已有账号登录
- 开始使用安全问答、图像识别、检查管理等功能

## API 文档

启动后端后，访问 http://localhost:8001/docs 查看 Swagger 交互式 API 文档。

### 主要 API 端点

| 端点 | 方法 | 说明 | 认证 |
|------|------|------|------|
| `/api/qa/ask` | POST | 安全问答 | 否 |
| `/api/qa/ask/stream` | POST | 流式安全问答 | 是 |
| `/api/image/inspect` | POST | 图片安全隐患检测 | 否 |
| `/api/inspections` | GET/POST | 检查记录列表/创建 | 否 |
| `/api/inspections/{id}` | PUT/DELETE | 更新/删除检查记录 | 否 |
| `/api/user/register` | POST | 用户注册 | 否 |
| `/api/user/login` | POST | 用户登录 | 否 |
| `/api/user/list` | GET | 用户列表（管理员） | 是 |
| `/api/users` | GET/POST/PUT/DELETE | 用户管理（前端兼容） | 是 |

## 环境变量说明

在 `backend/.env` 中配置：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `MYSQL_URL` | MySQL 数据库连接 URL | `mysql+pymysql://root:root@localhost:3306/lab_safety` |
| `API_BASE_URL` | LLM API 地址 | `https://api.siliconflow.cn/v1` |
| `API_KEY` | LLM API 密钥 | （必填） |
| `EMBEDDING_MODEL` | 向量嵌入模型 | `all-MiniLM-L6-v2` |
| `CHROMA_PERSIST_DIR` | 向量数据库路径 | `../data/vector_db` |
| `KNOWLEDGE_DIR` | 知识库文档路径 | `../data/knowledge` |
| `YOLO_MODEL_PATH` | YOLO 模型路径 | `./models/yolov8n.pt` |

### 支持的 LLM 提供商

- **SiliconFlow** (`https://api.siliconflow.cn/v1`) — 默认，模型: `Qwen/Qwen3-8B`
- **阿里云 DashScope** (`https://dashscope.aliyuncs.com/compatible-mode/v1`) — 模型: `qwen3.6-plus`
- **OpenAI 兼容接口** — 设置对应 API 地址和密钥

## 常见问题

### Q: 问答接口返回超时？
A: 检查 `backend/.env` 中的 `API_BASE_URL` 和 `API_KEY` 是否正确配置，确保网络可以访问 API 服务。

### Q: 如何构建知识库？
A: 将文档（txt/pdf/docx）放入 `data/knowledge/` 目录，然后运行：
```bash
cd backend
python -c "from app.dataset_loader import DatasetLoader; loader = DatasetLoader(); loader.load_huggingface_dataset('yujunzhou/LabSafety_Bench')"
```

### Q: 前端页面刷新后提示未登录？
A: 这是正常的安全行为。如果已登录，系统会自动恢复登录状态（JWT Token 保存在 localStorage 中）。

## License

MIT
