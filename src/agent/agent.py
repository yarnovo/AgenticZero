"""智能体实现，提供简单的输入输出接口。"""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from src.graph import GraphManager
from src.mcp import MCPServiceManager

from .core_engine import CoreEngine
from .internal_mcp_client import InternalMCPClient
from .llm_session_manager import LLMSessionManager
from .mcp_client_factory import MCPClientFactory
from .mcp_session_manager import MCPSessionManager
from .memory_manager import MemoryManager
from .memory_mcp_server import MemoryMCPServer
from .message_history_manager import MessageHistoryManager
from .model_provider import ModelProviderFactory
from .session_context_manager import SessionContextManager
from .settings import AgentSettings

logger = logging.getLogger(__name__)


class Agent:
    """智能体类，提供简单的输入输出接口，内部使用自驱动架构。"""

    def __init__(
        self,
        config: AgentSettings | dict[str, Any],
        conversation_id: str | None = None,
        storage_dir: str | None = None,
    ):
        """初始化智能体。

        Args:
            config: 智能体配置
            conversation_id: 对话ID（可选）
            storage_dir: 存储目录（可选，用于持久化）
        """
        if isinstance(config, dict):
            config = AgentSettings.from_dict(config)

        self.config = config
        self.name = config.name
        self.conversation_id = conversation_id or f"agent_{self.name}"
        self.storage_dir = storage_dir

        # 初始化各个组件
        self._initialize_components()

        if config.debug:
            logging.basicConfig(level=logging.DEBUG)

    def _initialize_components(self) -> None:
        """初始化各个组件。"""
        # 创建模型提供商
        model_provider = ModelProviderFactory.create_provider(self.config.llm_settings)

        # 创建大模型会话管理器
        self.llm_session_manager = LLMSessionManager(model_provider)

        # 创建MCP会话管理器
        self.mcp_session_manager = MCPSessionManager()
        mcp_client_factory = MCPClientFactory()
        self.mcp_session_manager.set_client_factory(mcp_client_factory)

        # 创建消息历史管理器
        if self.storage_dir:
            history_manager = MessageHistoryManager.create_file_manager(
                self.storage_dir
            )
        else:
            history_manager = MessageHistoryManager.create_memory_manager()

        # 创建记忆管理器
        self.memory_manager = MemoryManager.create_memory_manager()

        # 创建图管理器
        self.graph_manager = GraphManager()

        # 创建会话上下文管理器，注入记忆管理器
        self.context_manager = SessionContextManager(
            history_manager=history_manager, memory_manager=self.memory_manager
        )

        # 创建核心引擎
        self.core_engine = CoreEngine(
            llm_session_manager=self.llm_session_manager,
            mcp_session_manager=self.mcp_session_manager,
            context_manager=self.context_manager,
            max_iterations=self.config.max_iterations,
        )

    async def initialize(self) -> None:
        """初始化智能体。"""
        logger.info(f"正在初始化智能体: {self.name}")

        # 初始化核心引擎
        await self.core_engine.initialize()

        # 添加内置的记忆MCP服务器
        await self._add_internal_memory_server()

        # 添加内置的MCP服务管理器
        await self._add_internal_mcp_service()

        # 添加用户配置的MCP服务器
        for server_name, server_config in self.config.mcp_servers.items():
            await self.mcp_session_manager.add_server(server_name, server_config)

        # 创建或获取会话上下文
        context = await self.context_manager.get_context(self.conversation_id)
        if not context:
            await self.context_manager.create_context(
                self.conversation_id,
                self.config.instruction,
            )

        logger.info(f"智能体 {self.name} 已初始化")

    async def close(self) -> None:
        """关闭智能体并清理资源。"""
        await self.core_engine.close()
        logger.info(f"智能体 {self.name} 已关闭")

    @asynccontextmanager
    async def connect(self):
        """智能体生命周期的上下文管理器。"""
        try:
            await self.initialize()
            yield self
        finally:
            await self.close()

    async def run(self, user_input: str, max_iterations: int | None = None) -> str:
        """运行智能体处理用户输入。

        Args:
            user_input: 用户输入
            max_iterations: 最大迭代次数（可选）

        Returns:
            智能体的最终响应
        """
        return await self.core_engine.process_input(
            user_input, self.conversation_id, max_iterations
        )

    async def run_stream(
        self, user_input: str, max_iterations: int | None = None
    ) -> AsyncIterator[dict[str, Any]]:
        """以流式方式运行智能体处理用户输入。

        Args:
            user_input: 用户输入
            max_iterations: 最大迭代次数（可选）

        Yields:
            流式响应片段，包含：
            - {"type": "content", "content": str} - 内容片段
            - {"type": "tool_call", "tool": str, "arguments": dict} - 工具调用
            - {"type": "tool_result", "tool": str, "result": dict} - 工具结果
            - {"type": "iteration", "current": int, "max": int} - 迭代信息
            - {"type": "complete", "final_response": str} - 完成标记
            - {"type": "error", "error": str} - 错误信息
        """
        async for chunk in self.core_engine.process_input_stream(
            user_input, self.conversation_id, max_iterations
        ):
            yield chunk

    async def get_status(self) -> dict[str, Any]:
        """获取智能体状态。

        Returns:
            状态信息字典
        """
        engine_status = await self.core_engine.get_engine_status()

        context = await self.context_manager.get_context(self.conversation_id)
        context_info = {}
        if context:
            context_info = {
                "message_count": context.get_message_count(),
                "token_estimate": context.get_token_estimate(),
            }

        return {
            "name": self.name,
            "conversation_id": self.conversation_id,
            "config": {
                "instruction": self.config.instruction,
                "max_iterations": self.config.max_iterations,
                "mcp_servers": list(self.config.mcp_servers.keys()),
                "llm_provider": self.config.llm_settings.provider,
                "llm_model": self.config.llm_settings.model,
            },
            "context": context_info,
            "engine": engine_status,
        }

    async def clear_history(self, keep_system: bool = True) -> None:
        """清除对话历史。

        Args:
            keep_system: 是否保留系统消息
        """
        context = await self.context_manager.get_context(self.conversation_id)
        if context:
            context.clear_history(keep_system)
            await self.context_manager.update_context(context)
            logger.info(f"清除对话历史: {self.conversation_id}")

    async def get_history(self) -> list[dict[str, str]]:
        """获取对话历史。

        Returns:
            消息列表
        """
        context = await self.context_manager.get_context(self.conversation_id)
        if context:
            return context.get_current_messages()
        return []

    def set_conversation_id(self, conversation_id: str) -> None:
        """设置对话ID。

        Args:
            conversation_id: 新的对话ID
        """
        self.conversation_id = conversation_id
        logger.info(f"切换到对话: {conversation_id}")

    async def list_conversations(self) -> list[str]:
        """列出所有对话。

        Returns:
            对话ID列表
        """
        return await self.context_manager.list_contexts()

    async def _add_internal_memory_server(self) -> None:
        """添加内置的记忆MCP服务器。"""
        # 创建记忆MCP服务器实例
        memory_server = MemoryMCPServer(self.memory_manager)

        # 创建内部MCP客户端
        internal_client = InternalMCPClient(memory_server)

        # 使用特殊配置添加到MCP会话管理器
        from .settings import MCPServerSettings

        internal_config = MCPServerSettings(
            name="memory",
            command="internal:memory",
            args=[],
            env={},
        )

        # 直接创建会话并添加
        from .mcp_session_manager import MCPSession

        session = MCPSession("memory", internal_config, internal_client)
        await session.connect()
        self.mcp_session_manager.sessions["memory"] = session

        logger.info("已添加内置记忆MCP服务器")

    async def _add_internal_mcp_service(self) -> None:
        """添加内置的 MCP 服务管理器。"""
        # 创建 MCP 服务管理器实例
        mcp_service = MCPServiceManager(graph_manager=self.graph_manager)

        # 创建内部 MCP 客户端
        internal_client = InternalMCPClient(mcp_service)

        # 使用特殊配置添加到 MCP 会话管理器
        from .settings import MCPServerSettings

        internal_config = MCPServerSettings(
            name="mcp_service_manager",
            command="internal:mcp_service",
            args=[],
            env={},
        )

        # 直接创建会话并添加
        from .mcp_session_manager import MCPSession

        session = MCPSession("mcp_service_manager", internal_config, internal_client)
        await session.connect()
        self.mcp_session_manager.sessions["mcp_service_manager"] = session

        logger.info("已添加内置 MCP 服务管理器")
