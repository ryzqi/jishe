from pydantic import BaseModel


class ChatMessage(BaseModel):
    """
    聊天消息
    """

    message: str


class ChatResponse(BaseModel):
    """
    聊天响应
    """

    message: str
    role: str
