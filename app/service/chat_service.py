from app.core.config import settings
from autogen_agentchat.messages import TextMessage
from app.schemas.chat import ChatMessage
from autogen_core import CancellationToken
import json
from typing import AsyncGenerator
from typing import Sequence  # 用于异步生成器和序列类型
from autogen_agentchat.agents import BaseChatAgent
from autogen_agentchat.base import Response
from autogen_agentchat.messages import AgentEvent, ChatMessage
from autogen_core.model_context import UnboundedChatCompletionContext
from autogen_core.models import AssistantMessage, RequestUsage, UserMessage
from google import genai
from google.genai import types
import asyncio
from typing import Dict


class GeminiAssistantAgent(BaseChatAgent):
    """
    一个基于 Google Gemini 模型的聊天代理，提供带有工具使用能力的帮助。
    """

    def __init__(
        self,
        name: str,
        description: str = "An agent that provides assistance with ability to use tools.",
        model: str = "gemini-2.0-flash",
        api_key: str = settings.GEMINI_API_KEY,
        system_message: str
        | None = "你是物流管理系统的智能助手，请根据用户的问题给出最合适的回答。",
    ):
        """
        初始化 GeminiAssistantAgent。

        :param name: 代理的名称
        :param description: 代理的描述，默认为 "An agent that provides assistance with ability to use tools."
        :param model: 使用的 Gemini 模型名称，默认为 "gemini-2.0-flash"
        :param api_key: Gemini API 密钥，默认为环境变量 "GEMINI_API_KEY" 的值
        :param system_message: 系统消息，默认为助手的基本指令
        """
        super().__init__(name=name, description=description)  # 调用父类的初始化方法
        self._model_context = (
            UnboundedChatCompletionContext()
        )  # 初始化模型上下文，用于存储对话历史
        self._model_client = genai.Client(
            api_key=api_key
        )  # 初始化 Gemini 客户端，用于调用 API
        self._system_message = system_message  # 保存系统消息，作为助手的初始指令
        self._model = model  # 保存模型名称

    @property
    def produced_message_types(self) -> Sequence[type[ChatMessage]]:
        """
        返回代理产生的消息类型。

        :return: 消息类型的序列
        """
        return (TextMessage,)  # 代理只产生文本消息

    async def on_messages(
        self, messages: Sequence[ChatMessage], cancellation_token: CancellationToken
    ) -> Response:
        """
        处理接收到的消息并返回响应。

        此方法调用 on_messages_stream 并处理流式响应。

        :param messages: 接收到的消息序列
        :param cancellation_token: 取消令牌
        :return: 响应对象
        """
        final_response = None  # 初始化最终响应变量
        async for message in self.on_messages_stream(
            messages, cancellation_token
        ):  # 遍历流式响应
            if isinstance(message, Response):  # 如果消息是 Response 类型
                final_response = message  # 保存最终响应

        if final_response is None:  # 如果没有获取到最终响应
            raise AssertionError(
                "The stream should have returned the final result."
            )  # 抛出断言错误

        return final_response  # 返回最终响应

    async def on_messages_stream(
        self, messages: Sequence[ChatMessage], cancellation_token: CancellationToken
    ) -> AsyncGenerator[AgentEvent | ChatMessage | Response, None]:
        """
        以流式方式处理消息并生成响应。

        此方法将消息添加到模型上下文中，生成响应，并返回一个 Response 对象。

        :param messages: 接收到的消息序列
        :param cancellation_token: 取消令牌
        :yield: 代理事件、聊天消息或响应
        """
        # 将消息添加到模型上下文
        for msg in messages:
            await self._model_context.add_message(
                UserMessage(content=msg.content, source=msg.source)
            )

        # 获取对话历史
        history = [
            (
                msg.source if hasattr(msg, "source") else "system"
            )  # 获取消息来源，默认为 "system"
            + ": "
            + (
                msg.content if isinstance(msg.content, str) else ""
            )  # 获取消息内容，确保是字符串
            + "\n"
            for msg in await self._model_context.get_messages()  # 遍历模型上下文中的消息
        ]

        # 使用 Gemini 生成响应
        response = self._model_client.models.generate_content(
            model=self._model,  # 指定使用的模型
            contents=f"History: {history}\nGiven the history, please provide a response",  # 提供对话历史和生成指令
            config=types.GenerateContentConfig(
                system_instruction=self._system_message,  # 系统指令
                temperature=0.3,  # 控制生成内容的随机性，较低的值使输出更确定
            ),
        )

        # 创建使用元数据
        usage = RequestUsage(
            prompt_tokens=response.usage_metadata.prompt_token_count,  # 输入的令牌数
            completion_tokens=response.usage_metadata.candidates_token_count,  # 生成的令牌数
        )

        # 将响应添加到模型上下文
        await self._model_context.add_message(
            AssistantMessage(content=response.text, source=self.name)
        )

        # yield 最终响应
        yield Response(
            chat_message=TextMessage(
                content=response.text, source=self.name, models_usage=usage
            ),  # 响应消息
            inner_messages=[],  # 内部消息列表，当前为空
        )

    async def on_reset(self, cancellation_token: CancellationToken) -> None:
        """
        通过清除模型上下文来重置助手。

        :param cancellation_token: 取消令牌
        """
        await self._model_context.clear()


sessions: Dict[str, GeminiAssistantAgent] = {}
session_lock = asyncio.Lock()


async def get_agent(user_id: str) -> GeminiAssistantAgent:
    async with session_lock:
        if user_id not in sessions:
            sessions[user_id] = GeminiAssistantAgent(
                name=f"gemini_assistant_{user_id}",
            )
        return sessions[user_id]


async def chat(message: ChatMessage, user_id: str) -> AsyncGenerator[str, None]:
    """
    处理用户聊天消息并生成响应

    Args:
        message: 用户消息对象

    Returns:
        AsyncGenerator[str, None]: 流式生成的响应
    """
    gemini_assistant = await get_agent(user_id)

    user_message = TextMessage(content=message.message, source="user")

    # 使用历史记录创建流式响应
    async for msg in gemini_assistant.on_messages_stream(
        [user_message], cancellation_token=CancellationToken()
    ):
        # 解析消息内容
        try:
            # 解析JSON格式的消息
            parsed_message = json.loads(msg.chat_message.content)
            chunk = parsed_message.get("message", "")

            # 返回每个文本块
            if chunk:
                yield chunk
        except json.JSONDecodeError:
            # 如果不是JSON格式，尝试直接返回内容
            yield msg.chat_message.content


async def reset_chat(user_id: str) -> AsyncGenerator[str, None]:
    gemini_assistant = await get_agent(user_id)
    await gemini_assistant.on_reset(CancellationToken())
    return "Chat reset successfully."
