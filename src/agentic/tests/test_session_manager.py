"""测试会话管理器功能。"""

import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from ..config import MCPServerConfig
from ..session_manager import (
    DefaultSessionManager,
    MCPSession,
    PooledSessionManager,
)


@pytest.mark.unit
class TestMCPSession:
    """测试 MCP 会话类。"""

    def test_session_creation(self):
        """测试会话创建。"""
        config = MCPServerConfig(
            name="test_server", command="test_command", args=["arg1", "arg2"]
        )
        session = MCPSession("session_1", "test_server", config)

        assert session.session_id == "session_1"
        assert session.server_name == "test_server"
        assert session.config == config
        assert session.connection is None
        assert not session.is_connected
        assert session.metadata == {}

    def test_session_metadata(self):
        """测试会话元数据操作。"""
        config = MCPServerConfig(name="test", command="test")
        session = MCPSession("session_1", "test_server", config)

        # 设置和获取元数据
        session.set_metadata("key1", "value1")
        session.set_metadata("key2", {"nested": "data"})

        assert session.get_metadata("key1") == "value1"
        assert session.get_metadata("key2") == {"nested": "data"}
        assert session.get_metadata("nonexistent") is None
        assert session.get_metadata("nonexistent", "default") == "default"

    @pytest.mark.asyncio
    async def test_session_connection_lifecycle(self):
        """测试会话连接生命周期。"""
        config = MCPServerConfig(name="test", command="test")
        session = MCPSession("session_1", "test_server", config)

        # 模拟连接
        with patch(
            "src.agentic.session_manager.MCPServerConnection"
        ) as mock_connection_class:
            mock_connection = AsyncMock()
            mock_connection_class.return_value = mock_connection

            # 测试连接
            await session.connect()
            assert session.is_connected
            assert session.connection == mock_connection
            mock_connection.connect.assert_called_once()

            # 测试断开
            await session.disconnect()
            assert not session.is_connected
            assert session.connection is None
            mock_connection.disconnect.assert_called_once()

    @pytest.mark.asyncio
    async def test_ensure_connected_context_manager(self):
        """测试确保连接的上下文管理器。"""
        config = MCPServerConfig(name="test", command="test")
        session = MCPSession("session_1", "test_server", config)

        with patch.object(session, "connect", new_callable=AsyncMock) as mock_connect:
            async with session.ensure_connected() as connected_session:
                assert connected_session == session
                mock_connect.assert_called_once()


@pytest.mark.unit
@pytest.mark.asyncio
class TestDefaultSessionManager:
    """测试默认会话管理器。"""

    async def test_create_session(self):
        """测试创建会话。"""
        manager = DefaultSessionManager()
        config = MCPServerConfig(name="test", command="test")

        with patch("src.agentic.session_manager.MCPSession") as mock_session_class:
            mock_session = AsyncMock()
            mock_session_class.return_value = mock_session

            session_id = await manager.create_session("test_server", config)

            assert session_id in manager.sessions
            assert session_id.startswith("session_")
            mock_session.connect.assert_called_once()

    async def test_get_session(self):
        """测试获取会话。"""
        manager = DefaultSessionManager()
        config = MCPServerConfig(name="test", command="test")

        # 获取不存在的会话
        session = await manager.get_session("nonexistent")
        assert session is None

        # 创建并获取会话
        with patch("src.agentic.session_manager.MCPSession") as mock_session_class:
            mock_session = AsyncMock()
            mock_session_class.return_value = mock_session

            session_id = await manager.create_session("test_server", config)
            retrieved_session = await manager.get_session(session_id)

            assert retrieved_session == mock_session

    async def test_close_session(self):
        """测试关闭会话。"""
        manager = DefaultSessionManager()
        config = MCPServerConfig(name="test", command="test")

        with patch("src.agentic.session_manager.MCPSession") as mock_session_class:
            mock_session = AsyncMock()
            mock_session_class.return_value = mock_session

            session_id = await manager.create_session("test_server", config)
            assert session_id in manager.sessions

            await manager.close_session(session_id)
            assert session_id not in manager.sessions
            mock_session.disconnect.assert_called_once()

    async def test_close_all_sessions(self):
        """测试关闭所有会话。"""
        manager = DefaultSessionManager()
        config = MCPServerConfig(name="test", command="test")

        with patch("src.agentic.session_manager.MCPSession") as mock_session_class:
            mock_sessions = [AsyncMock() for _ in range(3)]
            mock_session_class.side_effect = mock_sessions

            # 创建多个会话
            session_ids = []
            for i in range(3):
                session_id = await manager.create_session(f"server_{i}", config)
                session_ids.append(session_id)

            assert len(manager.sessions) == 3

            # 关闭所有会话
            await manager.close_all_sessions()
            assert len(manager.sessions) == 0

            # 验证所有会话都被断开
            for mock_session in mock_sessions:
                mock_session.disconnect.assert_called_once()

    async def test_list_sessions(self):
        """测试列出会话。"""
        manager = DefaultSessionManager()
        config = MCPServerConfig(name="test", command="test")

        # 空列表
        sessions = manager.list_sessions()
        assert sessions == set()

        with patch("src.agentic.session_manager.MCPSession") as mock_session_class:
            mock_session_class.return_value = AsyncMock()

            # 创建多个会话
            session_ids = []
            for i in range(3):
                session_id = await manager.create_session(f"server_{i}", config)
                session_ids.append(session_id)

            sessions = manager.list_sessions()
            assert sessions == set(session_ids)

    async def test_get_connected_sessions(self):
        """测试获取已连接的会话。"""
        manager = DefaultSessionManager()
        config = MCPServerConfig(name="test", command="test")

        with patch("src.agentic.session_manager.MCPSession") as mock_session_class:
            # 创建模拟会话，部分连接，部分未连接
            mock_sessions = []
            for i in range(3):
                mock_session = AsyncMock()
                mock_session.is_connected = i < 2  # 前两个连接，最后一个未连接
                mock_sessions.append(mock_session)

            mock_session_class.side_effect = mock_sessions

            # 创建会话
            session_ids = []
            for i in range(3):
                session_id = await manager.create_session(f"server_{i}", config)
                session_ids.append(session_id)

            # 获取已连接的会话
            connected_sessions = await manager.get_connected_sessions()
            assert len(connected_sessions) == 2


