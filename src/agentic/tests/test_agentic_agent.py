"""测试 AgenticAgent 功能。"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ..agent import AgenticAgent
from ..config import AgentConfig, LLMConfig, MCPServerConfig
from ..llm import LLMResponse, ToolCall


@pytest.mark.unit
@pytest.mark.asyncio
class TestAgenticAgent:
    """测试 AgenticAgent 类。"""

    def create_test_config(self):
        """创建测试配置。"""
        return AgentConfig(
            name="test_agent",
            instruction="You are a test agent",
            llm_config=LLMConfig(provider="openai", api_key="test_key", model="gpt-4"),
            mcp_servers={
                "test_server": MCPServerConfig(
                    name="test_server", command="test_command"
                )
            },
        )

    async def test_agent_initialization(self):
        """测试智能体初始化。"""
        config = self.create_test_config()

        with (
            patch("src.agentic.agent.create_llm_provider") as mock_create_llm,
            patch("src.agentic.agent.MCPProviderFactory") as mock_provider_factory,
            patch("src.agentic.agent.ContextManager") as mock_context_manager,
        ):
            mock_llm = AsyncMock()
            mock_create_llm.return_value = mock_llm

            mock_mcp_provider = AsyncMock()
            mock_provider_factory.create_default_provider.return_value = (
                mock_mcp_provider
            )

            mock_context_mgr = AsyncMock()
            mock_context_manager.create_memory_manager.return_value = mock_context_mgr

            agent = AgenticAgent(config)

            assert agent.name == "test_agent"
            assert agent.instruction == "You are a test agent"
            assert agent.config == config
            assert agent.conversation_id == "agent_test_agent"
            assert agent.llm_provider == mock_llm

    async def test_agent_initialization_with_custom_components(self):
        """测试使用自定义组件初始化智能体。"""
        config = self.create_test_config()

        mock_mcp_provider = AsyncMock()
        mock_context_manager = AsyncMock()
        mock_session_manager = AsyncMock()
        mock_llm_provider = AsyncMock()

        agent = AgenticAgent(
            config=config,
            mcp_provider=mock_mcp_provider,
            context_manager=mock_context_manager,
            session_manager=mock_session_manager,
            llm_provider=mock_llm_provider,
            conversation_id="custom_conversation",
        )

        assert agent.mcp_provider == mock_mcp_provider
        assert agent.context_manager == mock_context_manager
        assert agent.session_manager == mock_session_manager
        assert agent.llm_provider == mock_llm_provider
        assert agent.conversation_id == "custom_conversation"

    async def test_agent_full_initialization(self):
        """测试智能体完整初始化过程。"""
        config = self.create_test_config()

        with (
            patch("src.agentic.agent.create_llm_provider") as mock_create_llm,
            patch("src.agentic.agent.MCPProviderFactory") as mock_provider_factory,
            patch("src.agentic.agent.ContextManager") as mock_context_manager,
        ):
            mock_llm = AsyncMock()
            mock_create_llm.return_value = mock_llm

            mock_mcp_provider = AsyncMock()
            mock_provider_factory.create_default_provider.return_value = (
                mock_mcp_provider
            )

            mock_context_mgr = AsyncMock()
            mock_context = AsyncMock()
            mock_context_mgr.get_context.return_value = None
            mock_context_mgr.create_context.return_value = mock_context
            mock_context_manager.create_memory_manager.return_value = mock_context_mgr

            agent = AgenticAgent(config)
            await agent.initialize()

            # 验证 MCP 提供商初始化
            mock_mcp_provider.initialize.assert_called_once()
            mock_mcp_provider.add_server.assert_called_once_with(
                "test_server", config.mcp_servers["test_server"]
            )

            # 验证上下文创建
            mock_context_mgr.get_context.assert_called_once_with("agent_test_agent")
            mock_context_mgr.create_context.assert_called_once_with(
                "agent_test_agent", "You are a test agent"
            )
            assert agent.context == mock_context

    async def test_agent_close(self):
        """测试智能体关闭。"""
        config = self.create_test_config()

        with (
            patch("src.agentic.agent.create_llm_provider"),
            patch("src.agentic.agent.MCPProviderFactory") as mock_provider_factory,
            patch("src.agentic.agent.ContextManager") as mock_context_manager,
        ):
            mock_mcp_provider = AsyncMock()
            mock_provider_factory.create_default_provider.return_value = (
                mock_mcp_provider
            )

            mock_context_mgr = AsyncMock()
            mock_context = AsyncMock()
            mock_context_manager.create_memory_manager.return_value = mock_context_mgr

            agent = AgenticAgent(config)
            agent.context = mock_context

            await agent.close()

            mock_context_mgr.update_context.assert_called_once_with(mock_context)
            mock_mcp_provider.shutdown.assert_called_once()

    async def test_agent_context_manager(self):
        """测试智能体上下文管理器。"""
        config = self.create_test_config()

        with (
            patch("src.agentic.agent.create_llm_provider"),
            patch("src.agentic.agent.MCPProviderFactory") as mock_provider_factory,
            patch("src.agentic.agent.ContextManager") as mock_context_manager,
        ):
            mock_mcp_provider = AsyncMock()
            mock_provider_factory.create_default_provider.return_value = (
                mock_mcp_provider
            )

            mock_context_mgr = AsyncMock()
            mock_context = AsyncMock()
            mock_context_mgr.get_context.return_value = None
            mock_context_mgr.create_context.return_value = mock_context
            mock_context_manager.create_memory_manager.return_value = mock_context_mgr

            agent = AgenticAgent(config)

            async with agent.connect() as connected_agent:
                assert connected_agent == agent
                mock_mcp_provider.initialize.assert_called_once()

            mock_mcp_provider.shutdown.assert_called_once()

    async def test_run_without_initialization(self):
        """测试未初始化运行智能体。"""
        config = self.create_test_config()
        agent = AgenticAgent(config)

        with pytest.raises(RuntimeError, match="智能体未初始化"):
            await agent.run("test input")

    async def test_run_simple_response(self):
        """测试简单响应（无工具调用）。"""
        config = self.create_test_config()

        with (
            patch("src.agentic.agent.create_llm_provider"),
            patch("src.agentic.agent.MCPProviderFactory") as mock_provider_factory,
            patch("src.agentic.agent.ContextManager") as mock_context_manager,
        ):
            mock_mcp_provider = AsyncMock()
            mock_mcp_provider.list_tools.return_value = []
            mock_provider_factory.create_default_provider.return_value = (
                mock_mcp_provider
            )

            mock_context_mgr = AsyncMock()
            mock_context = AsyncMock()
            mock_context.get_messages_for_llm.return_value = [
                {"role": "system", "content": "You are a test agent"},
                {"role": "user", "content": "Hello"},
            ]
            mock_context_manager.create_memory_manager.return_value = mock_context_mgr

            mock_llm = AsyncMock()
            mock_response = LLMResponse(content="Hello! How can I help you?")
            mock_llm.generate.return_value = mock_response

            agent = AgenticAgent(config, llm_provider=mock_llm)
            agent.context = mock_context

            response = await agent.run("Hello")

            assert response == "Hello! How can I help you?"
            mock_context.add_message.assert_any_call("user", "Hello")
            mock_context.add_message.assert_any_call(
                "assistant", "Hello! How can I help you?"
            )
            mock_context_mgr.update_context.assert_called_once_with(mock_context)

    async def test_run_with_tool_calls(self):
        """测试带工具调用的响应。"""
        config = self.create_test_config()

        with (
            patch("src.agentic.agent.create_llm_provider"),
            patch("src.agentic.agent.MCPProviderFactory") as mock_provider_factory,
            patch("src.agentic.agent.ContextManager") as mock_context_manager,
        ):
            # 模拟工具
            mock_tool = MagicMock()
            mock_tool.namespaced_name = "test_server_test_tool"
            mock_tool.description = "A test tool"
            mock_tool.parameters = {"type": "object"}

            mock_mcp_provider = AsyncMock()
            mock_mcp_provider.list_tools.return_value = [mock_tool]
            mock_mcp_provider.call_tool.return_value = {
                "content": [{"type": "text", "text": "Tool executed successfully"}]
            }
            mock_provider_factory.create_default_provider.return_value = (
                mock_mcp_provider
            )

            mock_context_mgr = AsyncMock()
            mock_context = AsyncMock()
            mock_context.get_messages_for_llm.side_effect = [
                [{"role": "user", "content": "Use the test tool"}],
                [
                    {"role": "user", "content": "Use the test tool"},
                    {"role": "assistant", "content": "I'll use the test tool"},
                    {
                        "role": "user",
                        "content": "工具结果:\n- test_server_test_tool: Tool executed successfully\n",
                    },
                ],
            ]
            mock_context_manager.create_memory_manager.return_value = mock_context_mgr

            mock_llm = AsyncMock()
            # 第一次调用返回工具调用，第二次返回最终响应
            mock_responses = [
                LLMResponse(
                    content="I'll use the test tool",
                    tool_calls=[ToolCall(name="test_server_test_tool", arguments={})],
                ),
                LLMResponse(content="Task completed successfully!"),
            ]
            mock_llm.generate.side_effect = mock_responses

            agent = AgenticAgent(config, llm_provider=mock_llm)
            agent.context = mock_context

            response = await agent.run("Use the test tool")

            assert response == "Task completed successfully!"
            mock_mcp_provider.call_tool.assert_called_once_with(
                tool_name="test_server_test_tool", arguments={}
            )

    async def test_clear_history(self):
        """测试清除历史。"""
        config = self.create_test_config()

        with patch("src.agentic.agent.ContextManager") as mock_context_manager:
            mock_context_mgr = AsyncMock()
            mock_context = AsyncMock()
            mock_context_manager.create_memory_manager.return_value = mock_context_mgr

            agent = AgenticAgent(config)
            agent.context = mock_context

            await agent.clear_history(keep_system=True)

            mock_context.clear_history.assert_called_once_with(True)
            mock_context_mgr.update_context.assert_called_once_with(mock_context)

    async def test_get_history(self):
        """测试获取历史。"""
        config = self.create_test_config()

        with patch("src.agentic.agent.ContextManager") as mock_context_manager:
            mock_context_mgr = AsyncMock()
            mock_context = AsyncMock()
            mock_context.get_messages_for_llm.return_value = [
                {"role": "system", "content": "You are a test agent"},
                {"role": "user", "content": "Hello"},
            ]
            mock_context_manager.create_memory_manager.return_value = mock_context_mgr

            agent = AgenticAgent(config)
            agent.context = mock_context

            history = agent.get_history()

            assert len(history) == 2
            assert history[0]["role"] == "system"
            assert history[1]["role"] == "user"

    async def test_get_health_status(self):
        """测试获取健康状态。"""
        config = self.create_test_config()

        with (
            patch("src.agentic.agent.create_llm_provider"),
            patch("src.agentic.agent.MCPProviderFactory") as mock_provider_factory,
            patch("src.agentic.agent.ContextManager") as mock_context_manager,
        ):
            mock_mcp_provider = AsyncMock()
            mock_mcp_provider.health_check.return_value = {
                "healthy": True,
                "total_servers": 1,
                "connected_servers": 1,
            }
            mock_provider_factory.create_default_provider.return_value = (
                mock_mcp_provider
            )

            mock_context_mgr = AsyncMock()
            mock_context = AsyncMock()
            mock_context.conversation_id = "test_conversation"
            mock_context.get_message_count.return_value = 5
            mock_context.get_token_estimate.return_value = 100
            mock_context_manager.create_memory_manager.return_value = mock_context_mgr

            agent = AgenticAgent(config, conversation_id="test_conversation")
            agent.context = mock_context

            health = await agent.get_health_status()

            assert health["name"] == "test_agent"
            assert health["conversation_id"] == "test_conversation"
            assert health["mcp_provider"]["healthy"] is True
            assert health["context"]["message_count"] == 5
            assert health["context"]["token_estimate"] == 100
            assert health["config"]["max_iterations"] == 10


@pytest.mark.integration
@pytest.mark.asyncio
class TestAgenticAgentIntegration:
    """AgenticAgent 集成测试。"""

    async def test_agent_lifecycle(self):
        """测试智能体完整生命周期。"""
        config = AgentConfig(
            name="integration_test_agent",
            instruction="You are an integration test agent",
            llm_config=LLMConfig(provider="openai", api_key="test_key", model="gpt-4"),
            max_iterations=2,
        )

        with patch("src.agentic.agent.create_llm_provider") as mock_create_llm:
            mock_llm = AsyncMock()
            mock_response = LLMResponse(content="Integration test response")
            mock_llm.generate.return_value = mock_response
            mock_create_llm.return_value = mock_llm

            async with AgenticAgent(config).connect() as agent:
                response = await agent.run("Test input")
                assert response == "Integration test response"

                history = agent.get_history()
                assert len(history) >= 2  # At least system and user messages
