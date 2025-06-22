# Agentic 智能体框架

一个功能完整的 Python 框架，用于创建可以与 MCP（模型上下文协议）服务器和大型语言模型交互的 AI 智能体。该框架提供了会话管理、上下文管理和 MCP 提供商等先进功能。

## 特性

### 核心功能
- **双智能体架构**：支持 `MinimalAgent`（简单快速）和 `AgenticAgent`（功能完整）
- **多 LLM 支持**：内置支持 OpenAI 和 Anthropic 模型
- **自动工具调用**：自动检测和执行 LLM 响应中的工具调用
- **MCP 服务器管理**：同时连接多个 MCP 服务器
- **异步支持**：完全异步实现，性能更好

### 高级功能
- **会话管理**：专业的 MCP 会话生命周期管理，支持连接池
- **上下文管理**：持久化对话历史，支持内存和文件存储
- **MCP 提供商**：抽象的 MCP 服务器管理，支持健康检查和错误恢复
- **依赖注入**：灵活的组件替换和自定义实现
- **健康监控**：实时监控智能体和 MCP 服务器状态

## 安装

本项目使用 uv 管理依赖，请在项目根目录运行：

```bash
# 安装所有依赖（包括开发依赖）
make dev-install
# 或直接使用 uv
uv sync

# 仅安装生产依赖
make install
# 或
uv sync --no-dev

# 可选：安装 MCP 服务器
npm install -g @modelcontextprotocol/server-filesystem
pip install mcp-server-fetch
```

项目依赖包括：
- `mcp>=1.0.0` - 官方 MCP SDK
- `openai>=1.0.0` - OpenAI 官方 SDK
- `anthropic>=0.18.0` - Anthropic 官方 SDK
- `pydantic>=2.0.0` - 数据验证和设置管理

## 快速开始

### 使用 MinimalAgent（简单快速）

```python
import asyncio
from agentic import MinimalAgent, AgentConfig, LLMConfig

async def main():
    # 配置智能体
    config = AgentConfig(
        name="my_agent",
        instruction="你是一个可以访问工具的有用助手。",
        llm_config=LLMConfig(
            provider="openai",
            api_key="your-api-key",
            model="gpt-4"
        )
    )
    
    # 添加 MCP 服务器
    config.add_mcp_server(
        name="filesystem",
        command="npx",
        args=["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
    )
    
    # 使用智能体
    async with MinimalAgent(config).connect() as agent:
        response = await agent.run("列出 /tmp 目录中的文件")
        print(response)

asyncio.run(main())
```

### 使用 AgenticAgent（功能完整）

```python
import asyncio
from agentic import AgenticAgent, AgentConfig, LLMConfig

async def main():
    # 配置智能体
    config = AgentConfig(
        name="advanced_agent",
        instruction="你是一个高级智能体助手。",
        llm_config=LLMConfig(
            provider="openai",
            api_key="your-api-key",
            model="gpt-4"
        )
    )
    
    # 使用高级智能体（自动管理会话和上下文）
    async with AgenticAgent(config).connect() as agent:
        # 执行对话
        response = await agent.run("你好，请介绍一下你自己")
        print(response)
        
        # 查看健康状态
        health = await agent.get_health_status()
        print(f"智能体健康状态: {health}")

asyncio.run(main())
```

## 架构

该框架采用模块化设计，由以下核心组件组成：

### 1. 智能体层 (`agent.py`)
- `MinimalAgent`：轻量级智能体，适合简单场景
- `AgenticAgent`：功能完整的智能体，支持高级特性
- 自动工具执行循环和对话管理

### 2. 配置管理 (`config.py`)
- `AgentConfig`：智能体的主要配置类
- `MCPServerConfig`：单个 MCP 服务器的配置
- `LLMConfig`：LLM 提供商的配置

### 3. LLM 提供商 (`llm.py`)
- `LLMProvider`：LLM 提供商的抽象基类
- `OpenAIProvider`：使用官方 OpenAI SDK 的实现
- `AnthropicProvider`：使用官方 Anthropic SDK 的实现
- 自动工具调用检测和解析

