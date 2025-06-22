"""MCP 客户端的官方 SDK 实现。"""

import logging
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import CallToolResult, EmbeddedResource, ImageContent, TextContent, Tool

from .config import MCPServerConfig
from .mcp_interface import MCPClientInterface

logger = logging.getLogger(__name__)


class MCPServerConnection:
    """单个 MCP 服务器连接的封装。"""

    def __init__(self, name: str, config: MCPServerConfig) -> None:
        self.name = name
        self.config = config
        self.session: ClientSession | None = None
        self._client = None
        self._read_task = None
        self._write_task = None

    async def connect(self) -> None:
        """连接到 MCP 服务器。"""
        logger.debug(f"正在连接到 MCP 服务器 {self.name}")

        # 创建服务器参数
        server_params = StdioServerParameters(
            command=self.config.command, args=self.config.args, env=self.config.env,
        )

        # 使用官方 SDK 创建客户端
        self._client = stdio_client(server_params)
        self._read_task, self._write_task = await self._client.__aenter__()

        # 初始化会话
        self.session = await self._client.initialize()

        logger.info(f"已连接到 MCP 服务器: {self.name}")
        logger.debug(f"服务器能力: {self.session.server_info}")

    async def disconnect(self) -> None:
        """断开与 MCP 服务器的连接。"""
        if self._client:
            await self._client.__aexit__(None, None, None)
            self._client = None
            self.session = None

        logger.info(f"已断开与 MCP 服务器的连接: {self.name}")

    async def list_tools(self) -> list[Tool]:
        """列出服务器提供的工具。"""
        if not self.session:
            raise RuntimeError(f"未连接到服务器 {self.name}")

        result = await self.session.list_tools()
        return result.tools

    async def call_tool(
        self, name: str, arguments: dict[str, Any] | None = None,
    ) -> CallToolResult:
        """调用服务器上的工具。"""
        if not self.session:
            raise RuntimeError(f"未连接到服务器 {self.name}")

        result = await self.session.call_tool(name, arguments or {})
        return result


class DefaultMCPClient(MCPClientInterface):
    """使用官方 MCP SDK 的客户端实现。"""

    def __init__(self) -> None:
        self.servers: dict[str, MCPServerConnection] = {}
        self._tools_cache: list[dict[str, Any]] | None = None

    async def add_server(self, name: str, config: MCPServerConfig) -> None:
        """添加并连接到 MCP 服务器。"""
        if name in self.servers:
            logger.warning(f"服务器 {name} 已存在，正在替换...")
            await self.remove_server(name)

        server = MCPServerConnection(name, config)
        await server.connect()
        self.servers[name] = server

        # 清除工具缓存
        self._tools_cache = None

    async def remove_server(self, name: str) -> None:
        """移除并断开与 MCP 服务器的连接。"""
        if name in self.servers:
            await self.servers[name].disconnect()
            del self.servers[name]
            self._tools_cache = None

    async def list_tools(self) -> list[dict[str, Any]]:
        """列出所有连接服务器的所有工具。"""
        if self._tools_cache is not None:
            return self._tools_cache

        all_tools = []
        for server_name, server in self.servers.items():
            tools = await server.list_tools()
            # 为每个工具添加服务器名称以进行命名空间管理
            for tool in tools:
                tool_dict = {
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": tool.inputSchema,
                    "_server": server_name,
                    "_namespaced_name": f"{server_name}_{tool.name}",
                }
                all_tools.append(tool_dict)

        self._tools_cache = all_tools
        return all_tools

    async def call_tool(
        self, tool_name: str, arguments: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """通过命名空间名称调用工具。"""
        # 提取服务器名称和工具名称
        parts = tool_name.split("_", 1)
        if len(parts) != 2:
            raise ValueError(f"无效的命名空间工具名称: {tool_name}")

        server_name, actual_tool_name = parts

        if server_name not in self.servers:
            raise ValueError(f"未找到服务器: {server_name}")

        result = await self.servers[server_name].call_tool(actual_tool_name, arguments)

        # 将 CallToolResult 转换为字典格式
        content_list = []
        for content in result.content:
            if isinstance(content, TextContent):
                content_list.append({"type": "text", "text": content.text})
            elif isinstance(content, ImageContent):
                content_list.append(
                    {
                        "type": "image",
                        "data": content.data,
                        "mimeType": content.mimeType,
                    },
                )
            elif isinstance(content, EmbeddedResource):
                content_list.append({"type": "resource", "resource": content.resource})

        return {
            "content": content_list,
            "isError": result.isError if hasattr(result, "isError") else False,
        }

    async def initialize(self) -> None:
        """初始化客户端（在此实现中为空操作）。"""

    async def close(self) -> None:
        """关闭所有服务器连接。"""
        for server in list(self.servers.values()):
            await server.disconnect()
        self.servers.clear()
        self._tools_cache = None


class DefaultMCPClientFactory:
    """默认的 MCP 客户端工厂实现。"""

    def create_client(self, servers: dict[str, MCPServerConfig]) -> MCPClientInterface:
        """创建默认的 MCP 客户端实例。

        Args:
            servers: 服务器配置字典

        Returns:
            DefaultMCPClient 实例
        """
        return DefaultMCPClient()


# 保持向后兼容
MCPClient = DefaultMCPClient
