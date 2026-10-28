from fastapi import APIRouter

from backend.agents.chat_agent import run_chat_agent
from backend.schemas.chat import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["聊天"])


@router.post("/", response_model=ChatResponse)
def chat(body: ChatRequest):
    """接收用户问题，返回 AI 回答"""
    answer = run_chat_agent(body.question)
    return ChatResponse(answer=answer)