### 4. 会话管理 (`session_manager.py`)
- `SessionManagerInterface`：会话管理抽象接口
- `DefaultSessionManager`：默认会话管理器
- `PooledSessionManager`：支持连接池的会话管理器
- `MCPSession`：单个 MCP 会话封装

### 5. 上下文管理 (`context_manager.py`)
- `ContextManagerInterface`：上下文管理抽象接口
- `InMemoryContextManager`：内存存储的上下文管理器
- `PersistentContextManager`：持久化存储的上下文管理器
- `ConversationContext`：对话上下文模型

### 6. MCP 提供商 (`mcp_provider.py`)
- `MCPProviderInterface`：MCP 提供商抽象接口
- `DefaultMCPProvider`：默认 MCP 提供商实现
- `MCPToolInfo`：工具信息封装
- 健康检查和错误处理

### 7. MCP 接口层 (`mcp_interface.py`, `mcp_client.py`)
- `MCPClientInterface`：MCP 客户端的抽象接口
- `DefaultMCPClient`：使用官方 MCP SDK 的客户端实现
- `MCPServerConnection`：封装单个服务器连接

## 使用示例

### 基本用法

```python
from agentic import MinimalAgent, AgentConfig, LLMConfig

config = AgentConfig(
    name="basic_agent",
    llm_config=LLMConfig(
        provider="openai",
        api_key="sk-...",
        model="gpt-4"
    )
)

async with MinimalAgent(config).connect() as agent:
    response = await agent.run("你好，你怎么样？")
    print(response)
```

### 高级智能体使用

```python
from agentic import AgenticAgent, ContextManager

# 使用持久化上下文
context_manager = ContextManager.create_persistent_manager("./conversations.json")

config = AgentConfig(
    name="advanced_agent",
    llm_config=LLMConfig(
        provider="anthropic",
        api_key="sk-ant-...",
        model="claude-3-opus-20240229"
    )
)

agent = AgenticAgent(
    config=config,
    context_manager=context_manager,
    conversation_id="user_123"
)

async with agent.connect() as connected_agent:
    response = await connected_agent.run("记住我喜欢咖啡")
    print(response)
    
    # 稍后在另一个会话中
    response = await connected_agent.run("我喜欢什么饮料？")
    print(response)  # 会记住之前的对话
```

### 使用 MCP 服务器

```python
from agentic import AgenticAgent, AgentConfig, LLMConfig, MCPServerConfig

config = AgentConfig(
    name="tool_agent",
    instruction="你可以访问文件和获取网页内容。",
    llm_config=LLMConfig(
        provider="anthropic",
        api_key="sk-ant-...",
        model="claude-3-opus-20240229"
    ),
    mcp_servers={
        "filesystem": MCPServerConfig(
            name="filesystem",
            command="npx",
            args=["-y", "@modelcontextprotocol/server-filesystem", "/home"]
        ),
        "git": MCPServerConfig(
            name="git",
            command="npx",
            args=["-y", "@modelcontextprotocol/server-git", "--repository", "."]
        ),
        "sqlite": MCPServerConfig(
            name="sqlite",
            command="npx",
            args=["-y", "@modelcontextprotocol/server-sqlite", "--db-path", "/tmp/test.db"]
        )
    }
)

async with AgenticAgent(config).connect() as agent:
    # 智能体会根据需要自动使用工具
    response = await agent.run("请查看当前目录的文件，并检查 Git 状态")
    print(response)
    
    # 查看 MCP 服务器健康状态
    health = await agent.get_health_status()
    print(f"MCP 服务器状态: {health['mcp_provider']}")
```

### 健康监控和错误处理