@pytest.mark.unit
@pytest.mark.asyncio
class TestPooledSessionManager:
    """测试连接池会话管理器。"""

    async def test_session_limit(self):
        """测试会话数量限制。"""
        manager = PooledSessionManager(max_sessions_per_server=2)
        config = MCPServerConfig(name="test", command="test")

        with patch("src.agentic.session_manager.MCPSession") as mock_session_class:
            mock_session_class.return_value = AsyncMock()

            # 创建最大数量的会话
            session_id1 = await manager.create_session("server_1", config)
            session_id2 = await manager.create_session("server_1", config)

            assert len(manager.sessions) == 2
            assert manager.server_session_count["server_1"] == 2

            # 尝试创建超过限制的会话，应该抛出异常
            with pytest.raises(RuntimeError, match="会话数已达到最大限制"):
                await manager.create_session("server_1", config)

    async def test_session_count_management(self):
        """测试会话计数管理。"""
        manager = PooledSessionManager(max_sessions_per_server=3)
        config = MCPServerConfig(name="test", command="test")

        with patch("src.agentic.session_manager.MCPSession") as mock_session_class:
            mock_session_class.return_value = AsyncMock()

            # 为不同服务器创建会话
            session_id1 = await manager.create_session("server_1", config)
            session_id2 = await manager.create_session("server_2", config)
            session_id3 = await manager.create_session("server_1", config)

            assert manager.server_session_count["server_1"] == 2
            assert manager.server_session_count["server_2"] == 1

            # 关闭会话并检查计数
            await manager.close_session(session_id1)
            assert manager.server_session_count["server_1"] == 1

            await manager.close_session(session_id2)
            assert manager.server_session_count["server_2"] == 0


@pytest.mark.integration
@pytest.mark.asyncio
class TestSessionManagerIntegration:
    """会话管理器集成测试。"""

    async def test_concurrent_session_operations(self):
        """测试并发会话操作。"""
        manager = DefaultSessionManager()
        config = MCPServerConfig(name="test", command="test")

        with patch("src.agentic.session_manager.MCPSession") as mock_session_class:
            mock_session_class.return_value = AsyncMock()

            # 并发创建多个会话
            tasks = []
            for i in range(5):
                task = asyncio.create_task(
                    manager.create_session(f"server_{i}", config)
                )
                tasks.append(task)

            session_ids = await asyncio.gather(*tasks)

            assert len(session_ids) == 5
            assert len(set(session_ids)) == 5  # 确保所有 ID 都是唯一的
            assert len(manager.sessions) == 5
