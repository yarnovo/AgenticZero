"""MCP 客户端抽象接口定义。"""

from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from typing import Any, Protocol


class Tool(Protocol):
    """工具协议定义。"""

    name: str
    description: str
    parameters: dict[str, Any]


class MCPClientInterface(ABC):
    """MCP 客户端抽象接口。

    定义了与 MCP 服务器交互的标准接口，
    允许不同的实现方式（如直接连接、HTTP、gRPC 等）
    """

    @abstractmethod
    async def list_tools(self) -> list[dict[str, Any]]:
        """列出所有可用的工具。

        Returns:
            工具列表，每个工具包含名称、描述和参数模式
        """

    @abstractmethod
    async def call_tool(
        self, tool_name: str, arguments: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """调用指定的工具。

        Args:
            tool_name: 工具名称（可能包含命名空间）
            arguments: 工具参数

        Returns:
            工具执行结果
        """

    @abstractmethod
    async def initialize(self) -> None:
        """初始化客户端连接。"""

    @abstractmethod
    async def close(self) -> None:
        """关闭客户端连接。"""

    @asynccontextmanager
    async def connect(self):  # type: ignore[misc]
        """上下文管理器，用于管理连接生命周期。"""
        try:
            await self.initialize()
            yield self
        finally:
            await self.close()


class MCPServerConfig(Protocol):
    """MCP 服务器配置协议。"""

    name: str
    command: str
    args: list[str]
    env: dict[str, str]


class MCPClientFactory(Protocol):
    """MCP 客户端工厂协议。

    用于创建 MCP 客户端实例的工厂接口
    """

    def create_client(self, servers: dict[str, MCPServerConfig]) -> MCPClientInterface:
        """创建 MCP 客户端实例。

        Args:
            servers: 服务器配置字典

        Returns:
            MCP 客户端实例
        """
        ...
