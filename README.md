# Mini RAG Agent

一个用于学习 **Python + LangChain + LlamaIndex + Vue 3 前后端联调** 的小型 RAG 项目。目标不是复刻 MaxKB，而是做一个小而完整的闭环：

1. 前端上传文档
2. 后端解析并切分文档
3. 用户提问
4. 后端检索相关片段
5. 调 LLM 或 mock 生成回答
6. 前端展示答案和引用来源
7. 用评测脚本批量检查效果
8. 用 LlamaIndex 练习分类、增删改查和检索

---

## 技术栈

| 层级 | 技术 |
|------|------|
| Frontend | Vue 3, TypeScript, Vite, Element Plus, Axios |
| Backend | Python 3.11, FastAPI, uv (包管理) |
| RAG | LangChain text splitter, 本地关键词向量存储 |
| LlamaIndex | VectorStoreIndex 文档 CRUD 演示 |
| LLM | OpenAI (可选), 无 Key 时使用 Mock 回答 |
| Eval | Python + httpx |

---

## 目录结构

```text
mini-rag-agent/
├── backend/
│   ├── src/backend/
│   │   ├── main.py              # FastAPI 应用入口
│   │   ├── config.py            # 配置管理 (.env)
│   │   ├── schemas.py           # Pydantic 数据模型
│   │   ├── routes/              # API 路由
│   │   │   ├── chat.py          # POST /api/chat — RAG 问答
│   │   │   ├── documents.py     # 文档上传、列表、删除
│   │   │   ├── health.py        # GET /api/health — 健康检查
│   │   │   └── llama.py         # LlamaIndex CRUD + 检索
│   │   ├── rag/                 # LangChain RAG 模块
│   │   │   ├── agent.py         # Agent 模式（工具调用）
│   │   │   ├── chain.py         # RAG 问答链（检索 + Prompt + LLM）
│   │   │   ├── ingest.py        # 文档摄入流程
│   │   │   ├── llm.py           # LLM 调用（OpenAI / Mock）
│   │   │   ├── loader.py        # 文档加载（txt / md / pdf）
│   │   │   ├── splitter.py      # 文本切分
│   │   │   └── store.py         # 简易向量存储 + 关键词检索
│   │   └── llama/               # LlamaIndex 学习模块
│   │       └── crud.py          # VectorStoreIndex CRUD
│   ├── data/                    # 上传文件 & 索引数据
│   ├── eval.py                  # 自动评测脚本
│   ├── pyproject.toml           # Python 项目配置
│   └── .env.example             # 环境变量模板
├── frontend/
│   ├── src/
│   │   ├── App.vue              # 主界面（问答 + LlamaIndex CRUD）
│   │   ├── api.ts               # 前端 API 封装
│   │   ├── main.ts              # Vue 入口
│   │   └── style.css            # 全局样式
│   └── package.json
├── examples/
│   └── rag-notes.md             # 可上传测试的示例文档
├── .vscode/
│   └── launch.json              # VS Code 调试配置
└── README.md
```

---

## 快速开始

### 环境要求

- **Python** >= 3.11, < 3.12
- **Node.js** >= 18
- **uv** (Python 包管理工具)

```powershell
# 安装 uv（如未安装）
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 1. 启动后端

```powershell
cd backend
uv sync
uv run uvicorn backend.main:app --reload --log-level debug
```

后端运行在 **http://127.0.0.1:8000**

- Swagger API 文档：http://127.0.0.1:8000/docs
- ReDoc 文档：http://127.0.0.1:8000/redoc

### 2. 启动前端

另开一个终端：

```powershell
cd frontend
npm install
npm run dev
```

前端运行在 **http://127.0.0.1:5174**

---

## 配置 LLM（可选）

后端默认使用 Mock 回答，无需 API Key 即可跑通全流程。

要使用真实 OpenAI 模型，复制环境变量模板并填入 Key：

```powershell
cd backend
cp .env.example .env
```

编辑 `.env`：

```env
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini
```

重启后端即可生效。

---

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/health` | 健康检查 |
| `POST` | `/api/chat` | RAG 问答（支持 agent 模式） |
| `POST` | `/api/documents/upload` | 上传文档 (txt/md/pdf) |
| `GET` | `/api/documents` | 获取文档列表 |
| `DELETE` | `/api/documents/{doc_id}` | 删除文档 |
| `POST` | `/api/llama/documents` | 创建 LlamaIndex 文档 |
| `GET` | `/api/llama/documents` | 列出所有文档 |
| `GET` | `/api/llama/documents/{doc_id}` | 获取文档详情 |
| `PUT` | `/api/llama/documents/{doc_id}` | 更新文档 |
| `DELETE` | `/api/llama/documents/{doc_id}` | 删除文档 |
| `POST` | `/api/llama/search` | LlamaIndex 语义检索 |

---

## 评测

后端启动后，运行评测脚本：

```powershell
cd backend
uv run python eval.py
```

评测用关键词匹配检查回答质量，输出准确率和平均延迟。

---

## VS Code 调试

项目已包含 `.vscode/launch.json` 配置，支持断点调试：

1. 在 VS Code 中打开项目根目录
2. 在任意 `.py` 文件中打上断点
3. 按 `F5`，选择 **Debug Backend** 启动
4. 发送请求，代码将在断点处暂停

---

## LlamaIndex CRUD 学习

前端右侧的 **LlamaIndex CRUD** 面板可直接练习文档管理：

- **分类**：给文档设置 `category`，如 `rag`、`agent`、`eval`
- **新增**：创建文档 → `index.insert(...)`
- **查询**：列表查看，语义搜索 → `index.as_retriever(...).retrieve(...)`
- **修改**：编辑文档 → `index.update_ref_doc(...)`
- **删除**：删除文档 → `index.delete_ref_doc(..., delete_from_docstore=True)`

使用 `MockEmbedding`，无需真实模型 Key 即可体验索引和文档管理流程。

---

## 建议学习顺序

1. `frontend/src/api.ts` — 理解前端如何调接口
2. `backend/src/backend/routes/chat.py` — 理解请求如何进入后端
3. `backend/src/backend/rag/chain.py` — 理解 RAG prompt 拼接逻辑
4. `backend/src/backend/rag/ingest.py` — 理解文档上传后的切分与索引
5. `backend/src/backend/rag/agent.py` — 理解最简工具调用 (agent 模式)
6. `backend/src/backend/routes/llama.py` — 理解 LlamaIndex CRUD API
7. `backend/src/backend/llama/crud.py` — 理解 LlamaIndex 的 insert/update/delete/retrieve
8. `backend/eval.py` — 理解评测脚本的基本形态

---

## License

MIT
