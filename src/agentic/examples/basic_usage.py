"""基本用法示例。"""

import asyncio
import logging
import os

from ..agent import AgenticAgent
from ..config import AgentConfig, LLMConfig

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def basic_agentic_example():
    """基本 AgenticAgent 使用示例。"""

    # 创建智能体配置
    config = AgentConfig(
        name="basic_agent",
        instruction="你是一个有用的助手，可以帮助用户完成各种任务。",
        llm_config=LLMConfig(
            provider="openai",  # 或 "anthropic"
            api_key=os.getenv("OPENAI_API_KEY", "your-api-key-here"),
            model="gpt-4",
            temperature=0.7,
            max_tokens=2048,
        ),
        max_iterations=5,
        debug=True,
    )

    # 使用上下文管理器确保资源正确清理
    async with AgenticAgent(config).connect() as agent:
        print(f"智能体 '{agent.name}' 已初始化")

        # 基本对话
        response = await agent.run("你好！请介绍一下你自己。")
        print(f"智能体回复: {response}")

        # 查看对话历史
        history = agent.get_history()
        print(f"对话历史条数: {len(history)}")

        # 检查健康状态
        health = await agent.get_health_status()
        print(f"健康状态: {health}")


async def custom_components_example():
    """使用自定义组件的示例。"""
    from ..context_manager import ContextManager
    from ..mcp_provider import MCPProviderFactory
    from ..session_manager import DefaultSessionManager

    # 创建自定义组件
    session_manager = DefaultSessionManager()
    context_manager = ContextManager.create_memory_manager()
    mcp_provider = MCPProviderFactory.create_default_provider(session_manager)

    config = AgentConfig(
        name="custom_agent",
        instruction="你是一个使用自定义组件的智能体。",
        llm_config=LLMConfig(
            provider="openai",
            api_key=os.getenv("OPENAI_API_KEY", "your-api-key-here"),
            model="gpt-3.5-turbo",
        ),
    )

    # 使用自定义组件创建智能体
    agent = AgenticAgent(
        config=config,
        mcp_provider=mcp_provider,
        context_manager=context_manager,
        session_manager=session_manager,
        conversation_id="custom_conversation_001",
    )

    async with agent.connect() as connected_agent:
        response = await connected_agent.run("使用自定义组件的智能体，你好！")
        print(f"自定义智能体回复: {response}")


async def persistent_context_example():
    """持久化上下文示例。"""
    from ..context_manager import ContextManager

    # 使用持久化上下文管理器
    context_manager = ContextManager.create_persistent_manager(
        "./agent_conversations.json"
    )

    config = AgentConfig(
        name="persistent_agent",
        instruction="你是一个会记住对话历史的智能体。",
        llm_config=LLMConfig(
            provider="openai",
            api_key=os.getenv("OPENAI_API_KEY", "your-api-key-here"),
            model="gpt-4",
        ),
    )

    conversation_id = "persistent_conversation_001"

    # 第一次对话
    agent1 = AgenticAgent(
        config=config, context_manager=context_manager, conversation_id=conversation_id
    )

    async with agent1.connect() as connected_agent:
        response1 = await connected_agent.run("我叫张三，我喜欢编程。")
        print(f"第一次对话: {response1}")

    # 第二次对话（新的智能体实例，但使用相同的对话ID）
    agent2 = AgenticAgent(
        config=config, context_manager=context_manager, conversation_id=conversation_id
    )

    async with agent2.connect() as connected_agent:
        response2 = await connected_agent.run("你还记得我的名字吗？")
        print(f"第二次对话: {response2}")


async def health_monitoring_example():
    """健康监控示例。"""
    config = AgentConfig(
        name="monitored_agent",
        instruction="你是一个被监控的智能体。",
        llm_config=LLMConfig(
            provider="openai",
            api_key=os.getenv("OPENAI_API_KEY", "your-api-key-here"),
            model="gpt-4",
        ),
    )

    async with AgenticAgent(config).connect() as agent:
        # 定期检查健康状态
        for i in range(3):
            print(f"\n--- 健康检查 {i + 1} ---")
            health = await agent.get_health_status()

            print(f"智能体名称: {health['name']}")
            print(f"对话ID: {health['conversation_id']}")
            print(f"MCP提供商健康: {health['mcp_provider']['healthy']}")
            print(f"消息数量: {health['context']['message_count']}")
            print(f"Token估算: {health['context']['token_estimate']}")

            # 执行一次对话
            await agent.run(f"这是第 {i + 1} 次对话测试。")

            # 等待一秒
            await asyncio.sleep(1)


async def error_handling_example():
    """错误处理示例。"""
    config = AgentConfig(
        name="error_prone_agent",
        instruction="你是一个测试错误处理的智能体。",
        llm_config=LLMConfig(
            provider="invalid_provider",  # 故意使用无效的提供商
            api_key="invalid_key",
            model="invalid_model",
        ),
    )

    try:
        async with AgenticAgent(config).connect() as agent:
            await agent.run("这应该会出错")
    except Exception as e:
        print(f"捕获到预期的错误: {e}")

    # 使用有效配置重试
    valid_config = AgentConfig(
        name="recovered_agent",
        instruction="你是一个从错误中恢复的智能体。",
        llm_config=LLMConfig(
            provider="openai",
            api_key=os.getenv("OPENAI_API_KEY", "your-api-key-here"),
            model="gpt-4",
        ),
    )

    async with AgenticAgent(valid_config).connect() as agent:
        response = await agent.run("错误已修复，现在可以正常工作了！")
        print(f"恢复后的回复: {response}")


async def main():
    """运行所有示例。"""
    examples = [
        ("基本用法", basic_agentic_example),
        ("自定义组件", custom_components_example),
        ("持久化上下文", persistent_context_example),
        ("健康监控", health_monitoring_example),
        ("错误处理", error_handling_example),
    ]

    for name, example_func in examples:
        print(f"\n{'=' * 50}")
        print(f"运行示例: {name}")
        print(f"{'=' * 50}")

        try:
            await example_func()
            print(f"✅ {name} 示例完成")
        except Exception as e:
            print(f"❌ {name} 示例出错: {e}")
            logger.exception(f"Error in {name} example")

        print(f"{'=' * 50}\n")


if __name__ == "__main__":
    # 运行示例
    print("AgenticAgent 示例演示")
    print("注意：运行前请设置正确的 API 密钥")

    asyncio.run(main())
