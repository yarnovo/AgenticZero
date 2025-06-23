"""Ollama 集成测试。"""

from unittest.mock import MagicMock, patch

import pytest

from src.agent import Agent, AgentSettings, LLMSettings
from src.agent.model_provider import OllamaProvider, OllamaSession


@pytest.mark.asyncio
@pytest.mark.unit
async def test_ollama_session_initialize():
    """测试Ollama会话初始化。"""
    config = LLMSettings(
        provider="ollama",
        model="llama3.2",
        base_url="http://localhost:11434",
        temperature=0.7,
    )

    session = OllamaSession(config)

    # Mock requests.get
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        await session.initialize()

        assert session._initialized is True
        mock_get.assert_called_once_with("http://localhost:11434/api/tags", timeout=5)


@pytest.mark.asyncio
@pytest.mark.unit
async def test_ollama_session_chat():
    """测试Ollama非流式对话。"""
    config = LLMSettings(
        provider="ollama",
        model="llama3.2",
        base_url="http://localhost:11434",
        temperature=0.7,
        max_tokens=512,
    )

    session = OllamaSession(config)
    session._initialized = True

    # Mock请求响应
    mock_response_data = {"message": {"content": "你好！我是Llama助手。"}}

    with patch("requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data
        mock_post.return_value = mock_response

        messages = [{"role": "user", "content": "你好"}]
        result = await session.chat(messages)

        # 验证结果
        assert result["content"] == "你好！我是Llama助手。"
        assert "tool_calls" not in result or len(result["tool_calls"]) == 0

        # 验证请求参数
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[1]["json"]["model"] == "llama3.2"
        assert call_args[1]["json"]["messages"] == messages
        assert call_args[1]["json"]["stream"] is False
        assert call_args[1]["json"]["options"]["temperature"] == 0.7
        assert call_args[1]["json"]["options"]["num_predict"] == 512


@pytest.mark.asyncio
@pytest.mark.unit
async def test_ollama_session_chat_with_tools():
    """测试Ollama带工具调用的对话。"""
    config = LLMSettings(
        provider="ollama",
        model="llama3.2",
        base_url="http://localhost:11434",
    )

    session = OllamaSession(config)
    session._initialized = True

    # Mock带工具调用的响应
    mock_response_data = {
        "message": {
            "content": "我来查询天气信息。",
            "tool_calls": [
                {"function": {"name": "get_weather", "arguments": '{"city": "北京"}'}}
            ],
        }
    }

    with patch("requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data
        mock_post.return_value = mock_response

        messages = [{"role": "user", "content": "北京天气怎么样？"}]
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "获取天气信息",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "city": {"type": "string", "description": "城市名称"}
                        },
                    },
                },
            }
        ]

        result = await session.chat(messages, tools)

        # 验证结果
        assert result["content"] == "我来查询天气信息。"
        assert len(result["tool_calls"]) == 1
        assert result["tool_calls"][0]["function"]["name"] == "get_weather"
        assert result["tool_calls"][0]["function"]["arguments"] == '{"city": "北京"}'


