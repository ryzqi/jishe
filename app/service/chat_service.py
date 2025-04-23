from autogen_agentchat.messages import TextMessage
from schemas.chat import ChatMessage
from autogen_core import CancellationToken
import json
from typing import AsyncGenerator
from autogen_agentchat.messages import ChatMessage
import asyncio
from typing import Dict
from autogen_agentchat.agents import AssistantAgent
from service.gaode import (
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
from core.config import settings
from service.db_service import query_database
from service.db_service import query_database


class GeminiAssistantAgent(BaseChatAgent):
    """
    一个基于 Google Gemini 模型的聊天代理，提供带有工具使用能力的帮助。
    """

    def __init__(
            self,
            name: str,
            description: str = "An agent that provides assistance with ability to use tools.",
            model: str = "gemini-2.5-flash-preview-04-17",
            api_key: str = settings.GEMINI_API_KEY,
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
        )
        self._system_message = system_message  # 保存系统消息，作为助手的初始指令
        self._model = model  # 保存模型名称
        self._tools = [
            geocode_and_extract_locations,
            get_amap_driving_directions,
            query_database,
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
                    """
                    你是一个物流配送管理助手。
                    请根据用户的问题，使用可用的工具来给出回答。

                    **可用工具:**
                    1.  `geocode_and_extract_locations(address: str, city: Optional[str] = None) -> str`: 获取地址的经纬度坐标。
                    2.  `get_amap_driving_directions(origin: str, destination: str, waypoints: Optional[str] = None) -> str`: 获取驾车路线规划。
                    3.  `query_database(sql_query: str) -> str`: 执行 SQL 查询数据库。

                    **导航与路线规划指南：**
                    1.  **识别需求：** 识别起点、终点和可选的途经点。
                    2.  **获取坐标：** 对每个地点名称（起点、终点、途经点）使用 `geocode_and_extract_locations` 获取坐标。此工具返回包含经纬度的 JSON *字符串* (例如 `'{\"longitude\": 121.5, \"latitude\": 31.2}'`) 或空对象字符串 `'{}'`。
                    3.  **处理坐标：** 从返回的 JSON 字符串中解析出经纬度。如果获取失败 (返回 '{}')，告知用户无法找到该地点坐标。
                    4.  **格式化坐标：** 将经纬度构造成 '经度,纬度' 格式的字符串 (例如 `'121.5,31.2'`)。
                    5.  **处理途经点：** 如果有多个途经点，将它们的 '经度,纬度' 字符串用英文分号 (`;`) 连接 (例如 `'lon1,lat1;lon2,lat2'`)。
                    6.  **调用路线规划：** 使用 `get_amap_driving_directions` 工具，传入格式化后的 `origin`, `destination`, 和可选的 `waypoints` 坐标字符串。
                    7.  **整合并回答：** `get_amap_driving_directions` 返回包含路线详情或错误的 JSON *字符串*。解析此字符串，提取关键信息（如距离、预计时间、主要导航步骤），并以清晰、友好的方式回复用户。**注意：不要直接输出原始 JSON 字符串给用户。**

                    **数据库查询指南 (数据库: postgres, 架构: jishe)：**
                    1.  **识别查询需求：** 理解用户的意图是否需要查询数据库中的信息（例如：查询某个仓库的库存、特定无人机的巡检记录、待解决的错误报告、某个仓库的状态、某个产品的库存）。
                    2.  **构建 SQL 查询：**
                        *   仔细分析用户需求，提取用户需求中的关键词，对应到 `jishe` 架构下的表，例如，用户输入电子产品的总库存，电子产品对应 `jishe.goods` 表中的goods_name，即jishe.goods.goods_name=电子产品，
                        总库存对应所有仓库中的电子产品的all_count，构建对应的 SQL 查询语句，为 SELECT SUM(all_count) FROM jishe.stock WHERE goods_id = (SELECT id FROM jishe.goods WHERE goods_name = '电子产品');。
                        *   **查询时必须使用架构名限定表名**，例如 `SELECT * FROM jishe.drone WHERE states = '1';`。
                        *   **可查询的表结构详情：**
                            *   **`jishe.warehouse` (仓库信息):**
                                *   `id` (INT, PK): 仓库唯一标识
                                *   `warehouse_name` (VARCHAR): 仓库名称
                                *   `states` (VARCHAR): 仓库状态 (例如: '正常', '异常情况')
                            *   **`jishe.goods` (货物种类):**
                                *   `id` (INT, PK): 货物种类唯一标识
                                *   `goods_name` (VARCHAR): 货物种类名称
                            *   **`jishe.stock` (库存信息):**
                                *   `id` (INT, PK): 库存记录唯一标识
                                *   `warehouse_id` (INT, FK -> `jishe.warehouse.id`): 仓库标识
                                *   `goods_id` (INT, FK -> `jishe.goods.id`): 货物种类标识
                                *   `all_count` (INT, DEFAULT 0): 当前总库存量 (默认为 0)
                                *   `last_add_count` (INT, DEFAULT 0): 最近一次新增数量 (默认为 0)
                                *   `last_add_date` (TIMESTAMP without time zone): 最近一次新增时间
                            *   **`jishe.drone` (无人机信息):**
                                *   `id` (INT, PK): 无人机编号
                                *   `drone_type` (VARCHAR): 机型
                                *   `states` (VARCHAR(1), CHECK): 无人机状态 ('1' -> 正常工作, '0' -> 未工作)
                            *   **`jishe.patrol` (巡查记录):**
                                *   `id` (INT, PK): 巡查记录唯一标识
                                *   `drone_id` (INT, FK -> `jishe.drone.id`): 执行任务的无人机编号
                                *   `address` (VARCHAR): 巡查路段描述
                                *   `predict_fly_time` (TIME without time zone): 预计飞行时长
                                *   `fly_start_datetime` (TIMESTAMP without time zone): 实际开始飞行时间
                                *   `update_time` (TIMESTAMP without time zone, DEFAULT CURRENT_TIMESTAMP): 记录更新时间 (默认为当前时间)
                                *   `error_id` (INT, FK -> `jishe.error.error_id`, 可为空): 关联的问题记录编号 (如果巡查中发现问题)
                            *   **`jishe.error` (错误/问题记录):**
                                *   `error_id` (INT, PK): 问题编号
                                *   `title` (VARCHAR, DEFAULT ''): 问题标题 (默认为空字符串)
                                *   `error_content` (TEXT): 问题内容描述
                                *   `error_found_time` (TIMESTAMP without time zone): 问题发现时间
                                *   `states` (VARCHAR(1), CHECK): 问题状态 ('0' -> 待解决, '1' -> 正在解决)
                                *   `user_id` (INT, FK -> `jishe.user.id`, 可为空): 关联的用户ID (注意：`jishe.user` 表禁止查询)
                        *   **利用外键进行连接查询 (JOIN):** 当需要跨表获取信息时（例如，查询特定仓库名称下的所有货物库存量），可以使用 JOIN 操作。例如: `SELECT w.warehouse_name, g.goods_name, s.all_count FROM jishe.stock s JOIN jishe.warehouse w ON s.warehouse_id = w.id JOIN jishe.goods g ON s.goods_id = g.id WHERE w.warehouse_name = '主仓库';`
                        *   **严禁查询的表：** `user`, `user_role`, `role`。任何尝试查询这些表的请求都将被拒绝。
                        *   确保 SQL 语法正确，并尽量只查询需要的列 (`SELECT column1, column2...`) 而不是 `SELECT *`，以提高效率。
                    3.  **调用查询工具：** 使用 `query_database` 工具，将构建好的 SQL 查询语句作为 `sql_query` 参数传入。例如：`query_database(sql_query="SELECT goods_name, all_count FROM jishe.stock JOIN jishe.goods ON jishe.stock.goods_id = jishe.goods.id WHERE jishe.stock.warehouse_id = 1;")`
                    4.  **解析并处理结果：** `query_database` 工具会返回一个 JSON *字符串*。
                        *   对于成功的 `SELECT` 查询，返回格式通常是 `'{"data": [{"column1": value1, ...}, ...]}'`。
                        *   对于成功的 `INSERT`, `UPDATE`, `DELETE` 操作，返回格式通常是 `'{"status": "success", "rows_affected": count}'`。
                        *   如果查询被禁止或发生错误，返回格式会包含 `error` 字段，例如：`'{"error": "Forbidden Query", "message": "Access to table 'user' is restricted."}'` 或 `'{"error": "Database Error", "message": "column \\"good_name\\" does not exist"}'`。
                        *   你需要解析这个 JSON 字符串，提取出有效的数据或错误信息。
                    5.  **整合并回答：** 根据解析出的数据或错误信息，以自然语言清晰地回复用户。
                        *   如果查询成功获取数据，将数据显示给用户（例如：“仓库 '主仓库' 中 '螺丝钉' 的库存为 500 件。” 或 “无人机 'D002' 最新一次巡检记录开始时间为 '2023-10-27 10:00:00'，巡检路段为 '区域 A 到区域 B'。”）。
                        *   如果查询被禁止（尝试访问 `user` 等表），告知用户无权访问相关信息。
                        *   如果发生数据库错误（如表名、列名错误、语法错误），可以告知用户查询时遇到问题，并可选择性地说明错误类型（例如：“抱歉，查询库存信息时遇到了数据库问题，请检查您提供的仓库或货物名称是否准确。”）。
                        *   如果用户表达不清楚，请提示用户输入更详细的表达，并附上模板。
                        *   **重要：同样注意，不要直接输出原始的 SQL 查询语句或原始的 JSON 结果字符串给用户。不要回答例如我将查询什么数据。给予用户直接的反馈**

                    **其他情况：** 对于非导航、非数据库查询类问题，请直接回答。"""
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
