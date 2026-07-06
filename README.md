# Mini RAG Agent

一个用于学习 **Python + LangChain + LlamaIndex + Vue 3 前后端联调** 的小型 RAG 项目。

它故意做得不复杂：能上传文档、提问、看引用来源，也能在右侧面板练习 LlamaIndex 文档分类和增删改查。

## 技术栈

| 层级 | 技术 |
| --- | --- |
| Frontend | Vue 3, TypeScript, Vite, Element Plus, Axios |
| Backend | Python 3.11, FastAPI, uv |
| RAG | LangChain text splitter, 本地关键词检索 |
| LlamaIndex | VectorStoreIndex 文档 CRUD |
| LLM | OpenAI 可选；未配置 key 时使用 mock 回答 |
| Eval/Test | httpx, pytest |

## 功能

- 文档上传：支持 `.txt`、`.md`、`.pdf`
- RAG 问答：检索文档片段，拼接 prompt，生成回答
- Agent 示例：演示最小工具调用
- LlamaIndex CRUD：分类、创建、查询、更新、删除、检索
- 评测脚本：批量请求接口并统计关键词命中
- 后端测试：覆盖 health、chat、documents、llama API

## 启动

后端：

```powershell
cd backend
uv sync
uv run uvicorn backend.main:app --reload
```

前端：

```powershell
cd frontend
npm install
npm run dev
```

访问：

- Frontend: http://127.0.0.1:5174
- API docs: http://127.0.0.1:8000/docs

## 可选：配置真实 LLM

默认不需要 API Key，会返回 mock 回答。要接真实 OpenAI 模型：

```powershell
cd backend
copy .env.example .env
```

编辑 `backend/.env`：

```env
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini
```

重启后端即可。

## 示例文档

可以上传：

```text
examples/rag-notes.md
```

然后提问：

```text
RAG 的核心流程是什么？
```

## LlamaIndex 学习点

右侧 `LlamaIndex CRUD` 面板对应这些后端方法：

| 操作 | LlamaIndex 方法 |
| --- | --- |
| 新增 | `index.insert(...)` |
| 检索 | `index.as_retriever(...).retrieve(...)` |
| 更新 | `index.update_ref_doc(...)` |
| 删除 | `index.delete_ref_doc(..., delete_from_docstore=True)` |

实现位置：

- `backend/src/backend/routes/llama.py`
- `backend/src/backend/llama/crud.py`
- `frontend/src/api.ts`
- `frontend/src/App.vue`

项目使用 `MockEmbedding`，所以 LlamaIndex CRUD 不依赖真实模型 key。

## 测试

```powershell
cd backend
uv run pytest
```

评测脚本：

```powershell
cd backend
uv run python eval.py
```

## 项目结构

```text
mini-rag-agent/
  backend/
    src/backend/
      routes/
      rag/
      llama/
    src/tests/
    eval.py
  frontend/
    src/
      App.vue
      api.ts
  examples/
    rag-notes.md
```

## License

MIT