```python
from agentic import AgenticAgent, MCPProviderFactory, DefaultSessionManager

# 创建自定义组件
session_manager = DefaultSessionManager()
mcp_provider = MCPProviderFactory.create_default_provider(
    session_manager=session_manager,
    auto_reconnect=True
)

agent = AgenticAgent(
    config=config,
    mcp_provider=mcp_provider,
    session_manager=session_manager
)

async with agent.connect() as connected_agent:
    # 定期健康检查
    health = await connected_agent.get_health_status()
    
    if not health['mcp_provider']['healthy']:
        print("警告：部分 MCP 服务器不可用")
        for server, status in health['mcp_provider']['server_status'].items():
            if not status['connected']:
                print(f"服务器 {server} 连接失败")
    
    # 执行任务
    try:
        response = await connected_agent.run("执行一些需要工具的任务")
        print(response)
    except Exception as e:
        print(f"任务执行失败: {e}")
```

### 依赖注入

```python
# 自定义 MCP 客户端
class CustomMCPClient(MCPClientInterface):
    async def list_tools(self) -> List[Dict[str, Any]]:
        # 自定义实现
        pass
    
    async def call_tool(self, tool_name: str, arguments: Optional[Dict[str, Any]] = None):
        # 自定义实现
        pass
    
    async def initialize(self):
        pass
    
    async def close(self):
        pass

# 使用自定义客户端
config = AgentConfig(
    name="custom_agent",
    llm_config={...}
)

custom_client = CustomMCPClient()
agent = MinimalAgent(
    config=config,
    mcp_client=custom_client  # 注入自定义客户端
)
```

### 从字典配置

```python
config_dict = {
    "name": "dict_agent",
    "mcp_servers": {
        "filesystem": {
            "name": "filesystem",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem"]
        }
    },
    "llm_config": {
        "provider": "openai",
        "api_key": "sk-...",
        "model": "gpt-3.5-turbo"
    }
}

agent = MinimalAgent(config_dict)
```

## API 参考

### AgenticAgent

```python
class AgenticAgent:
    def __init__(
        self,
        config: Union[AgentConfig, Dict[str, Any]],
        mcp_provider: Optional[MCPProviderInterface] = None,
        context_manager: Optional[ContextManagerInterface] = None,
        session_manager: Optional[SessionManagerInterface] = None,
        llm_provider: Optional[LLMProvider] = None,
        conversation_id: Optional[str] = None
    )
    async def initialize() -> None
    async def close() -> None
    async def connect()  # 上下文管理器
    async def run(user_input: str, max_iterations: Optional[int] = None) -> str
    async def clear_history(keep_system: bool = True) -> None
    def get_history() -> List[Dict[str, str]]
    async def get_health_status() -> Dict[str, Any]
```

### MinimalAgent

```python
class MinimalAgent:
    def __init__(
        self, 
        config: Union[AgentConfig, Dict[str, Any]],
        mcp_client: Optional[MCPClientInterface] = None,
        llm_provider: Optional[LLMProvider] = None
    )
    async def initialize() -> None
    async def close() -> None
    async def connect()  # 上下文管理器
    async def run(user_input: str, max_iterations: Optional[int] = None) -> str
    def clear_history() -> None
    def get_history() -> List[Dict[str, str]]
```

### 配置类

```python
class AgentConfig:
    name: str = "agent"
    instruction: str = "你是一个有用的助手。"
    mcp_servers: Dict[str, MCPServerConfig] = {}
    llm_config: LLMConfig
    max_iterations: int = 10
    debug: bool = False
    
    def add_mcp_server(name: str, command: str, args: Optional[List[str]] = None)

class LLMConfig:
    provider: str = "openai"  # openai, anthropic
    api_key: str
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 2048

class MCPServerConfig:
    name: str
    command: str
    args: List[str] = []
    env: Dict[str, str] = {}
```

### 管理器接口

```python
class ContextManagerInterface(ABC):
    async def create_context(conversation_id: str, system_instruction: Optional[str] = None) -> ConversationContext
    async def get_context(conversation_id: str) -> Optional[ConversationContext]
    async def update_context(context: ConversationContext) -> None
    async def delete_context(conversation_id: str) -> None
    async def list_contexts() -> List[str]

class SessionManagerInterface(ABC):
    async def create_session(server_name: str, config: MCPServerConfig) -> str
    async def get_session(session_id: str) -> Optional[MCPSession]
    async def close_session(session_id: str) -> None
    async def close_all_sessions() -> None
    def list_sessions() -> Set[str]

class MCPProviderInterface(ABC):
    async def initialize() -> None
    async def shutdown() -> None
    async def add_server(name: str, config: MCPServerConfig) -> None
    async def remove_server(name: str) -> None
    async def list_tools(server_name: Optional[str] = None) -> List[MCPToolInfo]
    async def call_tool(tool_name: str, arguments: Optional[Dict[str, Any]] = None) -> Dict[str, Any]
    async def health_check() -> Dict[str, Any]
```

