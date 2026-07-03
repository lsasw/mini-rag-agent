from langchain_openai import ChatOpenAI

from backend.config import get_settings


async def complete(prompt: str) -> tuple[str, str]:
    settings = get_settings()
    if not settings.openai_api_key:
        answer = (
            "这是本地 mock 回答，因为还没有配置 OPENAI_API_KEY。\n\n"
            "我已经收到问题和检索上下文。你可以先用它学习前后端联调、RAG 流程和评测脚本；"
            "配置真实模型后，这里会返回大模型生成的答案。"
        )
        return answer, "mock"

    llm = ChatOpenAI(model=settings.openai_model, temperature=0.2, api_key=settings.openai_api_key)
    result = await llm.ainvoke(prompt)
    return str(result.content), settings.openai_model
