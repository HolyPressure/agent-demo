from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, description="用户问题")


class ChatResponse(BaseModel):
    answer: str
