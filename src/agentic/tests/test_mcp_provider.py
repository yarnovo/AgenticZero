"""测试 MCP 提供商功能。"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ..config import MCPServerConfig
from ..mcp_provider import DefaultMCPProvider, MCPProviderFactory, MCPToolInfo


@pytest.mark.unit
class TestMCPToolInfo:
    """测试 MCP 工具信息类。"""

    def test_tool_info_creation(self):
        """测试工具信息创建。"""
        tool = MCPToolInfo(
            name="test_tool",
            description="A test tool",
            parameters={"type": "object", "properties": {}},
            server_name="test_server",
            namespaced_name="test_server_test_tool",
            metadata={"version": "1.0"},
        )

        assert tool.name == "test_tool"
        assert tool.description == "A test tool"
        assert tool.server_name == "test_server"
        assert tool.namespaced_name == "test_server_test_tool"
        assert tool.metadata == {"version": "1.0"}

    def test_tool_info_to_dict(self):
        """测试工具信息转换为字典。"""
        tool = MCPToolInfo(
            name="test_tool",
            description="A test tool",
            parameters={"type": "object"},
            server_name="test_server",
            namespaced_name="test_server_test_tool",
        )

        result = tool.to_dict()
        expected = {
            "name": "test_tool",
            "description": "A test tool",
            "inputSchema": {"type": "object"},
            "_server": "test_server",
            "_namespaced_name": "test_server_test_tool",
            "_metadata": {},
        }
        assert result == expected


@pytest.mark.unit
@pytest.mark.asyncio
class TestDefaultMCPProvider:
    """测试默认 MCP 提供商。"""

    async def test_initialization(self):
        """测试提供商初始化。"""
        provider = DefaultMCPProvider()
        assert not provider._initialized

        await provider.initialize()
        assert provider._initialized

    async def test_shutdown(self):
        """测试提供商关闭。"""
        provider = DefaultMCPProvider()
        await provider.initialize()

        with patch.object(
            provider.session_manager, "close_all_sessions", new_callable=AsyncMock
        ) as mock_close:
            await provider.shutdown()
            mock_close.assert_called_once()
            assert not provider._initialized

    async def test_add_server(self):
        """测试添加服务器。"""
        provider = DefaultMCPProvider()
        config = MCPServerConfig(name="test", command="test")

        with patch.object(
            provider.session_manager, "create_session", new_callable=AsyncMock
        ) as mock_create:
            mock_create.return_value = "session_1"

            await provider.add_server("test_server", config)

            assert "test_server" in provider.server_configs
            assert provider.server_configs["test_server"] == config
            assert provider.server_sessions["test_server"] == "session_1"
            mock_create.assert_called_once_with("test_server", config)

    async def test_remove_server(self):
        """测试移除服务器。"""
        provider = DefaultMCPProvider()
        config = MCPServerConfig(name="test", command="test")

        with (
            patch.object(
                provider.session_manager, "create_session", new_callable=AsyncMock
            ) as mock_create,
            patch.object(
                provider.session_manager, "close_session", new_callable=AsyncMock
            ) as mock_close,
        ):
            mock_create.return_value = "session_1"

            # 添加服务器
            await provider.add_server("test_server", config)
            assert "test_server" in provider.server_configs

            # 移除服务器
            await provider.remove_server("test_server")

            assert "test_server" not in provider.server_configs
            assert "test_server" not in provider.server_sessions
            mock_close.assert_called_once_with("session_1")

    async def test_list_servers(self):
        """测试列出服务器。"""
        provider = DefaultMCPProvider()
        config = MCPServerConfig(name="test", command="test")

        # 空列表
        servers = await provider.list_servers()
        assert servers == set()

        with patch.object(
            provider.session_manager, "create_session", new_callable=AsyncMock
        ):
            # 添加服务器
            await provider.add_server("server_1", config)
            await provider.add_server("server_2", config)

            servers = await provider.list_servers()
            assert servers == {"server_1", "server_2"}

    async def test_get_server_info(self):
        """测试获取服务器信息。"""
        provider = DefaultMCPProvider()
        config = MCPServerConfig(name="test", command="test")

        # 不存在的服务器
        info = await provider.get_server_info("nonexistent")
        assert info is None

        with (
            patch.object(
                provider.session_manager, "create_session", new_callable=AsyncMock
            ) as mock_create,
            patch.object(
                provider.session_manager, "get_session", new_callable=AsyncMock
            ) as mock_get,
        ):
            mock_create.return_value = "session_1"
            mock_session = MagicMock()
            mock_session.is_connected = True
            mock_get.return_value = mock_session

            await provider.add_server("test_server", config)

            with patch.object(
                provider, "list_tools", new_callable=AsyncMock
            ) as mock_list_tools:
                mock_list_tools.return_value = []

                info = await provider.get_server_info("test_server")

                assert info is not None
                assert info["name"] == "test_server"
                assert info["session_id"] == "session_1"
                assert info["is_connected"] is True
                assert info["tools_count"] == 0

    async def test_list_tools_for_server(self):
        """测试列出指定服务器的工具。"""
        provider = DefaultMCPProvider()
        config = MCPServerConfig(name="test", command="test")

        # 不存在的服务器
        tools = await provider.list_tools("nonexistent")
        assert tools == []

        with (
            patch.object(
                provider.session_manager, "create_session", new_callable=AsyncMock
            ) as mock_create,
            patch.object(
                provider.session_manager, "get_session", new_callable=AsyncMock
            ) as mock_get,
        ):
            mock_create.return_value = "session_1"
            mock_session = MagicMock()
            mock_session.is_connected = True

            # 模拟连接对象
            mock_connection = AsyncMock()
            mock_tool = MagicMock()
            mock_tool.name = "test_tool"
            mock_tool.description = "A test tool"
            mock_tool.inputSchema = {"type": "object"}
            mock_connection.list_tools.return_value = [mock_tool]
            mock_session.connection = mock_connection

            mock_get.return_value = mock_session

            await provider.add_server("test_server", config)

            tools = await provider.list_tools("test_server")

            assert len(tools) == 1
            assert tools[0].name == "test_tool"
            assert tools[0].server_name == "test_server"
            assert tools[0].namespaced_name == "test_server_test_tool"

    async def test_list_all_tools(self):
        """测试列出所有工具。"""
        provider = DefaultMCPProvider()
        config = MCPServerConfig(name="test", command="test")

        with patch.object(
            provider, "_get_server_tools", new_callable=AsyncMock
        ) as mock_get_tools:
            # 模拟两个服务器的工具
            tool1 = MCPToolInfo("tool1", "desc1", {}, "server1", "server1_tool1")
            tool2 = MCPToolInfo("tool2", "desc2", {}, "server2", "server2_tool2")

            mock_get_tools.side_effect = lambda server: {
                "server1": [tool1],
                "server2": [tool2],
            }.get(server, [])

            # 添加服务器配置
            provider.server_configs["server1"] = config
            provider.server_configs["server2"] = config

            tools = await provider.list_tools()

            assert len(tools) == 2
            assert tools[0] == tool1
            assert tools[1] == tool2

    async def test_call_tool_with_server_name(self):
        """测试通过服务器名称调用工具。"""
        provider = DefaultMCPProvider()
        config = MCPServerConfig(name="test", command="test")

        with (
            patch.object(
                provider.session_manager, "create_session", new_callable=AsyncMock
            ) as mock_create,
            patch.object(
                provider.session_manager, "get_session", new_callable=AsyncMock
            ) as mock_get,
        ):
            mock_create.return_value = "session_1"
            mock_session = MagicMock()

            # 模拟工具调用结果
            mock_result = MagicMock()
            mock_content = MagicMock()
            mock_content.text = "Tool result"
            mock_result.content = [mock_content]

            mock_connection = AsyncMock()
            mock_connection.call_tool.return_value = mock_result
            mock_session.connection = mock_connection

            mock_get.return_value = mock_session

            await provider.add_server("test_server", config)

            result = await provider.call_tool(
                tool_name="test_tool",
                arguments={"param": "value"},
                server_name="test_server",
            )

            mock_connection.call_tool.assert_called_once_with(
                "test_tool", {"param": "value"}
            )
            assert "content" in result
            assert result["content"][0]["type"] == "text"
            assert result["content"][0]["text"] == "Tool result"

    async def test_call_tool_with_namespaced_name(self):
        """测试通过命名空间名称调用工具。"""
        provider = DefaultMCPProvider()
        config = MCPServerConfig(name="test", command="test")

        with (
            patch.object(
                provider.session_manager, "create_session", new_callable=AsyncMock
            ) as mock_create,
            patch.object(
                provider.session_manager, "get_session", new_callable=AsyncMock
            ) as mock_get,
        ):
            mock_create.return_value = "session_1"
            mock_session = MagicMock()

            mock_result = MagicMock()
            mock_content = MagicMock()
            mock_content.text = "Tool result"
            mock_result.content = [mock_content]

            mock_connection = AsyncMock()
            mock_connection.call_tool.return_value = mock_result
            mock_session.connection = mock_connection

            mock_get.return_value = mock_session

            await provider.add_server("test_server", config)

            result = await provider.call_tool("test_server_test_tool")

            mock_connection.call_tool.assert_called_once_with("test_tool", {})

    async def test_call_tool_invalid_name(self):
        """测试调用无效工具名称。"""
        provider = DefaultMCPProvider()

        with pytest.raises(ValueError, match="无效的工具名称格式"):
            await provider.call_tool("invalid_tool_name_without_underscore")

    async def test_call_tool_nonexistent_server(self):
        """测试调用不存在服务器的工具。"""
        provider = DefaultMCPProvider()

        with pytest.raises(ValueError, match="未找到服务器"):
            await provider.call_tool("nonexistent_server_tool")

    async def test_health_check(self):
        """测试健康检查。"""
        provider = DefaultMCPProvider()
        config = MCPServerConfig(name="test", command="test")

        with (
            patch.object(
                provider.session_manager, "create_session", new_callable=AsyncMock
            ) as mock_create,
            patch.object(
                provider.session_manager, "get_session", new_callable=AsyncMock
            ) as mock_get,
        ):
            mock_create.return_value = "session_1"
            mock_session = MagicMock()
            mock_session.is_connected = True
            mock_get.return_value = mock_session

            await provider.initialize()
            await provider.add_server("test_server", config)

            health = await provider.health_check()

            assert health["healthy"] is True
            assert health["total_servers"] == 1
            assert health["connected_servers"] == 1
            assert health["initialized"] is True
            assert "test_server" in health["server_status"]
            assert health["server_status"]["test_server"]["connected"] is True


@pytest.mark.unit
def test_mcp_provider_factory():
    """测试 MCP 提供商工厂。"""
    # 测试创建默认提供商
    provider = MCPProviderFactory.create_default_provider()
    assert isinstance(provider, DefaultMCPProvider)

    # 测试从配置创建提供商
    config = {"type": "default", "auto_reconnect": False}
    provider = MCPProviderFactory.create_provider_from_config(config)
    assert isinstance(provider, DefaultMCPProvider)
    assert provider.auto_reconnect is False

    # 测试不支持的提供商类型
    with pytest.raises(ValueError, match="不支持的提供商类型"):
        MCPProviderFactory.create_provider_from_config({"type": "unsupported"})
