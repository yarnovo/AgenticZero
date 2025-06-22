#!/usr/bin/env python3
"""测试使用官方 SDK 的最小化智能体实现。"""

import asyncio
import sys
from pathlib import Path

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent))

from minimal_agentic import AgentConfig, LLMProvider, MCPClientInterface, MinimalAgent
from minimal_agentic.llm import AnthropicProvider, OpenAIProvider


async def test_sdk_imports() -> bool:
    """测试官方 SDK 导入。"""
    print("测试 1：官方 SDK 导入")

    try:
        # 测试 MCP SDK
        import mcp
        import mcp.client.stdio

        print("✓ MCP SDK 导入成功")

        # 测试 OpenAI SDK
        import openai

        print("✓ OpenAI SDK 导入成功")

        # 测试 Anthropic SDK
        import anthropic

        print("✓ Anthropic SDK 导入成功")

    except ImportError as e:
        print(f"✗ SDK 导入失败: {e}")
        return False

    print()
    return True


async def test_llm_providers() -> None:
    """测试 LLM 提供商创建。"""
    print("测试 2: LLM 提供商初始化")

    # 测试 OpenAI 提供商
    try:
        openai_provider = OpenAIProvider(api_key="test-key", model="gpt-3.5-turbo")
        assert isinstance(openai_provider.client, object)
        print("✓ OpenAI 提供商创建成功")
    except Exception as e:
        print(f"✗ OpenAI 提供商创建失败: {e}")

    # 测试 Anthropic 提供商
    try:
        anthropic_provider = AnthropicProvider(
            api_key="test-key", model="claude-3-opus-20240229",
        )
        assert isinstance(anthropic_provider.client, object)
        print("✓ Anthropic 提供商创建成功")
    except Exception as e:
        print(f"✗ Anthropic 提供商创建失败: {e}")

    print()


async def test_agent_creation() -> None:
    """测试智能体创建。"""
    print("测试 3: 智能体创建和配置")

    config = AgentConfig(
        name="test_agent",
        instruction="你是一个测试助手。",
        llm_config={
            "provider": "openai",
            "api_key": "test-key",
            "model": "gpt-3.5-turbo",
        },
    )

    try:
        agent = MinimalAgent(config)
        assert agent.name == "test_agent"
        assert isinstance(agent.llm_provider, LLMProvider)
        assert isinstance(agent.mcp_client, MCPClientInterface)
        print("✓ 智能体创建成功")
        print(f"  - 名称: {agent.name}")
        print(f"  - LLM 提供商类型: {type(agent.llm_provider).__name__}")
        print(f"  - MCP 客户端类型: {type(agent.mcp_client).__name__}")
    except Exception as e:
        print(f"✗ 智能体创建失败: {e}")

    print()


async def test_mcp_client() -> None:
    """测试 MCP 客户端基本功能。"""
    print("测试 4: MCP 客户端基本功能")

    from minimal_agentic.mcp_client import DefaultMCPClient

    client = DefaultMCPClient()

    # 测试初始状态
    assert len(client.servers) == 0
    print("✓ MCP 客户端初始化成功")

    # 测试工具列表(应该为空)
    tools = await client.list_tools()
    assert len(tools) == 0
    print("✓ 空工具列表测试通过")

    print()


def main() -> None:
    """运行所有测试。"""
    print("=" * 50)
    print("官方 SDK 集成测试")
    print("=" * 50)
    print()

    # 运行测试
    asyncio.run(test_sdk_imports())
    asyncio.run(test_llm_providers())
    asyncio.run(test_agent_creation())
    asyncio.run(test_mcp_client())

    print("=" * 50)
    print("基础测试完成!")
    print("=" * 50)

    print("\n注意:")
    print("- 这些是基础单元测试,不需要实际的 API 密钥")
    print("- 完整的集成测试需要有效的 API 密钥和运行中的 MCP 服务器")
    print("- 请查看 example.py 了解完整的使用示例")


if __name__ == "__main__":
    main()
