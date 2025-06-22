#!/usr/bin/env python3
"""MinimalAgent 的使用示例

本示例演示如何：
1. 配置 MCP 服务器
2. 设置 LLM 提供商
3. 使用自动工具调用运行智能体
4. 使用依赖注入自定义组件
"""

import asyncio
import os
from typing import Any

from minimal_agentic import (
    AgentConfig,
    MCPClientInterface,
    MCPServerConfig,
    MinimalAgent,
    create_llm_provider,
)


async def basic_example() -> None:
    """基本示例：使用文件系统和网页抓取服务器。"""
    config = AgentConfig(
        name="example_agent",
        instruction="""你是一个可以访问文件系统和网页抓取工具的有用助手。
        你可以读取文件、列出目录和获取网页内容。
        总是使用适当的工具来回答用户问题。""",
        llm_config={
            "provider": "openai",  # 或 "anthropic"
            "api_key": os.getenv("OPENAI_API_KEY", "your-api-key-here"),
            "model": "gpt-4",
            "temperature": 0.7,
            "max_tokens": 2048,
        },
        max_iterations=5,
        debug=True,
    )

    # 添加 MCP 服务器
    config.add_mcp_server(
        name="filesystem",
        command="npx",
        args=["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
    )

    config.add_mcp_server(name="fetch", command="uvx", args=["mcp-server-fetch"])

    # 使用智能体
    async with MinimalAgent(config).connect() as agent:
        # 示例 1：列出可用工具
        print("=== 可用工具 ===")
        tools = await agent.mcp_client.list_tools()
        for tool in tools:
            print(f"- {tool['_namespaced_name']}: {tool.get('description', '无描述')}")
        print()

        # 示例 2：简单查询（不需要工具）
        print("=== 简单查询 ===")
        response = await agent.run("法国的首都是什么？")
        print(f"响应: {response}\n")

        # 示例 3：需要使用工具的查询
        print("=== 工具使用查询 ===")
        response = await agent.run(
            "在 /tmp 中创建一个名为 test.txt 的文件，内容为 'Hello from MinimalAgent!'",
        )
        print(f"响应: {response}\n")

        # 示例 4：多步骤任务
        print("=== 多步骤任务 ===")
        response = await agent.run("""
        1. 检查 /tmp 中有哪些文件
        2. 如果 test.txt 存在，读取其内容
        3. 获取 https://example.com 的标题
        """)
        print(f"响应: {response}\n")

        # 示例 5：清除历史并重新开始
        agent.clear_history()
        response = await agent.run("我们刚才做了什么？")
        print(f"清除历史后的响应: {response}\n")


# 自定义 MCP 客户端示例
class MockMCPClient(MCPClientInterface):
    """用于测试的模拟 MCP 客户端。"""

    async def list_tools(self) -> list[dict[str, Any]]:
        return [
            {
                "name": "get_time",
                "_namespaced_name": "mock_get_time",
                "description": "获取当前时间",
                "inputSchema": {"type": "object", "properties": {}},
            },
        ]

    async def call_tool(
        self, tool_name: str, arguments: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if tool_name == "mock_get_time":
            return {
                "content": [{"type": "text", "text": "当前时间是 2024-01-01 12:00:00"}],
            }
        raise ValueError(f"未知工具: {tool_name}")

    async def initialize(self) -> None:
        print("模拟 MCP 客户端已初始化")

    async def close(self) -> None:
        print("模拟 MCP 客户端已关闭")


async def dependency_injection_example() -> None:
    """依赖注入示例：使用自定义 MCP 客户端和 LLM 提供商。"""
    # 配置
    config = AgentConfig(
        name="custom_agent",
        instruction="你是一个可以获取时间的助手。",
        llm_config={
            "provider": "openai",
            "api_key": os.getenv("OPENAI_API_KEY", "your-api-key"),
            "model": "gpt-3.5-turbo",
        },
    )

    # 创建自定义组件
    custom_mcp_client = MockMCPClient()
    custom_llm_provider = create_llm_provider(
        provider_type="openai",
        api_key=config.llm_config.api_key,
        model=config.llm_config.model,
        temperature=0.5,
    )

    # 使用依赖注入创建智能体
    agent = MinimalAgent(
        config=config, mcp_client=custom_mcp_client, llm_provider=custom_llm_provider,
    )

    async with agent.connect() as connected_agent:
        response = await connected_agent.run("现在几点了？")
        print(f"使用自定义组件的响应: {response}")


async def interactive_example() -> None:
    """交互式示例：带有自定义配置和错误处理。"""
    # 从字典配置
    config_dict = {
        "name": "interactive_agent",
        "instruction": "你是一个具有多种功能的高级 AI 助手。",
        "mcp_servers": {
            "filesystem": {
                "name": "filesystem",
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home"],
            },
        },
        "llm_config": {
            "provider": "anthropic",
            "api_key": os.getenv("ANTHROPIC_API_KEY", "your-anthropic-key"),
            "model": "claude-3-opus-20240229",
            "temperature": 0.5,
        },
        "max_iterations": 3,
    }

    agent = MinimalAgent(config_dict)

    try:
        await agent.initialize()

        # 自定义交互循环
        while True:
            user_input = input("\n你: ")
            if user_input.lower() in ["退出", "quit", "exit", "bye"]:
                break

            response = await agent.run(user_input)
            print(f"\n智能体: {response}")

            # 显示对话历史长度
            print(f"(历史记录: {len(agent.get_history())} 条消息)")

    except KeyboardInterrupt:
        print("\n用户中断")
    except Exception as e:
        print(f"错误: {e}")
    finally:
        await agent.close()


async def minimal_example() -> None:
    """最小化示例 - 只包含必要的部分。"""
    config = AgentConfig(
        name="minimal",
        llm_config={
            "provider": "openai",
            "api_key": os.getenv("OPENAI_API_KEY"),
            "model": "gpt-3.5-turbo",
        },
    )

    # 添加单个 MCP 服务器
    config.mcp_servers["fetch"] = MCPServerConfig(
        name="fetch", command="uvx", args=["mcp-server-fetch"],
    )

    async with MinimalAgent(config).connect() as agent:
        result = await agent.run("weather.com 上显示的天气如何？")
        print(result)


if __name__ == "__main__":
    print("MinimalAgent 示例")
    print("=" * 50)

    # 运行基本示例
    asyncio.run(basic_example())

    # 取消注释以运行其他示例：
    # asyncio.run(dependency_injection_example())
    # asyncio.run(interactive_example())
    # asyncio.run(minimal_example())
