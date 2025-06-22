"""MCP会话管理模块，负责管理与MCP服务器的会话和通信。"""

import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from .settings import MCPServerSettings

if TYPE_CHECKING:
    from .mcp_client_factory import MCPClientFactory

logger = logging.getLogger(__name__)


class MCPClientInterface(ABC):
    """MCP客户端抽象接口。"""

    @abstractmethod
    async def connect(self, config: MCPServerSettings) -> None:
        """连接到MCP服务器。

        Args:
            config: MCP服务器配置
        """

    @abstractmethod
    async def disconnect(self) -> None:
        """断开MCP服务器连接。"""

    @abstractmethod
    async def list_tools(self) -> list[dict[str, Any]]:
        """获取可用工具列表。

        Returns:
            工具列表
        """

    @abstractmethod
    async def call_tool(
        self, tool_name: str, arguments: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """调用工具。

        Args:
            tool_name: 工具名称
            arguments: 工具参数

        Returns:
            工具执行结果
        """

    @abstractmethod
    async def is_connected(self) -> bool:
        """检查连接状态。

        Returns:
            连接状态
        """


class MCPSession:
    """MCP会话，封装单个MCP服务器的连接和通信。"""

    def __init__(
        self, server_name: str, config: MCPServerSettings, client: MCPClientInterface
    ):
        """初始化MCP会话。

        Args:
            server_name: 服务器名称
            config: 服务器配置
            client: MCP客户端实例
        """
        self.server_name = server_name
        self.config = config
        self.client = client
        self._connected = False

    async def connect(self) -> None:
        """连接到MCP服务器。"""
        if self._connected:
            logger.warning(f"MCP会话 {self.server_name} 已经连接")
            return

        try:
            await self.client.connect(self.config)
            self._connected = True
            logger.info(f"MCP会话 {self.server_name} 连接成功")
        except Exception as e:
            logger.error(f"MCP会话 {self.server_name} 连接失败: {e}")
            raise

    async def disconnect(self) -> None:
        """断开MCP服务器连接。"""
        if not self._connected:
            return

        try:
            await self.client.disconnect()
            self._connected = False
            logger.info(f"MCP会话 {self.server_name} 已断开连接")
        except Exception as e:
            logger.error(f"MCP会话 {self.server_name} 断开连接时出错: {e}")

    async def list_tools(self) -> list[dict[str, Any]]:
        """获取可用工具列表。

        Returns:
            工具列表

        Raises:
            RuntimeError: 会话未连接时抛出
        """
        if not self._connected:
            raise RuntimeError(f"MCP会话 {self.server_name} 未连接")

        try:
            tools = await self.client.list_tools()
            # 为工具添加命名空间前缀
            for tool in tools:
                tool["_server_name"] = self.server_name
                if "_namespaced_name" not in tool:
                    tool["_namespaced_name"] = (
                        f"{self.server_name}__{tool.get('name', 'unknown')}"
                    )
            return tools
        except Exception as e:
            logger.error(f"获取 {self.server_name} 工具列表失败: {e}")
            raise

    async def call_tool(
        self, tool_name: str, arguments: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """调用工具。

        Args:
            tool_name: 工具名称（不带命名空间前缀）
            arguments: 工具参数

        Returns:
            工具执行结果

        Raises:
            RuntimeError: 会话未连接时抛出
        """
        if not self._connected:
            raise RuntimeError(f"MCP会话 {self.server_name} 未连接")

        try:
            result = await self.client.call_tool(tool_name, arguments)
            logger.debug(f"工具 {tool_name} 在服务器 {self.server_name} 上执行成功")
            return result
        except Exception as e:
            logger.error(
                f"调用工具 {tool_name} 在服务器 {self.server_name} 上失败: {e}"
            )
            raise

    @property
    def is_connected(self) -> bool:
        """检查连接状态。"""
        return self._connected


class MCPSessionManager:
    """MCP会话管理器，管理多个MCP服务器的会话。"""

    def __init__(self):
        """初始化MCP会话管理器。"""
        self.sessions: dict[str, MCPSession] = {}
        self._client_factory: MCPClientFactory | None = None

    def set_client_factory(self, factory: "MCPClientFactory") -> None:
        """设置MCP客户端工厂。

        Args:
            factory: 客户端工厂实例
        """
        self._client_factory = factory

    async def add_server(self, server_name: str, config: MCPServerSettings) -> None:
        """添加MCP服务器。

        Args:
            server_name: 服务器名称
            config: 服务器配置

        Raises:
            RuntimeError: 客户端工厂未设置时抛出
        """
        if not self._client_factory:
            raise RuntimeError("MCP客户端工厂未设置")

        if server_name in self.sessions:
            logger.warning(f"MCP服务器 {server_name} 已存在，将替换现有会话")
            await self.remove_server(server_name)

        # 创建客户端和会话
        client = self._client_factory.create_client()
        session = MCPSession(server_name, config, client)

        # 连接服务器
        await session.connect()
        self.sessions[server_name] = session
        logger.info(f"添加MCP服务器 {server_name}")

    async def remove_server(self, server_name: str) -> None:
        """移除MCP服务器。

        Args:
            server_name: 服务器名称
        """
        if server_name in self.sessions:
            session = self.sessions[server_name]
            await session.disconnect()
            del self.sessions[server_name]
            logger.info(f"移除MCP服务器 {server_name}")

    async def list_all_tools(self) -> list[dict[str, Any]]:
        """获取所有服务器的工具列表。

        Returns:
            所有工具的列表
        """
        all_tools = []
        for session in self.sessions.values():
            if session.is_connected:
                try:
                    tools = await session.list_tools()
                    all_tools.extend(tools)
                except Exception as e:
                    logger.error(f"获取服务器 {session.server_name} 工具列表失败: {e}")
        return all_tools

    async def call_tool(
        self, namespaced_tool_name: str, arguments: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """调用指定工具。

        Args:
            namespaced_tool_name: 带命名空间的工具名称（格式：server_name__tool_name）
            arguments: 工具参数

        Returns:
            工具执行结果

        Raises:
            ValueError: 工具名称格式错误或服务器不存在时抛出
        """
        # 解析命名空间工具名称
        if "__" not in namespaced_tool_name:
            raise ValueError(
                f"工具名称格式错误: {namespaced_tool_name}，应为 server_name__tool_name"
            )

        server_name, tool_name = namespaced_tool_name.split("__", 1)

        if server_name not in self.sessions:
            raise ValueError(f"MCP服务器 {server_name} 不存在")

        session = self.sessions[server_name]
        return await session.call_tool(tool_name, arguments)

    async def get_server_status(self) -> dict[str, dict[str, Any]]:
        """获取所有服务器的状态。

        Returns:
            服务器状态字典
        """
        status = {}
        for server_name, session in self.sessions.items():
            status[server_name] = {
                "connected": session.is_connected,
                "config": {
                    "command": session.config.command,
                    "args": session.config.args,
                },
            }
        return status

    async def close_all(self) -> None:
        """关闭所有MCP会话。"""
        for server_name in list(self.sessions.keys()):
            await self.remove_server(server_name)
        logger.info("所有MCP会话已关闭")

    def get_session(self, server_name: str) -> MCPSession | None:
        """获取指定服务器的会话。

        Args:
            server_name: 服务器名称

        Returns:
            MCP会话对象，如果不存在则返回None
        """
        return self.sessions.get(server_name)
