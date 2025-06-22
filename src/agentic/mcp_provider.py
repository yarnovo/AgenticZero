"""MCP 提供商抽象类，用于管理不同类型的 MCP 服务器和客户端。"""

import logging
from abc import ABC, abstractmethod
from typing import Any

from .config import MCPServerConfig
from .session_manager import DefaultSessionManager, SessionManagerInterface

logger = logging.getLogger(__name__)


class MCPToolInfo:
    """MCP 工具信息封装。"""

    def __init__(
        self,
        name: str,
        description: str,
        parameters: dict[str, Any],
        server_name: str,
        namespaced_name: str,
        metadata: dict[str, Any] | None = None,
    ):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.server_name = server_name
        self.namespaced_name = namespaced_name
        self.metadata = metadata or {}

    def to_dict(self) -> dict[str, Any]:
        """转换为字典格式。"""
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.parameters,
            "_server": self.server_name,
            "_namespaced_name": self.namespaced_name,
            "_metadata": self.metadata,
        }


class MCPProviderInterface(ABC):
    """MCP 提供商抽象接口。"""

    @abstractmethod
    async def initialize(self) -> None:
        """初始化提供商。"""

    @abstractmethod
    async def shutdown(self) -> None:
        """关闭提供商，清理所有资源。"""

    @abstractmethod
    async def add_server(self, name: str, config: MCPServerConfig) -> None:
        """添加 MCP 服务器。

        Args:
            name: 服务器名称
            config: 服务器配置
        """

    @abstractmethod
    async def remove_server(self, name: str) -> None:
        """移除 MCP 服务器。

        Args:
            name: 服务器名称
        """

    @abstractmethod
    async def list_servers(self) -> set[str]:
        """列出所有服务器名称。

        Returns:
            服务器名称集合
        """

    @abstractmethod
    async def get_server_info(self, name: str) -> dict[str, Any] | None:
        """获取服务器信息。

        Args:
            name: 服务器名称

        Returns:
            服务器信息字典
        """

    @abstractmethod
    async def list_tools(self, server_name: str | None = None) -> list[MCPToolInfo]:
        """列出工具。

        Args:
            server_name: 服务器名称，如果为None则列出所有工具

        Returns:
            工具信息列表
        """

    @abstractmethod
    async def call_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any] | None = None,
        server_name: str | None = None,
    ) -> dict[str, Any]:
        """调用工具。

        Args:
            tool_name: 工具名称（可以是命名空间名称或原始名称）
            arguments: 工具参数
            server_name: 服务器名称，如果提供则直接在该服务器上调用

        Returns:
            工具执行结果
        """

    @abstractmethod
    async def health_check(self) -> dict[str, Any]:
        """健康检查。

        Returns:
            健康状态信息
        """


