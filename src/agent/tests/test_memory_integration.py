"""测试记忆模块集成的示例代码。"""

import asyncio

import pytest

from ..core_engine import CoreEngine
from ..llm_session_manager import LLMSessionManager
from ..mcp_session_manager import MCPSessionManager
from ..memory_manager import MemoryManager, MemoryType
from ..memory_mcp_server import MemoryMCPServer
from ..message_history_manager import MessageHistoryManager
from ..model_provider import ModelProvider
from ..session_context_manager import SessionContextManager
from ..settings import AgentSettings


@pytest.mark.asyncio
@pytest.mark.integration
async def test_memory_integration():
    """测试记忆模块与上下文管理器的集成。"""
    # 创建各个组件
    settings = AgentSettings()
    model_provider = ModelProvider(model_config=settings.model_config)

    # 创建记忆管理器
    memory_manager = MemoryManager.create_memory_manager()

    # 创建消息历史管理器
    history_manager = MessageHistoryManager.create_memory_manager()

    # 创建会话上下文管理器，注入记忆管理器
    context_manager = SessionContextManager(
        history_manager=history_manager, memory_manager=memory_manager
    )

    # 创建LLM和MCP会话管理器
    llm_session_manager = LLMSessionManager(model_provider)
    mcp_session_manager = MCPSessionManager()

    # 创建核心引擎
    engine = CoreEngine(
        llm_session_manager=llm_session_manager,
        mcp_session_manager=mcp_session_manager,
        context_manager=context_manager,
        max_iterations=5,
    )

    # 初始化引擎
    await engine.initialize()

    try:
        # 测试场景1：存储一些记忆
        await memory_manager.store_memory(
            content="项目使用Python 3.11和pytest进行测试",
            memory_type=MemoryType.SEMANTIC,
            importance=0.8,
            metadata={"category": "技术栈"},
        )

        await memory_manager.store_memory(
            content="用户喜欢使用async/await异步编程模式",
            memory_type=MemoryType.LONG_TERM,
            importance=0.7,
            metadata={"category": "编程偏好"},
        )

        # 测试场景2：创建会话上下文
        conversation_id = "test_conv_001"
        context = await context_manager.create_context(
            conversation_id=conversation_id,
            system_instruction="你是一个有记忆能力的AI助手",
            enable_memory=True,
            memory_context_size=3,
        )

        # 测试场景3：模拟对话
        context.add_message("user", "我们的项目用什么语言开发？")
        context.add_message(
            "assistant",
            "根据我的记忆，你们的项目使用Python 3.11进行开发，并使用pytest进行测试。",
        )

        # 存储对话记忆
        await context.store_conversation_memory()

        # 测试场景4：获取包含记忆的消息上下文
        messages = context.get_current_messages()

        # 验证消息中包含记忆内容
        assert len(messages) >= 2  # 至少包含系统指令和记忆

        # 查找记忆消息
        memory_message = None
        for msg in messages:
            if msg["role"] == "system" and "相关记忆:" in msg["content"]:
                memory_message = msg
                break

        assert memory_message is not None, "应该包含记忆消息"
        assert "Python 3.11" in memory_message["content"], "记忆内容应该包含相关信息"

        # 测试场景5：更新上下文并验证记忆存储
        await context_manager.update_context(context, store_memory=True)

        # 验证记忆数量增加
        stats = await memory_manager.get_memory_stats()
        assert stats.total_memories >= 3  # 至少有3条记忆（2条初始 + 1条对话）

        print("✅ 记忆集成测试通过！")
        print(f"📊 记忆统计: {stats.total_memories} 条记忆")
        print(f"📝 记忆类型分布: {stats.by_type}")

    finally:
        # 清理
        await engine.close()


@pytest.mark.asyncio
@pytest.mark.unit
async def test_memory_mcp_server():
    """测试记忆MCP服务器功能。"""
    # 创建记忆管理器
    memory_manager = MemoryManager.create_memory_manager()

    # 创建MCP服务器
    memory_server = MemoryMCPServer(memory_manager)

    # 测试工具列表
    tools_result = await memory_server.server.list_tools()
    tools = tools_result.tools

    assert len(tools) == 8  # 应该有8个工具
    tool_names = [tool.name for tool in tools]
    assert "memory_store" in tool_names
    assert "memory_search" in tool_names
    assert "memory_get_recent" in tool_names
    assert "memory_get_important" in tool_names

    # 测试存储记忆
    store_result = await memory_server.server.call_tool(
        "memory_store",
        {"content": "测试记忆内容", "memory_type": "short_term", "importance": 0.6},
    )

    assert store_result.content
    assert "记忆已存储" in store_result.content[0].text

    # 测试搜索记忆
    search_result = await memory_server.server.call_tool(
        "memory_search", {"query": "测试", "limit": 5}
    )

    assert search_result.content
    assert "找到" in search_result.content[0].text

    print("✅ 记忆MCP服务器测试通过！")


if __name__ == "__main__":
    # 运行测试
    asyncio.run(test_memory_integration())
    asyncio.run(test_memory_mcp_server())
