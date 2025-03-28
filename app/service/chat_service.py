from autogen_agentchat.messages import TextMessage
from app.schemas.chat import ChatMessage
from autogen_core import CancellationToken
import json
from typing import AsyncGenerator, List
from autogen_agentchat.messages import ChatMessage
import asyncio
from typing import Dict
from autogen_agentchat.agents import AssistantAgent
from app.service.gaode import (
    geocode_and_extract_locations,
    get_amap_driving_directions,
)
from typing import Sequence
from autogen_agentchat.agents import BaseChatAgent
from autogen_agentchat.base import Response
from autogen_agentchat.messages import AgentEvent
from autogen_core.model_context import UnboundedChatCompletionContext
from autogen_core.models import AssistantMessage, RequestUsage, UserMessage
from google import genai
from google.genai import types
import os


class GeminiAssistantAgent(BaseChatAgent):
    """
    一个基于 Google Gemini 模型的聊天代理，提供带有工具使用能力的帮助。
    """

    def __init__(
        self,
        name: str,
        description: str = "An agent that provides assistance with ability to use tools.",
        model: str = "gemini-2.0-flash",
        api_key: str = os.environ["GEMINI_API_KEY"],
        system_message: str
        | None = "You are a helpful assistant that can respond to messages. Reply with TERMINATE when the task has been completed.",
    ):
        """
        初始化 GeminiAssistantAgent。

        :param name: 代理的名称
        :param description: 代理的描述，默认为 "An agent that provides assistance with ability to use tools."
        :param model: 使用的 Gemini 模型名称，默认为 "gemini-1.5-flash-002"
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
        self._tools = [
            geocode_and_extract_locations,
            get_amap_driving_directions,
        ]

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
                tools=self._tools
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
        await self._model_context.clear()  # 清除模型上下文，重置对话状态


sessions: Dict[str, AssistantAgent] = {}
session_lock = asyncio.Lock()


async def get_agent(user_id: str) -> AssistantAgent:
    async with session_lock:
        if user_id not in sessions:
            sessions[user_id] = GeminiAssistantAgent(
                name=f"assistant_{user_id}",
                system_message=(
                    "你是一个物流配送管理助手。\n"
                    "请根据用户的问题，使用可用的工具来给出回答。\n\n"
                    "**导航与路线规划指南：**\n"
                    "1.  **识别需求：** 识别起点、终点和途经点。\n"
                    "2.  **获取坐标：** 对每个地点使用 `geocode_and_extract_locations_json_async` 获取坐标。此工具返回包含经纬度的 JSON *字符串* (例如 `'{\"longitude\": 121.5, \"latitude\": 31.2}'`) 或空对象字符串 `'{}'`。\n"
                    "3.  **处理坐标：** 从返回的 JSON 字符串中解析出经纬度。如果获取失败 (返回 '{}')，告知用户。\n"
                    "4.  **格式化坐标：** 将经纬度构造成 '经度,纬度' 格式的字符串 (例如 `'121.5,31.2'`)。\n"
                    "5.  **处理途经点：** 将多个途经点的 '经度,纬度' 字符串用英文分号 (`;`) 连接 (例如 `'lon1,lat1;lon2,lat2'`)。\n"
                    "6.  **调用路线规划：** 使用 `get_amap_driving_directions` 工具，传入格式化后的 `origin`, `destination`, 和可选的 `waypoints` 坐标字符串。\n"
                    "7.  **整合并回答：** `get_amap_driving_directions` 返回包含路线详情或错误的 JSON *字符串*。解析此字符串，提取关键信息（距离、时间、主要步骤），并以清晰、友好的方式回复用户。**注意：不要直接输出原始 JSON 字符串给用户。**\n\n"
                    "**其他情况：** 对于非导航类问题，直接回答。"
                ),
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
