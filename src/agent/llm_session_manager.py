"""大模型会话管理模块，负责管理与各种大模型提供商的会话。"""

import logging
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .model_provider import ModelProvider

logger = logging.getLogger(__name__)


class LLMSessionInterface(ABC):
    """大模型会话抽象接口。"""

    @abstractmethod
    async def chat(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """与大模型进行对话。

        Args:
            messages: 消息列表
            tools: 可用工具列表

        Returns:
            大模型响应
        """

    @abstractmethod
    async def chat_stream(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
    ) -> AsyncIterator[dict[str, Any]]:
        """与大模型进行流式对话。

        Args:
            messages: 消息列表
            tools: 可用工具列表

        Yields:
            大模型响应片段，可能包含：
            - {"type": "content", "content": str} - 内容片段
            - {"type": "tool_calls", "tool_calls": list} - 工具调用
            - {"type": "error", "error": str} - 错误信息
        """

    @abstractmethod
    async def initialize(self) -> None:
        """初始化会话。"""

    @abstractmethod
    async def close(self) -> None:
        """关闭会话。"""


class LLMSessionManager:
    """大模型会话管理器，管理与大模型的会话生命周期。"""

    def __init__(self, model_provider: "ModelProvider"):
        """初始化会话管理器。

        Args:
            model_provider: 模型提供商实例
        """
        self.model_provider = model_provider
        self.session: LLMSessionInterface | None = None
        self._initialized = False

    async def initialize(self) -> None:
        """初始化会话管理器。"""
        if self._initialized:
            return

        self.session = await self.model_provider.create_session()
        await self.session.initialize()
        self._initialized = True
        logger.info("大模型会话管理器已初始化")

    async def chat(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """发起与大模型的对话。

        Args:
            messages: 消息列表
            tools: 可用工具列表

        Returns:
            大模型响应

        Raises:
            RuntimeError: 会话未初始化时抛出
        """
        if not self._initialized or not self.session:
            raise RuntimeError("会话管理器未初始化，请先调用 initialize() 方法")

        logger.debug(f"发起大模型对话，消息数: {len(messages)}")
        response = await self.session.chat(messages, tools)
        logger.debug("大模型对话完成")
        return response

    async def chat_stream(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
    ) -> AsyncIterator[dict[str, Any]]:
        """发起与大模型的流式对话。

        Args:
            messages: 消息列表
            tools: 可用工具列表

        Yields:
            大模型响应片段

        Raises:
            RuntimeError: 会话未初始化时抛出
        """
        if not self._initialized or not self.session:
            raise RuntimeError("会话管理器未初始化，请先调用 initialize() 方法")

        logger.debug(f"发起大模型流式对话，消息数: {len(messages)}")
        async for chunk in self.session.chat_stream(messages, tools):
            yield chunk
        logger.debug("大模型流式对话完成")

    async def close(self) -> None:
        """关闭会话管理器。"""
        if self.session:
            await self.session.close()
            self.session = None
        self._initialized = False
        logger.info("大模型会话管理器已关闭")

    @property
    def is_initialized(self) -> bool:
        """检查会话是否已初始化。"""
        return self._initialized
