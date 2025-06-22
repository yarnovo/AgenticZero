from typing import Any

from pydantic import BaseModel, Field


class MCPServerConfig(BaseModel):
    """单个 MCP 服务器的配置。"""

    name: str
    command: str
    args: list[str] = Field(default_factory=list)
    env: dict[str, str] = Field(default_factory=dict)

    class Config:
        extra = "allow"


class LLMConfig(BaseModel):
    """LLM 提供商配置。"""

    provider: str = "openai"  # openai, anthropic 等
    api_key: str
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 2048

    class Config:
        extra = "allow"


class AgentConfig(BaseModel):
    """最小化智能体配置。"""

    name: str = "minimal_agent"
    instruction: str = "你是一个可以访问 MCP 工具的有用助手。"
    mcp_servers: dict[str, MCPServerConfig] = Field(default_factory=dict)
    llm_config: LLMConfig
    max_iterations: int = 10
    debug: bool = False

    class Config:
        extra = "allow"

    @classmethod
    def from_dict(cls, config_dict: dict[str, Any]) -> "AgentConfig":
        """从字典创建配置。"""
        return cls(**config_dict)

    def add_mcp_server(
        self,
        name: str,
        command: str,
        args: list[str] | None = None,
    ) -> None:
        """添加 MCP 服务器配置。"""
        self.mcp_servers[name] = MCPServerConfig(
            name=name,
            command=command,
            args=args or [],
        )
