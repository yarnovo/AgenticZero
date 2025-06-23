"""流式响应功能测试。"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.agent import Agent, AgentSettings, LLMSettings


@pytest.mark.asyncio
@pytest.mark.unit
async def test_agent_run_stream_basic():
    """测试Agent流式响应的基本功能。"""

    # 创建模拟的流式响应
    async def mock_stream_response():
        chunks = [
            {"type": "iteration", "current": 1, "max": 10},
            {"type": "content", "content": "你好"},
            {"type": "content", "content": "，我是"},
            {"type": "content", "content": "智能助手"},
            {
                "type": "complete",
                "final_response": "你好，我是智能助手",
                "iterations": 1,
            },
        ]
        for chunk in chunks:
            yield chunk

    # 配置
    settings = AgentSettings(
        llm_settings=LLMSettings(
            provider="openai",
            model="gpt-3.5-turbo",
            api_key="test-key",
            temperature=0.7,
        )
    )

    # 创建智能体
    agent = Agent(config=settings)

    # Mock核心引擎的流式处理方法
    with patch.object(agent.core_engine, "process_input_stream") as mock_stream:
        mock_stream.return_value = mock_stream_response()

        # 收集所有流式响应片段
        chunks = []
        async for chunk in agent.run_stream("你好"):
            chunks.append(chunk)

        # 验证响应
        assert len(chunks) == 5
        assert chunks[0]["type"] == "iteration"
        assert chunks[1]["type"] == "content"
        assert chunks[1]["content"] == "你好"
        assert chunks[4]["type"] == "complete"
        assert chunks[4]["final_response"] == "你好，我是智能助手"


@pytest.mark.asyncio
@pytest.mark.unit
async def test_agent_run_stream_with_tools():
    """测试带工具调用的流式响应。"""

    # 创建模拟的流式响应（包含工具调用）
    async def mock_stream_response_with_tools():
        chunks = [
            {"type": "iteration", "current": 1, "max": 10},
            {"type": "content", "content": "让我查询一下天气"},
            {"type": "tool_call", "tool": "get_weather", "arguments": {"city": "北京"}},
            {
                "type": "tool_result",
                "tool": "get_weather",
                "success": True,
                "result": "晴天，温度25°C",
            },
            {"type": "iteration", "current": 2, "max": 10},
            {"type": "content", "content": "北京今天的天气是晴天，温度25°C"},
            {
                "type": "complete",
                "final_response": "北京今天的天气是晴天，温度25°C",
                "iterations": 2,
            },
        ]
        for chunk in chunks:
            yield chunk

    # 配置
    settings = AgentSettings(
        llm_settings=LLMSettings(
            provider="openai",
            model="gpt-3.5-turbo",
            api_key="test-key",
        )
    )

    # 创建智能体
    agent = Agent(config=settings)

    # Mock核心引擎的流式处理方法
    with patch.object(agent.core_engine, "process_input_stream") as mock_stream:
        mock_stream.return_value = mock_stream_response_with_tools()

        # 收集所有流式响应片段
        chunks = []
        async for chunk in agent.run_stream("北京天气怎么样？"):
            chunks.append(chunk)

        # 验证响应
        assert len(chunks) == 7

        # 验证工具调用
        tool_call_chunk = next(c for c in chunks if c["type"] == "tool_call")
        assert tool_call_chunk["tool"] == "get_weather"
        assert tool_call_chunk["arguments"] == {"city": "北京"}

        # 验证工具结果
        tool_result_chunk = next(c for c in chunks if c["type"] == "tool_result")
        assert tool_result_chunk["tool"] == "get_weather"
        assert tool_result_chunk["success"] is True
        assert "晴天" in tool_result_chunk["result"]


@pytest.mark.asyncio
@pytest.mark.unit
async def test_agent_run_stream_error_handling():
    """测试流式响应的错误处理。"""

    # 创建模拟的流式响应（包含错误）
    async def mock_stream_response_with_error():
        chunks = [
            {"type": "iteration", "current": 1, "max": 10},
            {"type": "content", "content": "处理中..."},
            {"type": "error", "error": "API调用失败: 超时"},
        ]
        for chunk in chunks:
            yield chunk

    # 配置
    settings = AgentSettings(
        llm_settings=LLMSettings(
            provider="openai",
            model="gpt-3.5-turbo",
            api_key="test-key",
        )
    )

    # 创建智能体
    agent = Agent(config=settings)

    # Mock核心引擎的流式处理方法
    with patch.object(agent.core_engine, "process_input_stream") as mock_stream:
        mock_stream.return_value = mock_stream_response_with_error()

        # 收集所有流式响应片段
        chunks = []
        async for chunk in agent.run_stream("测试错误"):
            chunks.append(chunk)

        # 验证响应
        assert len(chunks) == 3
        assert chunks[2]["type"] == "error"
        assert "API调用失败" in chunks[2]["error"]


@pytest.mark.asyncio
@pytest.mark.unit
async def test_openai_session_chat_stream():
    """测试OpenAI会话的流式响应实现。"""
    from src.agent.model_provider import OpenAISession

    # 模拟OpenAI流式响应
    mock_chunk1 = MagicMock()
    mock_chunk1.choices = [MagicMock()]
    mock_chunk1.choices[0].delta = MagicMock(content="你好", tool_calls=None)
    mock_chunk1.choices[0].finish_reason = None

    mock_chunk2 = MagicMock()
    mock_chunk2.choices = [MagicMock()]
    mock_chunk2.choices[0].delta = MagicMock(content="世界", tool_calls=None)
    mock_chunk2.choices[0].finish_reason = None

    mock_chunk3 = MagicMock()
    mock_chunk3.choices = [MagicMock()]
    mock_chunk3.choices[0].delta = MagicMock(content=None, tool_calls=None)
    mock_chunk3.choices[0].finish_reason = "stop"

    async def mock_stream():
        for chunk in [mock_chunk1, mock_chunk2, mock_chunk3]:
            yield chunk

    # 创建会话
    config = LLMSettings(
        provider="openai",
        model="gpt-3.5-turbo",
        api_key="test-key",
        temperature=0.7,
    )
    session = OpenAISession(config)
    session._initialized = True

    # Mock OpenAI客户端
    mock_client = AsyncMock()
    mock_client.chat.completions.create.return_value = mock_stream()
    session.client = mock_client

    # 测试流式响应
    messages = [{"role": "user", "content": "你好"}]
    chunks = []

    async for chunk in session.chat_stream(messages):
        chunks.append(chunk)

    # 验证响应
    assert len(chunks) == 2
    assert chunks[0] == {"type": "content", "content": "你好"}
    assert chunks[1] == {"type": "content", "content": "世界"}


@pytest.mark.asyncio
@pytest.mark.unit
async def test_llm_session_manager_chat_stream():
    """测试LLM会话管理器的流式聊天功能。"""
    from src.agent.llm_session_manager import LLMSessionManager
    from src.agent.model_provider import ModelProvider

    # 创建模拟的流式响应
    async def mock_chat_stream(messages, tools=None):
        yield {"type": "content", "content": "测试"}
        yield {"type": "content", "content": "响应"}

    # 创建模拟的会话
    mock_session = AsyncMock()
    mock_session.chat_stream = mock_chat_stream

    # 创建模拟的模型提供商
    mock_provider = AsyncMock(spec=ModelProvider)
    mock_provider.create_session.return_value = mock_session

    # 创建会话管理器
    manager = LLMSessionManager(mock_provider)
    manager._initialized = True
    manager.session = mock_session

    # 测试流式聊天
    messages = [{"role": "user", "content": "你好"}]
    chunks = []

    async for chunk in manager.chat_stream(messages):
        chunks.append(chunk)

    # 验证响应
    assert len(chunks) == 2
    assert chunks[0]["content"] == "测试"
    assert chunks[1]["content"] == "响应"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_core_engine_process_input_stream():
    """测试核心引擎的流式处理功能。"""
    from src.agent.core_engine import CoreEngine

    # 创建模拟的流式响应
    async def mock_chat_stream(messages, tools=None):
        yield {"type": "content", "content": "处理中"}
        yield {"type": "content", "content": "..."}

    # 创建模拟的依赖
    mock_llm_manager = AsyncMock()
    mock_llm_manager.chat_stream = mock_chat_stream

    mock_mcp_manager = AsyncMock()
    mock_mcp_manager.list_all_tools.return_value = []

    mock_context_manager = AsyncMock()
    mock_context = MagicMock()
    mock_context.get_current_messages.return_value = [
        {"role": "user", "content": "测试"}
    ]
    mock_context_manager.get_context.return_value = mock_context

    # 创建核心引擎
    engine = CoreEngine(
        llm_session_manager=mock_llm_manager,
        mcp_session_manager=mock_mcp_manager,
        context_manager=mock_context_manager,
        max_iterations=5,
    )
    engine._initialized = True

    # 测试流式处理
    chunks = []
    async for chunk in engine.process_input_stream("测试", "test-conversation"):
        chunks.append(chunk)

    # 验证响应
    assert any(c["type"] == "iteration" for c in chunks)
    assert any(c["type"] == "content" for c in chunks)
    assert any(c["type"] == "complete" for c in chunks)
