"""MCP 会话管理器，负责管理 MCP 服务器连接和会话生命周期。"""

import logging
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from typing import Any, Optional

from .config import MCPServerConfig
from .mcp_client import MCPServerConnection

logger = logging.getLogger(__name__)


class SessionManagerInterface(ABC):
    """MCP 会话管理器抽象接口。"""

    @abstractmethod
    async def create_session(self, server_name: str, config: MCPServerConfig) -> str:
        """创建新的会话。

        Args:
            server_name: 服务器名称
            config: 服务器配置

        Returns:
            会话ID
        """

    @abstractmethod
    async def get_session(self, session_id: str) -> Optional["MCPSession"]:
        """获取指定会话。

        Args:
            session_id: 会话ID

        Returns:
            会话对象，如果不存在则返回None
        """

    @abstractmethod
    async def close_session(self, session_id: str) -> None:
        """关闭指定会话。

        Args:
            session_id: 会话ID
        """

    @abstractmethod
    async def close_all_sessions(self) -> None:
        """关闭所有会话。"""

    @abstractmethod
    def list_sessions(self) -> set[str]:
        """列出所有会话ID。

        Returns:
            会话ID集合
        """


class MCPSession:
    """MCP 会话，封装服务器连接和相关状态。"""

    def __init__(self, session_id: str, server_name: str, config: MCPServerConfig):
        self.session_id = session_id
        self.server_name = server_name
        self.config = config
        self.connection: MCPServerConnection | None = None
        self.is_connected = False
        self.metadata: dict[str, Any] = {}

    async def connect(self) -> None:
        """连接到 MCP 服务器。"""
        if self.is_connected:
            logger.warning(f"会话 {self.session_id} 已经连接")
            return

        self.connection = MCPServerConnection(self.server_name, self.config)
        await self.connection.connect()
        self.is_connected = True
        logger.info(f"会话 {self.session_id} 已连接到服务器 {self.server_name}")

    async def disconnect(self) -> None:
        """断开服务器连接。"""
        if not self.is_connected or not self.connection:
            return

        await self.connection.disconnect()
        self.connection = None
        self.is_connected = False
        logger.info(f"会话 {self.session_id} 已断开与服务器 {self.server_name} 的连接")

    @asynccontextmanager
    async def ensure_connected(self):
        """确保连接的上下文管理器。"""
        if not self.is_connected:
            await self.connect()
        try:
            yield self
        finally:
            pass

    def set_metadata(self, key: str, value: Any) -> None:
        """设置会话元数据。"""
        self.metadata[key] = value

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """获取会话元数据。"""
        return self.metadata.get(key, default)


class DefaultSessionManager(SessionManagerInterface):
    """默认的 MCP 会话管理器实现。"""

    def __init__(self):
        self.sessions: dict[str, MCPSession] = {}
        self._session_counter = 0

    def _generate_session_id(self) -> str:
        """生成唯一的会话ID。"""
        self._session_counter += 1
        return f"session_{self._session_counter}"

    async def create_session(self, server_name: str, config: MCPServerConfig) -> str:
        """创建新的会话。"""
        session_id = self._generate_session_id()
        session = MCPSession(session_id, server_name, config)

        # 立即连接到服务器
        await session.connect()

        self.sessions[session_id] = session
        logger.info(f"创建会话 {session_id} 用于服务器 {server_name}")
        return session_id

    async def get_session(self, session_id: str) -> MCPSession | None:
        """获取指定会话。"""
        return self.sessions.get(session_id)

    async def close_session(self, session_id: str) -> None:
        """关闭指定会话。"""
        session = self.sessions.get(session_id)
        if session:
            await session.disconnect()
            del self.sessions[session_id]
            logger.info(f"关闭会话 {session_id}")

    async def close_all_sessions(self) -> None:
        """关闭所有会话。"""
        for session_id in list(self.sessions.keys()):
            await self.close_session(session_id)
        logger.info("所有会话已关闭")

    def list_sessions(self) -> set[str]:
        """列出所有会话ID。"""
        return set(self.sessions.keys())

    async def get_connected_sessions(self) -> dict[str, MCPSession]:
        """获取所有已连接的会话。"""
        return {
            sid: session
            for sid, session in self.sessions.items()
            if session.is_connected
        }


class PooledSessionManager(DefaultSessionManager):
    """支持连接池的会话管理器。"""

    def __init__(self, max_sessions_per_server: int = 5):
        super().__init__()
        self.max_sessions_per_server = max_sessions_per_server
        self.server_session_count: dict[str, int] = {}

    async def create_session(self, server_name: str, config: MCPServerConfig) -> str:
        """创建新的会话，考虑连接池限制。"""
        current_count = self.server_session_count.get(server_name, 0)

        if current_count >= self.max_sessions_per_server:
            raise RuntimeError(
                f"服务器 {server_name} 的会话数已达到最大限制 {self.max_sessions_per_server}"
            )

        session_id = await super().create_session(server_name, config)
        self.server_session_count[server_name] = current_count + 1
        return session_id

    async def close_session(self, session_id: str) -> None:
        """关闭指定会话并更新计数。"""
        session = self.sessions.get(session_id)
        if session:
            server_name = session.server_name
            await super().close_session(session_id)

            # 更新计数
            current_count = self.server_session_count.get(server_name, 0)
            if current_count > 0:
                self.server_session_count[server_name] = current_count - 1
