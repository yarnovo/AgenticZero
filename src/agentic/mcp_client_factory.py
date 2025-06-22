"""MCP客户端工厂，用于创建MCP客户端实例。"""

import logging
from typing import Any

from .mcp_session_manager import MCPClientInterface
from .settings import MCPServerSettings

logger = logging.getLogger(__name__)


class DefaultMCPClient(MCPClientInterface):
    """默认MCP客户端实现，使用官方MCP SDK。"""

    def __init__(self):
        """初始化默认MCP客户端。"""
        self.server_connection = None
        self._connected = False

    async def connect(self, config: MCPServerSettings) -> None:
        """连接到MCP服务器。"""
        try:
            from .mcp_client import MCPServerConnection

            self.server_connection = MCPServerConnection("default", config)
            await self.server_connection.connect()
            self._connected = True
            logger.info(f"连接到MCP服务器: {config.command}")
        except Exception as e:
            logger.error(f"连接MCP服务器失败: {e}")
            raise

    async def disconnect(self) -> None:
        """断开MCP服务器连接。"""
        if self.server_connection:
            await self.server_connection.disconnect()
            self.server_connection = None
            self._connected = False
            logger.info("断开MCP服务器连接")

    async def list_tools(self) -> list[dict[str, Any]]:
        """获取可用工具列表。"""
        if not self._connected or not self.server_connection:
            raise RuntimeError("MCP客户端未连接")

        try:
            tools = await self.server_connection.list_tools()
            return tools
        except Exception as e:
            logger.error(f"获取工具列表失败: {e}")
            raise

    async def call_tool(
        self, tool_name: str, arguments: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """调用工具。"""
        if not self._connected or not self.server_connection:
            raise RuntimeError("MCP客户端未连接")

        try:
            result = await self.server_connection.call_tool(tool_name, arguments)
            return result
        except Exception as e:
            logger.error(f"调用工具失败: {e}")
            raise

    async def is_connected(self) -> bool:
        """检查连接状态。"""
        return self._connected


class MCPClientFactory:
    """MCP客户端工厂。"""

    @staticmethod
    def create_client() -> MCPClientInterface:
        """创建默认MCP客户端。

        Returns:
            MCP客户端实例
        """
        return DefaultMCPClient()
