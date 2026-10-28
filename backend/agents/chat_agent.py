from langchain_core.messages import HumanMessage, SystemMessage
from langchain_deepseek import ChatDeepSeek

from backend.agents.prompts import SYSTEM_PROMPT
from backend.core.config import settings


def run_chat_agent(question: str) -> str:
    """聊天 Agent 入口：使用 DeepSeek（ChatDeepSeek）回答用户问题。"""
    if not settings.deepseek_api_key:
        return (
            f"收到你的问题：{question}。"
            "目前这是一个模拟回答，请在 .env 中配置 DEEPSEEK_API_KEY 后接入真实模型。"
        )

    llm = ChatDeepSeek(
        model=settings.deepseek_model,
        api_key=settings.deepseek_api_key,
        api_base=settings.deepseek_api_base,
        temperature=0.7,
    )
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=question),
    ]
    response = llm.invoke(messages)
    content = response.content
    if isinstance(content, str):
        return content
    # 少数情况下 content 可能是分块列表，统一转成字符串
    return str(content)