class DefaultMCPProvider(MCPProviderInterface):
    """默认的 MCP 提供商实现。"""

    def __init__(
        self,
        session_manager: SessionManagerInterface | None = None,
        auto_reconnect: bool = True,
    ):
        self.session_manager = session_manager or DefaultSessionManager()
        self.auto_reconnect = auto_reconnect
        self.server_configs: dict[str, MCPServerConfig] = {}
        self.server_sessions: dict[str, str] = {}  # server_name -> session_id
        self._tools_cache: dict[str, list[MCPToolInfo]] = {}
        self._initialized = False

    async def initialize(self) -> None:
        """初始化提供商。"""
        if self._initialized:
            return

        logger.info("正在初始化 MCP 提供商")
        self._initialized = True
        logger.info("MCP 提供商初始化完成")

    async def shutdown(self) -> None:
        """关闭提供商，清理所有资源。"""
        logger.info("正在关闭 MCP 提供商")

        # 关闭所有会话
        await self.session_manager.close_all_sessions()

        # 清理缓存
        self._tools_cache.clear()
        self.server_sessions.clear()

        self._initialized = False
        logger.info("MCP 提供商已关闭")

    async def add_server(self, name: str, config: MCPServerConfig) -> None:
        """添加 MCP 服务器。"""
        if name in self.server_configs:
            logger.warning(f"服务器 {name} 已存在，正在替换")
            await self.remove_server(name)

        self.server_configs[name] = config

        # 创建会话
        session_id = await self.session_manager.create_session(name, config)
        self.server_sessions[name] = session_id

        # 清除相关缓存
        self._tools_cache.pop(name, None)

        logger.info(f"添加 MCP 服务器 {name}")

    async def remove_server(self, name: str) -> None:
        """移除 MCP 服务器。"""
        if name not in self.server_configs:
            logger.warning(f"服务器 {name} 不存在")
            return

        # 关闭会话
        session_id = self.server_sessions.get(name)
        if session_id:
            await self.session_manager.close_session(session_id)
            del self.server_sessions[name]

        # 清理配置和缓存
        del self.server_configs[name]
        self._tools_cache.pop(name, None)

        logger.info(f"移除 MCP 服务器 {name}")

    async def list_servers(self) -> set[str]:
        """列出所有服务器名称。"""
        return set(self.server_configs.keys())

    async def get_server_info(self, name: str) -> dict[str, Any] | None:
        """获取服务器信息。"""
        if name not in self.server_configs:
            return None

        config = self.server_configs[name]
        session_id = self.server_sessions.get(name)
        session = (
            await self.session_manager.get_session(session_id) if session_id else None
        )

        return {
            "name": name,
            "config": config.dict(),
            "session_id": session_id,
            "is_connected": session.is_connected if session else False,
            "tools_count": len(await self.list_tools(name)),
        }

    async def list_tools(self, server_name: str | None = None) -> list[MCPToolInfo]:
        """列出工具。"""
        if server_name:
            # 列出指定服务器的工具
            return await self._get_server_tools(server_name)
        else:
            # 列出所有服务器的工具
            all_tools = []
            for name in self.server_configs.keys():
                tools = await self._get_server_tools(name)
                all_tools.extend(tools)
            return all_tools

    async def _get_server_tools(self, server_name: str) -> list[MCPToolInfo]:
        """获取指定服务器的工具。"""
        if server_name not in self.server_configs:
            return []

        # 检查缓存
        if server_name in self._tools_cache:
            return self._tools_cache[server_name]

        # 获取会话
        session_id = self.server_sessions.get(server_name)
        if not session_id:
            logger.error(f"服务器 {server_name} 没有活动会话")
            return []

        session = await self.session_manager.get_session(session_id)
        if not session or not session.connection:
            logger.error(f"服务器 {server_name} 会话无效")
            return []

        try:
            # 获取工具列表
            raw_tools = await session.connection.list_tools()
            tools = []

            for tool in raw_tools:
                tool_info = MCPToolInfo(
                    name=tool.name,
                    description=tool.description,
                    parameters=tool.inputSchema,
                    server_name=server_name,
                    namespaced_name=f"{server_name}_{tool.name}",
                )
                tools.append(tool_info)

            # 缓存结果
            self._tools_cache[server_name] = tools
            return tools

        except Exception as e:
            logger.error(f"获取服务器 {server_name} 工具列表时出错: {e}")
            return []

    async def call_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any] | None = None,
        server_name: str | None = None,
    ) -> dict[str, Any]:
        """调用工具。"""
        arguments = arguments or {}

        # 解析工具名称
        if server_name:
            # 直接在指定服务器上调用
            actual_tool_name = tool_name
            target_server = server_name
        else:
            # 从命名空间名称中解析
            parts = tool_name.split("_", 1)
            if len(parts) != 2:
                raise ValueError(f"无效的工具名称格式: {tool_name}")
            target_server, actual_tool_name = parts

        # 检查服务器是否存在
        if target_server not in self.server_configs:
            raise ValueError(f"服务器 {target_server} 不存在")

        # 获取会话
        session_id = self.server_sessions.get(target_server)
        if not session_id:
            raise RuntimeError(f"服务器 {target_server} 没有活动会话")

        session = await self.session_manager.get_session(session_id)
        if not session or not session.connection:
            raise RuntimeError(f"服务器 {target_server} 会话无效")

        try:
            # 调用工具
            result = await session.connection.call_tool(actual_tool_name, arguments)

            # 转换结果格式
            if hasattr(result, "content"):
                # 处理 MCP 结果格式
                content_list = []
                for content in result.content:
                    if hasattr(content, "text"):
                        content_list.append({"type": "text", "text": content.text})
                    elif hasattr(content, "data") and hasattr(content, "mimeType"):
                        content_list.append(
                            {
                                "type": "image",
                                "data": content.data,
                                "mimeType": content.mimeType,
                            }
                        )
                    else:
                        content_list.append(
                            {"type": "unknown", "content": str(content)}
                        )

                return {
                    "content": content_list,
                    "isError": getattr(result, "isError", False),
                }

            return {"content": [{"type": "text", "text": str(result)}]}

        except Exception as e:
            logger.error(f"调用工具 {tool_name} 时出错: {e}")
            return {
                "content": [{"type": "text", "text": f"工具调用错误: {e}"}],
                "isError": True,
            }

    async def health_check(self) -> dict[str, Any]:
        """健康检查。"""
        total_servers = len(self.server_configs)
        connected_servers = 0
        server_status = {}

        for server_name in self.server_configs:
            session_id = self.server_sessions.get(server_name)
            if session_id:
                session = await self.session_manager.get_session(session_id)
                is_connected = session.is_connected if session else False
                if is_connected:
                    connected_servers += 1
                server_status[server_name] = {
                    "connected": is_connected,
                    "session_id": session_id,
                }
            else:
                server_status[server_name] = {"connected": False, "session_id": None}

        return {
            "healthy": connected_servers == total_servers,
            "total_servers": total_servers,
            "connected_servers": connected_servers,
            "server_status": server_status,
            "initialized": self._initialized,
        }


class MCPProviderFactory:
    """MCP 提供商工厂。"""

    @staticmethod
    def create_default_provider(
        session_manager: SessionManagerInterface | None = None,
        auto_reconnect: bool = True,
    ) -> DefaultMCPProvider:
        """创建默认的 MCP 提供商。"""
        return DefaultMCPProvider(session_manager, auto_reconnect)

    @staticmethod
    def create_provider_from_config(
        provider_config: dict[str, Any],
        session_manager: SessionManagerInterface | None = None,
    ) -> MCPProviderInterface:
        """从配置创建 MCP 提供商。"""
        provider_type = provider_config.get("type", "default")

        if provider_type == "default":
            return DefaultMCPProvider(
                session_manager=session_manager,
                auto_reconnect=provider_config.get("auto_reconnect", True),
            )
        else:
            raise ValueError(f"不支持的提供商类型: {provider_type}")
