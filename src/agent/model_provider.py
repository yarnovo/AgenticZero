"""模型提供商模块，提供与不同大模型提供商的集成。"""

import json
import logging
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from typing import Any

from .llm_session_manager import LLMSessionInterface
from .settings import LLMSettings

logger = logging.getLogger(__name__)


class ModelProvider(ABC):
    """模型提供商抽象基类，用于依赖注入。"""

    @abstractmethod
    async def create_session(self) -> LLMSessionInterface:
        """创建大模型会话。

        Returns:
            大模型会话接口实例
        """

    @abstractmethod
    def get_provider_name(self) -> str:
        """获取提供商名称。

        Returns:
            提供商名称
        """


class OpenAISession(LLMSessionInterface):
    """OpenAI大模型会话实现。"""

    def __init__(self, config: LLMSettings):
        """初始化OpenAI会话。

        Args:
            config: LLM配置
        """
        self.config = config
        self.client = None
        self._initialized = False

    async def initialize(self) -> None:
        """初始化会话。"""
        if self._initialized:
            return

        try:
            from openai import AsyncOpenAI

            self.client = AsyncOpenAI(api_key=self.config.api_key)
            self._initialized = True
            logger.info("OpenAI会话已初始化")
        except ImportError:
            raise RuntimeError("需要安装 openai 包: pip install openai")

    async def close(self) -> None:
        """关闭会话。"""
        if self.client:
            await self.client.close()
            self.client = None
            self._initialized = False
            logger.info("OpenAI会话已关闭")

    async def chat(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """与OpenAI模型进行对话。

        Args:
            messages: 消息列表
            tools: 可用工具列表

        Returns:
            模型响应

        Raises:
            RuntimeError: 会话未初始化时抛出
        """
        if not self._initialized or not self.client:
            raise RuntimeError("OpenAI会话未初始化")

        try:
            # 构建请求参数
            request_params = {
                "model": self.config.model,
                "messages": messages,
                "temperature": self.config.temperature,
                "max_tokens": self.config.max_tokens,
            }

            # 如果有工具，添加工具参数
            if tools:
                request_params["tools"] = tools
                request_params["tool_choice"] = "auto"

            # 调用OpenAI API
            response = await self.client.chat.completions.create(**request_params)

            # 提取响应内容
            message = response.choices[0].message
            result = {
                "content": message.content or "",
            }

            # 处理工具调用
            if message.tool_calls:
                result["tool_calls"] = []
                for tool_call in message.tool_calls:
                    result["tool_calls"].append(
                        {
                            "type": "function",
                            "function": {
                                "name": tool_call.function.name,
                                "arguments": tool_call.function.arguments,
                            },
                        }
                    )

            logger.debug(
                f"OpenAI响应: {len(result['content'])} 字符，{len(result.get('tool_calls', []))} 个工具调用"
            )
            return result

        except Exception as e:
            logger.error(f"OpenAI调用失败: {e}")
            raise

    async def chat_stream(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
    ) -> AsyncIterator[dict[str, Any]]:
        """与OpenAI模型进行流式对话。

        Args:
            messages: 消息列表
            tools: 可用工具列表

        Yields:
            模型响应片段

        Raises:
            RuntimeError: 会话未初始化时抛出
        """
        if not self._initialized or not self.client:
            raise RuntimeError("OpenAI会话未初始化")

        try:
            # 构建请求参数
            request_params = {
                "model": self.config.model,
                "messages": messages,
                "temperature": self.config.temperature,
                "max_tokens": self.config.max_tokens,
                "stream": True,  # 启用流式响应
            }

            # 如果有工具，添加工具参数
            if tools:
                request_params["tools"] = tools
                request_params["tool_choice"] = "auto"

            # 调用OpenAI API
            stream = await self.client.chat.completions.create(**request_params)

            # 处理流式响应
            accumulated_content = ""
            accumulated_tool_calls = []

            async for chunk in stream:
                delta = chunk.choices[0].delta

                # 处理内容片段
                if delta.content:
                    accumulated_content += delta.content
                    yield {"type": "content", "content": delta.content}

                # 处理工具调用
                if delta.tool_calls:
                    for tool_call in delta.tool_calls:
                        # OpenAI 流式工具调用需要累积
                        if tool_call.index < len(accumulated_tool_calls):
                            # 更新现有工具调用
                            existing = accumulated_tool_calls[tool_call.index]
                            if tool_call.function.name:
                                existing["function"]["name"] = tool_call.function.name
                            if tool_call.function.arguments:
                                existing["function"]["arguments"] += (
                                    tool_call.function.arguments
                                )
                        else:
                            # 新的工具调用
                            accumulated_tool_calls.append(
                                {
                                    "type": "function",
                                    "function": {
                                        "name": tool_call.function.name or "",
                                        "arguments": tool_call.function.arguments or "",
                                    },
                                }
                            )

                # 检查是否完成
                if (
                    chunk.choices[0].finish_reason == "tool_calls"
                    and accumulated_tool_calls
                ):
                    # 解析完整的工具调用参数
                    parsed_tool_calls = []
                    for tc in accumulated_tool_calls:
                        try:
                            parsed_tool_calls.append(
                                {
                                    "type": "function",
                                    "function": {
                                        "name": tc["function"]["name"],
                                        "arguments": tc["function"]["arguments"],
                                    },
                                }
                            )
                        except Exception as e:
                            logger.error(f"解析工具调用参数失败: {e}")
                            yield {"type": "error", "error": f"工具调用解析失败: {e}"}

                    if parsed_tool_calls:
                        yield {"type": "tool_calls", "tool_calls": parsed_tool_calls}

            logger.debug(f"OpenAI流式响应完成: {len(accumulated_content)} 字符")

        except Exception as e:
            logger.error(f"OpenAI流式调用失败: {e}")
            yield {"type": "error", "error": str(e)}


class AnthropicSession(LLMSessionInterface):
    """Anthropic大模型会话实现。"""

    def __init__(self, config: LLMSettings):
        """初始化Anthropic会话。

        Args:
            config: LLM配置
        """
        self.config = config
        self.client = None
        self._initialized = False

    async def initialize(self) -> None:
        """初始化会话。"""
        if self._initialized:
            return

        try:
            from anthropic import AsyncAnthropic

            self.client = AsyncAnthropic(api_key=self.config.api_key)
            self._initialized = True
            logger.info("Anthropic会话已初始化")
        except ImportError:
            raise RuntimeError("需要安装 anthropic 包: pip install anthropic")

    async def close(self) -> None:
        """关闭会话。"""
        if self.client:
            # Anthropic 客户端不需要显式关闭
            self.client = None
            self._initialized = False
            logger.info("Anthropic会话已关闭")

    async def chat(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """与Anthropic模型进行对话。

        Args:
            messages: 消息列表
            tools: 可用工具列表

        Returns:
            模型响应

        Raises:
            RuntimeError: 会话未初始化时抛出
        """
        if not self._initialized or not self.client:
            raise RuntimeError("Anthropic会话未初始化")

        try:
            # 分离系统消息和其他消息
            system_message = ""
            chat_messages = []

            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    chat_messages.append(msg)

            # 构建请求参数
            request_params = {
                "model": self.config.model,
                "messages": chat_messages,
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature,
            }

            if system_message:
                request_params["system"] = system_message

            # 如果有工具，添加工具参数
            if tools:
                # 转换工具格式为Anthropic格式
                anthropic_tools = []
                for tool in tools:
                    if tool.get("type") == "function":
                        func = tool["function"]
                        anthropic_tools.append(
                            {
                                "name": func["name"],
                                "description": func["description"],
                                "input_schema": func["parameters"],
                            }
                        )

                request_params["tools"] = anthropic_tools

            # 调用Anthropic API
            response = await self.client.messages.create(**request_params)

            # 提取响应内容
            result: dict[str, Any] = {
                "content": "",
            }

            # 处理响应内容块
            for content_block in response.content:
                if content_block.type == "text":
                    result["content"] += content_block.text
                elif content_block.type == "tool_use":
                    if "tool_calls" not in result:
                        result["tool_calls"] = []
                    result["tool_calls"].append(
                        {
                            "type": "function",
                            "function": {
                                "name": content_block.name,
                                "arguments": content_block.input,
                            },
                        }
                    )

            logger.debug(
                f"Anthropic响应: {len(result['content'])} 字符，{len(result.get('tool_calls', []))} 个工具调用"
            )
            return result

        except Exception as e:
            logger.error(f"Anthropic调用失败: {e}")
            raise

    async def chat_stream(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
    ) -> AsyncIterator[dict[str, Any]]:
        """与Anthropic模型进行流式对话。

        Args:
            messages: 消息列表
            tools: 可用工具列表

        Yields:
            模型响应片段

        Raises:
            RuntimeError: 会话未初始化时抛出
        """
        if not self._initialized or not self.client:
            raise RuntimeError("Anthropic会话未初始化")

        try:
            # 分离系统消息和其他消息
            system_message = ""
            chat_messages = []

            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    chat_messages.append(msg)

            # 构建请求参数
            request_params = {
                "model": self.config.model,
                "messages": chat_messages,
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature,
                "stream": True,  # 启用流式响应
            }

            if system_message:
                request_params["system"] = system_message

            # 如果有工具，添加工具参数
            if tools:
                # 转换工具格式为Anthropic格式
                anthropic_tools = []
                for tool in tools:
                    if tool.get("type") == "function":
                        func = tool["function"]
                        anthropic_tools.append(
                            {
                                "name": func["name"],
                                "description": func["description"],
                                "input_schema": func["parameters"],
                            }
                        )

                request_params["tools"] = anthropic_tools

            # 调用Anthropic API
            accumulated_content = ""

            async with self.client.messages.stream(**request_params) as stream:
                async for event in stream:
                    # 处理不同类型的事件
                    if event.type == "content_block_start":
                        # 内容块开始
                        if event.content_block.type == "text":
                            # 文本内容块开始
                            pass
                        elif event.content_block.type == "tool_use":
                            # 工具使用块开始
                            pass

                    elif event.type == "content_block_delta":
                        # 内容块增量更新
                        if event.delta.type == "text_delta":
                            # 文本增量
                            accumulated_content += event.delta.text
                            yield {"type": "content", "content": event.delta.text}
                        elif event.delta.type == "input_json_delta":
                            # 工具输入增量（JSON）
                            pass

                    elif event.type == "content_block_stop":
                        # 内容块结束
                        if (
                            hasattr(event, "content_block")
                            and event.content_block.type == "tool_use"
                        ):
                            # 工具调用完成
                            yield {
                                "type": "tool_calls",
                                "tool_calls": [
                                    {
                                        "type": "function",
                                        "function": {
                                            "name": event.content_block.name,
                                            "arguments": json.dumps(
                                                event.content_block.input
                                            )
                                            if isinstance(
                                                event.content_block.input, dict
                                            )
                                            else event.content_block.input,
                                        },
                                    }
                                ],
                            }

                    elif event.type == "message_stop":
                        # 消息结束
                        logger.debug(
                            f"Anthropic流式响应完成: {len(accumulated_content)} 字符"
                        )

        except Exception as e:
            logger.error(f"Anthropic流式调用失败: {e}")
            yield {"type": "error", "error": str(e)}


class OllamaSession(LLMSessionInterface):
    """Ollama大模型会话实现。"""

    def __init__(self, config: LLMSettings):
        """初始化Ollama会话。

        Args:
            config: LLM配置
        """
        self.config = config
        self.client = None
        self._initialized = False
        # Ollama默认配置
        self.base_url = getattr(config, "base_url", "http://localhost:11434")

    async def initialize(self) -> None:
        """初始化会话。"""
        if self._initialized:
            return

        try:
            # 使用 requests 进行 HTTP 请求，Ollama 提供 REST API
            import requests

            # 测试连接
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                self._initialized = True
                logger.info("Ollama会话已初始化")
            else:
                raise RuntimeError(f"无法连接到Ollama服务: {response.status_code}")
        except ImportError:
            raise RuntimeError("需要安装 requests 包: pip install requests")
        except Exception as e:
            raise RuntimeError(f"初始化Ollama会话失败: {e}")

    async def close(self) -> None:
        """关闭会话。"""
        if self._initialized:
            self._initialized = False
            logger.info("Ollama会话已关闭")

    async def chat(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """与Ollama模型进行对话。

        Args:
            messages: 消息列表
            tools: 可用工具列表

        Returns:
            模型响应

        Raises:
            RuntimeError: 会话未初始化时抛出
        """
        if not self._initialized:
            raise RuntimeError("Ollama会话未初始化")

        try:
            import requests

            # 准备请求数据
            request_data = {
                "model": self.config.model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": self.config.temperature,
                    "num_predict": self.config.max_tokens,
                },
            }

            # 如果有工具，添加工具参数（Ollama支持工具调用）
            if tools:
                request_data["tools"] = tools

            # 调用Ollama API
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=request_data,
                timeout=300,  # 5分钟超时
            )
            response.raise_for_status()

            # 解析响应
            result_data = response.json()
            message = result_data.get("message", {})

            result = {
                "content": message.get("content", ""),
            }

            # 处理工具调用
            if "tool_calls" in message and message["tool_calls"]:
                result["tool_calls"] = []
                for tool_call in message["tool_calls"]:
                    result["tool_calls"].append(
                        {
                            "type": "function",
                            "function": {
                                "name": tool_call.get("function", {}).get("name", ""),
                                "arguments": tool_call.get("function", {}).get(
                                    "arguments", "{}"
                                ),
                            },
                        }
                    )

            logger.debug(
                f"Ollama响应: {len(result['content'])} 字符，{len(result.get('tool_calls', []))} 个工具调用"
            )
            return result

        except Exception as e:
            logger.error(f"Ollama调用失败: {e}")
            raise

    async def chat_stream(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
    ) -> AsyncIterator[dict[str, Any]]:
        """与Ollama模型进行流式对话。

        Args:
            messages: 消息列表
            tools: 可用工具列表

        Yields:
            模型响应片段

        Raises:
            RuntimeError: 会话未初始化时抛出
        """
        if not self._initialized:
            raise RuntimeError("Ollama会话未初始化")

        try:
            import requests

            # 准备请求数据
            request_data = {
                "model": self.config.model,
                "messages": messages,
                "stream": True,
                "options": {
                    "temperature": self.config.temperature,
                    "num_predict": self.config.max_tokens,
                },
            }

            # 如果有工具，添加工具参数
            if tools:
                request_data["tools"] = tools

            # 调用Ollama流式API
            response = requests.post(
                f"{self.base_url}/api/chat", json=request_data, stream=True, timeout=300
            )
            response.raise_for_status()

            # 处理流式响应
            accumulated_content = ""
            accumulated_tool_calls = []

            for line in response.iter_lines():
                if line:
                    try:
                        chunk_data = json.loads(line.decode("utf-8"))

                        # 检查是否出错
                        if "error" in chunk_data:
                            yield {"type": "error", "error": chunk_data["error"]}
                            continue

                        message = chunk_data.get("message", {})

                        # 处理内容片段
                        if "content" in message and message["content"]:
                            content = message["content"]
                            accumulated_content += content
                            yield {"type": "content", "content": content}

                        # 处理工具调用
                        if "tool_calls" in message and message["tool_calls"]:
                            for tool_call in message["tool_calls"]:
                                accumulated_tool_calls.append(
                                    {
                                        "type": "function",
                                        "function": {
                                            "name": tool_call.get("function", {}).get(
                                                "name", ""
                                            ),
                                            "arguments": tool_call.get(
                                                "function", {}
                                            ).get("arguments", "{}"),
                                        },
                                    }
                                )

                        # 检查是否完成
                        if chunk_data.get("done", False):
                            # 如果有工具调用，发送它们
                            if accumulated_tool_calls:
                                yield {
                                    "type": "tool_calls",
                                    "tool_calls": accumulated_tool_calls,
                                }
                            break

                    except json.JSONDecodeError as e:
                        logger.warning(f"解析Ollama流式响应失败: {e}")
                        continue

            logger.debug(f"Ollama流式响应完成: {len(accumulated_content)} 字符")

        except Exception as e:
            logger.error(f"Ollama流式调用失败: {e}")
            yield {"type": "error", "error": str(e)}


class OpenAIProvider(ModelProvider):
    """OpenAI模型提供商。"""

    def __init__(self, config: LLMSettings):
        """初始化OpenAI提供商。

        Args:
            config: LLM配置
        """
        self.config = config

    async def create_session(self) -> LLMSessionInterface:
        """创建OpenAI会话。"""
        return OpenAISession(self.config)

    def get_provider_name(self) -> str:
        """获取提供商名称。"""
        return "openai"


class AnthropicProvider(ModelProvider):
    """Anthropic模型提供商。"""

    def __init__(self, config: LLMSettings):
        """初始化Anthropic提供商。

        Args:
            config: LLM配置
        """
        self.config = config

    async def create_session(self) -> LLMSessionInterface:
        """创建Anthropic会话。"""
        return AnthropicSession(self.config)

    def get_provider_name(self) -> str:
        """获取提供商名称。"""
        return "anthropic"


class OllamaProvider(ModelProvider):
    """Ollama模型提供商。"""

    def __init__(self, config: LLMSettings):
        """初始化Ollama提供商。

        Args:
            config: LLM配置
        """
        self.config = config

    async def create_session(self) -> LLMSessionInterface:
        """创建Ollama会话。"""
        return OllamaSession(self.config)

    def get_provider_name(self) -> str:
        """获取提供商名称。"""
        return "ollama"


class ModelProviderFactory:
    """模型提供商工厂类。"""

    _providers = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "ollama": OllamaProvider,
    }

    @classmethod
    def create_provider(cls, config: LLMSettings) -> ModelProvider:
        """根据配置创建模型提供商。

        Args:
            config: LLM配置

        Returns:
            模型提供商实例

        Raises:
            ValueError: 不支持的提供商类型时抛出
        """
        provider_class = cls._providers.get(config.provider.lower())
        if not provider_class:
            supported = ", ".join(cls._providers.keys())
            raise ValueError(
                f"不支持的模型提供商: {config.provider}，支持的类型: {supported}"
            )

        return provider_class(config)

    @classmethod
    def register_provider(cls, name: str, provider_class: type[ModelProvider]) -> None:
        """注册自定义模型提供商。

        Args:
            name: 提供商名称
            provider_class: 提供商类
        """
        cls._providers[name.lower()] = provider_class
        logger.info(f"注册自定义模型提供商: {name}")

    @classmethod
    def get_supported_providers(cls) -> list[str]:
        """获取支持的提供商列表。

        Returns:
            提供商名称列表
        """
        return list(cls._providers.keys())
