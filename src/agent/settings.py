from typing import Any

from pydantic import BaseModel, Field


class MCPServerSettings(BaseModel):
    """单个 MCP 服务器的设置。"""

    name: str
    command: str
    args: list[str] = Field(default_factory=list)
    env: dict[str, str] = Field(default_factory=dict)

    class Config:
        extra = "allow"


class LLMSettings(BaseModel):
    """LLM 提供商设置。"""

    provider: str = "openai"  # openai, anthropic, ollama 等
    api_key: str = ""  # Ollama 不需要 API key
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 2048
    base_url: str = ""  # Ollama 服务器地址，如 http://localhost:11434

    class Config:
        extra = "allow"


class AgentSettings(BaseModel):
    """智能体设置。"""

    name: str = "agent"
    instruction: str = "你是一个可以访问 MCP 工具的有用助手。"
    mcp_servers: dict[str, MCPServerSettings] = Field(default_factory=dict)
    llm_settings: LLMSettings
    max_iterations: int = 10
    debug: bool = False

    class Config:
        extra = "allow"

    @classmethod
    def from_dict(cls, settings_dict: dict[str, Any]) -> "AgentSettings":
        """从字典创建设置。"""
        return cls(**settings_dict)

    def add_mcp_server(
        self,
        name: str,
        command: str,
        args: list[str] | None = None,
    ) -> None:
        """添加 MCP 服务器设置。"""
        self.mcp_servers[name] = MCPServerSettings(
            name=name,
            command=command,
            args=args or [],
        )
