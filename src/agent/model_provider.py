"""模型提供商模块，提供与不同大模型提供商的集成。"""

import logging
from abc import ABC, abstractmethod
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


class ModelProviderFactory:
    """模型提供商工厂类。"""

    _providers = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
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
