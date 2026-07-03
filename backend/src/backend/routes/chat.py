from fastapi import APIRouter

from backend.rag.agent import answer_with_agent
from backend.rag.chain import answer_with_rag
from backend.schemas import ChatRequest, ChatResponse

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    if request.use_agent:
        return await answer_with_agent(request.message)
    return await answer_with_rag(request.message)
