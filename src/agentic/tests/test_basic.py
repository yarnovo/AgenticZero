"""基本功能测试。"""

import pytest

from agentic import AgentSettings, LLMSettings, MCPServerSettings


@pytest.mark.unit
def test_llm_config_creation():
    """测试LLM配置创建。"""
    config = LLMSettings(
        provider="openai",
        api_key="test-key",
        model="gpt-4"
    )
    assert config.provider == "openai"
    assert config.api_key == "test-key"
    assert config.model == "gpt-4"


@pytest.mark.unit
def test_mcp_server_config_creation():
    """测试MCP服务器配置创建。"""
    config = MCPServerSettings(
        name="test-server",
        command="echo",
        args=["hello"]
    )
    assert config.name == "test-server"
    assert config.command == "echo"
    assert config.args == ["hello"]


@pytest.mark.unit
def test_agent_config_creation():
    """测试智能体配置创建。"""
    llm_settings = LLMSettings(
        provider="openai",
        api_key="test-key",
        model="gpt-4"
    )

    config = AgentSettings(
        name="test-agent",
        llm_settings=llm_settings
    )

    assert config.name == "test-agent"
    assert config.llm_settings.provider == "openai"


@pytest.mark.unit
def test_agent_config_add_mcp_server():
    """测试向智能体配置添加MCP服务器。"""
    llm_settings = LLMSettings(
        provider="openai",
        api_key="test-key",
        model="gpt-4"
    )

    config = AgentSettings(
        name="test-agent",
        llm_settings=llm_settings
    )

    config.add_mcp_server("filesystem", "npx", ["-y", "@modelcontextprotocol/server-filesystem"])

    assert "filesystem" in config.mcp_servers
    assert config.mcp_servers["filesystem"].command == "npx"
