"""LLM 提供商实现，使用官方 SDK。"""

import json
from abc import ABC, abstractmethod
from typing import Any

from anthropic import AsyncAnthropic

# 官方 SDK 导入
from openai import AsyncOpenAI
from pydantic import BaseModel, Field


class ToolCall(BaseModel):
    """表示从 LLM 响应中提取的工具调用。"""

    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    id: str | None = None


class LLMResponse(BaseModel):
    """LLM 响应，包括内容和工具调用。"""

    content: str
    tool_calls: list[ToolCall] = Field(default_factory=list)
    raw_response: Any = None

    def has_tool_calls(self) -> bool:
        """检查响应是否包含工具调用。"""
        return len(self.tool_calls) > 0


class LLMProvider(ABC):
    """LLM 提供商的抽象基类。"""

    def __init__(self, api_key: str, model: str, **kwargs) -> None:
        self.api_key = api_key
        self.model = model
        self.temperature = kwargs.get("temperature", 0.7)
        self.max_tokens = kwargs.get("max_tokens", 2048)

    @abstractmethod
    async def generate(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
    ) -> LLMResponse:
        """从 LLM 生成响应。"""


class OpenAIProvider(LLMProvider):
    """OpenAI LLM 提供商实现。"""

    def __init__(self, api_key: str, model: str = "gpt-4", **kwargs) -> None:
        super().__init__(api_key, model, **kwargs)
        self.client = AsyncOpenAI(api_key=api_key)

    async def generate(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
    ) -> LLMResponse:
        """使用 OpenAI API 生成响应。"""
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }

        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        response = await self.client.chat.completions.create(**kwargs)

        message = response.choices[0].message
        content = message.content or ""
        tool_calls = []

        if hasattr(message, "tool_calls") and message.tool_calls:
            for tc in message.tool_calls:
                tool_calls.append(
                    ToolCall(
                        name=tc.function.name,
                        arguments=json.loads(tc.function.arguments)
                        if tc.function.arguments
                        else {},
                        id=tc.id,
                    ),
                )

        return LLMResponse(
            content=content,
            tool_calls=tool_calls,
            raw_response=response,
        )


class AnthropicProvider(LLMProvider):
    """Anthropic Claude LLM 提供商实现。"""

    def __init__(
        self, api_key: str, model: str = "claude-3-opus-20240229", **kwargs
    ) -> None:
        super().__init__(api_key, model, **kwargs)
        self.client = AsyncAnthropic(api_key=api_key)

    def _convert_tools_to_anthropic_format(
        self,
        tools: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """将 OpenAI 工具格式转换为 Anthropic 格式。"""
        anthropic_tools = []
        for tool in tools:
            anthropic_tool = {
                "name": tool["function"]["name"],
                "description": tool["function"].get("description", ""),
                "input_schema": tool["function"].get("parameters", {}),
            }
            anthropic_tools.append(anthropic_tool)
        return anthropic_tools

    async def generate(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
    ) -> LLMResponse:
        """使用 Anthropic API 生成响应。"""
        # 转换消息格式
        system_message = None
        user_messages = []

        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                user_messages.append(msg)

        kwargs = {
            "model": self.model,
            "messages": user_messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }

        if system_message:
            kwargs["system"] = system_message

        if tools:
            kwargs["tools"] = self._convert_tools_to_anthropic_format(tools)

        response = await self.client.messages.create(**kwargs)

        content = ""
        tool_calls = []

        for block in response.content:
            if block.type == "text":
                content += block.text
            elif block.type == "tool_use":
                tool_calls.append(
                    ToolCall(name=block.name, arguments=block.input, id=block.id),
                )

        return LLMResponse(
            content=content,
            tool_calls=tool_calls,
            raw_response=response,
        )


def create_llm_provider(
    provider_type: str,
    api_key: str,
    model: str,
    **kwargs,
) -> LLMProvider:
    """创建 LLM 提供商的工厂函数。"""
    providers = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
    }

    if provider_type not in providers:
        raise ValueError(
            f"未知的提供商: {provider_type}。可用的有: {list(providers.keys())}",
        )

    return providers[provider_type](api_key, model, **kwargs)
