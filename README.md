# Image RAG Engine

基于 **RAG（检索增强生成）** 思想的图片智能搜索与推荐系统。利用多模态大模型对图片进行多维度语义解耦，通过向量数据库实现"文搜图"和"以图搜图"的混合检索。

## 核心特点

- **多维度语义解耦** — 每张图片从显性特征、隐性特征、整体描述三个语义维度分别提取，解决传统单向量方案的"特征黑盒"问题
- **混合检索 + 加权重排序** — 三路向量并行 ANN 召回后通过 WeightedRanker(0.4, 0.2, 0.4) 融合排序，兼顾召回广度和排序精度
- **搜索词智能扩写** — 用户简短搜索词（如"温暖的午后"）通过 LLM 扩展为多维度描述，弥合语义鸿沟
- **拖拽上传 + 点击选择** — 前端支持拖曳图片和点击选择两种上传方式，一站式完成入库
- **用户级数据隔离** — 所有操作绑定 uid，不同用户图片库互不干扰，支持多租户

## 技术架构

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   React 前端     │────▶│  FastAPI 后端     │────▶│    Ollama        │
│   (Vite +       │     │  (Python)        │     │  qwen3-vl:8b    │
│   Tailwind)     │     │                  │     │  bge-m3          │
└─────────────────┘     └────────┬─────────┘     └─────────────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │     Milvus       │
                        │   向量数据库      │
                        │  (1024维 COSINE) │
                        └─────────────────┘
```

## 环境要求

| 组件 | 版本/说明 |
|------|----------|
| Python | 3.10+ |
| Node.js | 18+ |
| Ollama | 需拉取 `qwen3-vl:8b` 和 `bge-m3` 模型 |
| Milvus | 2.x，运行在 `localhost:19530` |

## 快速开始

### 1. 启动依赖服务

```bash
# 启动 Ollama（默认 localhost:11434）
ollama serve

# 拉取模型（首次运行）
ollama pull qwen3-vl:8b
ollama pull bge-m3

# 启动 Milvus（参考官方文档，此处以 Docker 为例）
# 下载 docker-compose.yml：
# https://milvus.io/docs/install_standalone-docker.md
docker compose up -d
```

### 2. 启动后端

```bash
cd rag_image
pip install -r requirements.txt
python main.py
# 服务启动在 http://0.0.0.0:8000
```

### 3. 启动前端

```bash
cd frontend
npm install
npm run dev
# 服务启动在 http://localhost:5173
```

打开浏览器访问 `http://localhost:5173`，默认 uid 为 `user_001`。

## 配置说明

后端配置集中在 `rag_image/feature_service.py` 顶部：

```python
BASE_URL = "http://localhost:11434/v1"   # Ollama OpenAI 兼容接口
VISION_MODEL = "qwen3-vl:8b"             # 视觉理解模型
EMBEDDING_MODEL = "bge-m3"               # 文本向量化模型（1024维）
```

Milvus 连接串在 `rag_image/main.py` 中通过 `MilvusModel()` 初始化（默认 `localhost:19530`），可按需修改。

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/images/upload` | 上传本地图片文件，一站式入库（FormData） |
| POST | `/api/v1/images/rag` | 通过图片 URL 入库（JSON） |
| POST | `/api/v1/recommend/text` | 文本搜图 |
| POST | `/api/v1/recommend/image` | 以图搜图 |

## 项目结构

```
rag_image/
├── rag_image/                  # 后端
│   ├── main.py                 # FastAPI 应用入口 + API 路由
│   ├── feature_service.py      # Ollama 交互：视觉分析、文本扩写、向量化
│   ├── milvus_db.py            # Milvus 向量数据库操作：混合检索
│   ├── schemas.py              # Pydantic 数据模型
│   └── requirements.txt        # Python 依赖
├── frontend/                   # 前端
│   ├── src/
│   │   ├── App.jsx             # 根组件
│   │   └── components/
│   │       ├── Navbar.jsx      # 导航栏
│   │       ├── UploadSection.jsx   # 图片上传
│   │       └── SearchSection.jsx   # 智能检索
│   ├── vite.config.js          # Vite 配置（含 API 代理）
│   └── package.json
└── README.md
```