## 工作原理

1. **用户输入**：用户向智能体提供查询
2. **LLM 处理**：智能体将查询和可用工具发送到配置的 LLM
3. **工具检测**：解析 LLM 响应以查找工具调用
4. **工具执行**：通过适当的 MCP 服务器调用检测到的工具
5. **结果集成**：将工具结果添加到对话中
6. **迭代**：重复步骤 2-5，直到没有更多工具调用或达到最大迭代次数
7. **最终响应**：将最终的 LLM 响应返回给用户

## 开发和测试

本项目使用 Makefile 管理开发任务：

```bash
# 运行所有检查（lint、类型检查、格式检查、测试）
make check

# 运行测试
make test

# 运行 lint 检查
make lint

# 自动修复 lint 问题
make lint-fix

# 类型检查
make type-check

# 格式化代码
make format

# 检查代码格式
make format-check

# 清理缓存文件
make clean
```

## 运行示例

项目提供了丰富的示例代码：

```bash
# 运行基本用法示例
uv run python src/agentic/examples/basic_usage.py

# 运行 MCP 集成示例
uv run python src/agentic/examples/mcp_integration.py

# 运行测试
make test

# 或直接使用 pytest
uv run pytest src/agentic/tests/
```

### 示例文件

- `examples/basic_usage.py` - 基本用法、自定义组件、持久化上下文等
- `examples/mcp_integration.py` - 各种 MCP 服务器集成示例
- `tests/` - 完整的测试套件，包含单元测试和集成测试

## 架构优势

### MinimalAgent vs AgenticAgent

| 特性 | MinimalAgent | AgenticAgent |
|------|-------------|-------------|
| 复杂度 | 简单，轻量级 | 功能完整，模块化 |
| 会话管理 | 基本连接管理 | 专业会话池管理 |
| 上下文管理 | 内存对话历史 | 持久化上下文存储 |
| 健康监控 | 无 | 完整的健康检查 |
| 错误恢复 | 基本错误处理 | 自动重连和恢复 |
| 适用场景 | 简单脚本和原型 | 生产环境和复杂应用 |

### 设计原则

- **模块化**：每个组件都可以独立测试和替换
- **可扩展**：通过接口和工厂模式支持自定义实现
- **异步优先**：充分利用 Python 异步特性
- **类型安全**：使用 Pydantic 进行数据验证
- **错误处理**：完善的异常处理和日志记录

## 测试

项目包含完整的测试套件：

```bash
# 运行所有测试
make test

# 运行特定类型的测试
pytest -m unit  # 单元测试
pytest -m integration  # 集成测试
pytest -m slow  # 慢速测试

# 运行特定文件的测试
pytest src/agentic/tests/test_agentic_agent.py -v
```

测试覆盖：
- 单元测试：所有核心组件的独立测试
- 集成测试：组件间交互测试
- 模拟测试：使用 mock 对象的隔离测试

## 限制和注意事项

- 需要有效的 LLM API 密钥才能正常工作
- MCP 服务器需要单独安装和配置
- 某些 MCP 服务器可能需要特定的运行环境
- 持久化上下文会占用磁盘空间
- 大量并发会话可能影响性能

## 未来计划

### 短期目标
- 支持更多 LLM 提供商（Google Gemini、Cohere 等）
- 增强错误处理和重试机制
- 添加工具调用验证
- 性能优化和内存管理改进

### 长期目标
- 流式响应支持
- 并行工具执行
- 插件系统和自定义工具处理器
- Web 界面和 API 服务器
- 分布式部署支持
- 高级对话管理（多轮对话、上下文切换等）

## 许可证

这是用于演示目的的示例代码。