@pytest.mark.asyncio
@pytest.mark.unit
async def test_ollama_session_chat_stream():
    """测试Ollama流式对话。"""
    config = LLMSettings(
        provider="ollama",
        model="llama3.2",
        base_url="http://localhost:11434",
    )

    session = OllamaSession(config)
    session._initialized = True

    # Mock流式响应数据
    mock_stream_data = [
        '{"message": {"content": "你好"}, "done": false}',
        '{"message": {"content": "！我是"}, "done": false}',
        '{"message": {"content": "Llama助手"}, "done": false}',
        '{"message": {}, "done": true}',
    ]

    def mock_iter_lines():
        for line in mock_stream_data:
            yield line.encode("utf-8")

    with patch("requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.iter_lines.return_value = mock_iter_lines()
        mock_post.return_value = mock_response

        messages = [{"role": "user", "content": "你好"}]
        chunks = []

        async for chunk in session.chat_stream(messages):
            chunks.append(chunk)

        # 验证流式响应
        assert len(chunks) == 3  # 3个内容片段
        assert all(chunk["type"] == "content" for chunk in chunks)
        content_parts = [chunk["content"] for chunk in chunks]
        assert content_parts == ["你好", "！我是", "Llama助手"]


@pytest.mark.asyncio
@pytest.mark.unit
async def test_ollama_provider():
    """测试Ollama提供商。"""
    config = LLMSettings(
        provider="ollama",
        model="llama3.2",
        base_url="http://localhost:11434",
    )

    provider = OllamaProvider(config)

    # 测试提供商名称
    assert provider.get_provider_name() == "ollama"

    # 测试创建会话
    session = await provider.create_session()
    assert isinstance(session, OllamaSession)
    assert session.config == config


@pytest.mark.asyncio
@pytest.mark.unit
async def test_agent_with_ollama():
    """测试使用Ollama的Agent。"""
    settings = AgentSettings(
        name="ollama_agent",
        instruction="你是一个使用Ollama本地模型的助手。",
        llm_settings=LLMSettings(
            provider="ollama",
            model="llama3.2",
            base_url="http://localhost:11434",
            temperature=0.8,
        ),
    )

    agent = Agent(config=settings)

    # Mock Ollama响应
    with patch("requests.get") as mock_get, patch("requests.post") as mock_post:
        # Mock初始化
        mock_get_response = MagicMock()
        mock_get_response.status_code = 200
        mock_get.return_value = mock_get_response

        # Mock对话响应
        mock_post_response = MagicMock()
        mock_post_response.status_code = 200
        mock_post_response.json.return_value = {
            "message": {"content": "你好！我是运行在本地的Llama模型。"}
        }
        mock_post.return_value = mock_post_response

        try:
            await agent.initialize()
            response = await agent.run("你好")

            assert response == "你好！我是运行在本地的Llama模型。"

            # 验证使用了正确的配置
            mock_post.assert_called()
            call_data = mock_post.call_args[1]["json"]
            assert call_data["model"] == "llama3.2"
            assert call_data["options"]["temperature"] == 0.8

        finally:
            await agent.close()


@pytest.mark.asyncio
@pytest.mark.unit
async def test_ollama_session_error_handling():
    """测试Ollama会话错误处理。"""
    config = LLMSettings(
        provider="ollama",
        model="llama3.2",
        base_url="http://localhost:11434",
    )

    session = OllamaSession(config)

    # 测试初始化失败
    with patch("requests.get") as mock_get:
        mock_get.side_effect = Exception("连接失败")

        with pytest.raises(RuntimeError, match="初始化Ollama会话失败"):
            await session.initialize()

    # 测试未初始化时调用chat
    with pytest.raises(RuntimeError, match="Ollama会话未初始化"):
        await session.chat([{"role": "user", "content": "test"}])

    # 测试请求失败
    session._initialized = True
    with patch("requests.post") as mock_post:
        mock_post.side_effect = Exception("请求失败")

        with pytest.raises(Exception, match="请求失败"):
            await session.chat([{"role": "user", "content": "test"}])


@pytest.mark.asyncio
@pytest.mark.integration
async def test_ollama_stream_with_agent():
    """测试Agent的Ollama流式响应。"""
    settings = AgentSettings(
        name="ollama_stream_agent",
        instruction="你是一个本地Llama助手。",
        llm_settings=LLMSettings(
            provider="ollama",
            model="llama3.2",
            base_url="http://localhost:11434",
        ),
    )

    agent = Agent(config=settings)

    # Mock流式响应
    mock_stream_data = [
        '{"message": {"content": "本地"}, "done": false}',
        '{"message": {"content": "模型"}, "done": false}',
        '{"message": {"content": "响应"}, "done": false}',
        '{"message": {}, "done": true}',
    ]

    def mock_iter_lines():
        for line in mock_stream_data:
            yield line.encode("utf-8")

    with patch("requests.get") as mock_get, patch("requests.post") as mock_post:
        # Mock初始化
        mock_get_response = MagicMock()
        mock_get_response.status_code = 200
        mock_get.return_value = mock_get_response

        # Mock流式响应
        mock_post_response = MagicMock()
        mock_post_response.status_code = 200
        mock_post_response.iter_lines.return_value = mock_iter_lines()
        mock_post.return_value = mock_post_response

        try:
            await agent.initialize()

            chunks = []
            async for chunk in agent.run_stream("你好"):
                chunks.append(chunk)

            # 验证包含内容片段
            content_chunks = [c for c in chunks if c["type"] == "content"]
            assert len(content_chunks) == 3
            assert content_chunks[0]["content"] == "本地"
            assert content_chunks[1]["content"] == "模型"
            assert content_chunks[2]["content"] == "响应"

            # 验证包含完成标记
            complete_chunks = [c for c in chunks if c["type"] == "complete"]
            assert len(complete_chunks) == 1

        finally:
            await agent.close()
