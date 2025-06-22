#!/usr/bin/env python3
"""Test script for the minimal agentic module.
This script tests the basic functionality without requiring actual MCP servers.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from minimal_agentic import AgentConfig, MinimalAgent


async def test_basic_functionality():
    """Test basic agent creation and configuration."""
    print("Test 1: Basic agent creation")

    config = AgentConfig(
        name="test_agent",
        instruction="You are a test assistant.",
        llm_config={
            "provider": "openai",
            "api_key": "test-key",
            "model": "gpt-3.5-turbo",
        },
    )

    assert config.name == "test_agent"
    assert config.instruction == "You are a test assistant."
    assert config.llm_config.provider == "openai"
    print("✓ Agent configuration created successfully")

    # Test adding MCP server
    config.add_mcp_server(name="test_server", command="echo", args=["test"])

    assert "test_server" in config.mcp_servers
    assert config.mcp_servers["test_server"].command == "echo"
    print("✓ MCP server added successfully")

    print()


async def test_config_from_dict():
    """Test creating configuration from dictionary."""
    print("Test 2: Configuration from dictionary")

    config_dict = {
        "name": "dict_agent",
        "instruction": "Test agent from dict",
        "mcp_servers": {
            "server1": {"name": "server1", "command": "test", "args": ["arg1", "arg2"]},
        },
        "llm_config": {
            "provider": "anthropic",
            "api_key": "test-anthropic-key",
            "model": "claude-3-opus-20240229",
        },
        "max_iterations": 3,
        "debug": True,
    }

    config = AgentConfig.from_dict(config_dict)

    assert config.name == "dict_agent"
    assert config.max_iterations == 3
    assert config.debug is True
    assert "server1" in config.mcp_servers
    print("✓ Configuration from dict successful")

    print()


async def test_agent_initialization():
    """Test agent initialization without actual connections."""
    print("Test 3: Agent initialization")

    config = AgentConfig(
        name="init_test",
        llm_config={"provider": "openai", "api_key": "test-key", "model": "gpt-4"},
    )

    agent = MinimalAgent(config)

    assert agent.name == "init_test"
    assert len(agent.conversation_history) == 0
    print("✓ Agent created successfully")

    # Test history management
    agent.conversation_history = [
        {"role": "system", "content": "Test"},
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi"},
    ]

    history = agent.get_history()
    assert len(history) == 3
    print("✓ History management working")

    agent.clear_history()
    # After clear, only system message should remain
    assert len(agent.conversation_history) == 1
    assert agent.conversation_history[0]["role"] == "system"
    print("✓ History clearing working")

    print()


def main():
    """Run all tests."""
    print("=" * 50)
    print("Minimal Agentic Module Tests")
    print("=" * 50)
    print()

    # Run tests
    asyncio.run(test_basic_functionality())
    asyncio.run(test_config_from_dict())
    asyncio.run(test_agent_initialization())

    print("=" * 50)
    print("All tests passed! ✓")
    print("=" * 50)

    print("\nNote: These are basic unit tests.")
    print("For full integration testing, you'll need:")
    print("- Valid API keys for OpenAI/Anthropic")
    print("- MCP servers installed and running")
    print("\nSee example.py for integration examples.")


if __name__ == "__main__":
    main()
