"""Agentic 智能体框架 - 自驱动智能体实现。"""

from .agent import Agent, AgenticAgent, MinimalAgent
from .core_engine import CoreEngine
from .llm_session_manager import LLMSessionInterface, LLMSessionManager
from .mcp_client_factory import MCPClientFactory
from .mcp_session_manager import (
    MCPClientInterface,
    MCPSession,
    MCPSessionManager,
)
from .message_history_manager import (
    FileMessageHistoryManager,
    InMemoryMessageHistoryManager,
    Message,
    MessageHistory,
    MessageHistoryManager,
    MessageHistoryManagerInterface,
)
from .model_provider import (
    AnthropicProvider,
    ModelProvider,
    ModelProviderFactory,
    OpenAIProvider,
)
from .session_context_manager import SessionContext, SessionContextManager
from .settings import AgentSettings, LLMSettings, MCPServerSettings

__all__ = [
    # 核心智能体
    "Agent",
    "AgenticAgent",  # 别名，向后兼容
    "MinimalAgent",  # 别名，向后兼容
    # 配置
    "AgentSettings",
    "LLMSettings",
    "MCPServerSettings",
    # 核心引擎
    "CoreEngine",
    # 大模型会话管理
    "LLMSessionInterface",
    "LLMSessionManager",
    # MCP会话管理
    "MCPClientInterface",
    "MCPClientFactory",
    "MCPSession",
    "MCPSessionManager",
    # 消息历史管理
    "Message",
    "MessageHistory",
    "MessageHistoryManager",
    "MessageHistoryManagerInterface",
    "InMemoryMessageHistoryManager",
    "FileMessageHistoryManager",
    # 会话上下文管理
    "SessionContext",
    "SessionContextManager",
    # 模型提供商
    "ModelProvider",
    "ModelProviderFactory",
    "OpenAIProvider",
    "AnthropicProvider",
]

__version__ = "2.0.0"
