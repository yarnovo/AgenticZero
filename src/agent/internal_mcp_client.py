"""内置MCP客户端，用于连接内部MCP服务（如记忆服务）。"""

import logging
from typing import Any

from .mcp_session_manager import MCPClientInterface
from .settings import MCPServerSettings

logger = logging.getLogger(__name__)


class InternalMCPClient(MCPClientInterface):
    """内部MCP客户端，直接调用内部服务器实例。"""

    def __init__(self, server_instance: Any):
        """初始化内部MCP客户端。

        Args:
            server_instance: 内部服务器实例（如MemoryMCPServer）
        """
        self.server = server_instance
        self._connected = False

    async def connect(self, config: MCPServerSettings) -> None:
        """连接到内部服务器（实际上只是设置连接状态）。"""
        self._connected = True
        logger.debug("内部MCP客户端已连接")

    async def disconnect(self) -> None:
        """断开连接。"""
        self._connected = False
        logger.debug("内部MCP客户端已断开")

    async def list_tools(self) -> list[dict[str, Any]]:
        """获取工具列表。"""
        if not self._connected:
            raise RuntimeError("内部MCP客户端未连接")

        # 直接调用服务器的list_tools
        tools = await self.server.server.list_tools()

        # 转换工具格式
        tool_list = []
        for tool in tools:
            tool_dict = {
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.inputSchema,
            }
            tool_list.append(tool_dict)

        return tool_list

    async def call_tool(
        self, tool_name: str, arguments: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """调用工具。"""
        if not self._connected:
            raise RuntimeError("内部MCP客户端未连接")

        # 直接调用服务器的call_tool
        result = await self.server.server.call_tool(tool_name, arguments)

        # 转换结果格式
        content_list = []
        for content in result:
            if hasattr(content, "text"):
                content_list.append({"type": "text", "text": content.text})

        return {"content": content_list}

    async def send_notification(self, method: str, params: dict[str, Any]) -> None:
        """发送通知（内部服务不支持）。"""
        logger.warning(f"内部MCP客户端不支持发送通知: {method}")

    async def list_resources(self) -> list[dict[str, Any]]:
        """获取资源列表（内部服务不支持）。"""
        return []

    async def read_resource(self, uri: str) -> dict[str, Any]:
        """读取资源（内部服务不支持）。"""
        raise NotImplementedError("内部MCP客户端不支持资源操作")

    async def list_prompts(self) -> list[dict[str, Any]]:
        """获取提示列表（内部服务不支持）。"""
        return []

    async def get_prompt(
        self, name: str, arguments: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """获取提示（内部服务不支持）。"""
        raise NotImplementedError("内部MCP客户端不支持提示操作")

    async def is_connected(self) -> bool:
        """检查连接状态。"""
        return self._connected
