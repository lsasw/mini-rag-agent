from backend.rag.llm import complete
from backend.rag.store import search
from backend.schemas import ChatResponse


async def answer_with_rag(question: str) -> ChatResponse:
    matches = search(question)
    sources = [source for source, _ in matches]
    context = "\n\n".join(f"[{index + 1}] {text}" for index, (_, text) in enumerate(matches))

    if not context:
        context = "当前知识库没有检索到相关内容。"

    prompt = f"""你是一个学习型 RAG 助手。
请基于【检索上下文】回答用户问题。如果上下文不足，请明确说明。

【检索上下文】
{context}

【用户问题】
{question}
"""
    answer, mode = await complete(prompt)
    return ChatResponse(answer=answer, sources=sources, mode=f"rag:{mode}")
