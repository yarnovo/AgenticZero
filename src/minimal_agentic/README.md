# 最小化智能体模块

一个轻量级的 Python 模块，用于创建可以与 MCP（模型上下文协议）服务器和大型语言模型交互的 AI 智能体。

## 特性

- **简单配置**：易于使用的 MCP 服务器和 LLM 提供商配置系统
- **多 LLM 支持**：内置支持 OpenAI 和 Anthropic 模型
- **自动工具调用**：自动检测和执行 LLM 响应中的工具调用
- **MCP 服务器管理**：同时连接多个 MCP 服务器
- **对话历史**：跨交互维护对话上下文
- **异步支持**：完全异步实现，性能更好
- **依赖注入**：支持自定义 MCP 客户端和 LLM 提供商

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

```python
import asyncio
from minimal_agentic import MinimalAgent, AgentConfig

async def main():
    # 配置智能体
    config = AgentConfig(
        name="my_agent",
        instruction="你是一个可以访问工具的有用助手。",
        llm_config={
            "provider": "openai",
            "api_key": "your-api-key",
            "model": "gpt-4"
        }
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

## 架构

该模块由五个主要组件组成：

### 1. 配置 (`config.py`)
- `AgentConfig`：智能体的主要配置类
- `MCPServerConfig`：单个 MCP 服务器的配置
- `LLMConfig`：LLM 提供商的配置

### 2. LLM 提供商 (`llm.py`)
- `LLMProvider`：LLM 提供商的抽象基类
- `OpenAIProvider`：使用官方 OpenAI SDK 的实现
- `AnthropicProvider`：使用官方 Anthropic SDK 的实现
- 自动工具调用检测和解析

### 3. MCP 接口 (`mcp_interface.py`)
- `MCPClientInterface`：MCP 客户端的抽象接口
- `MCPClientFactory`：创建 MCP 客户端的工厂协议
- 支持自定义 MCP 客户端实现

### 4. MCP 客户端 (`mcp_client.py`)
- `DefaultMCPClient`：使用官方 MCP SDK 的客户端实现
- `MCPServerConnection`：封装单个服务器连接
- 基于官方 SDK 的标准 MCP 协议支持

### 5. 智能体 (`agent.py`)
- `MinimalAgent`：协调所有组件的主要智能体类
- 自动工具执行循环
- 对话历史管理
- 支持依赖注入

## 使用示例

### 基本用法

```python
config = AgentConfig(
    name="basic_agent",
    llm_config={
        "provider": "openai",
        "api_key": "sk-...",
        "model": "gpt-4"
    }
)

async with MinimalAgent(config).connect() as agent:
    response = await agent.run("你好，你怎么样？")
    print(response)
```

### 使用 MCP 服务器

```python
config = AgentConfig(
    name="tool_agent",
    instruction="你可以访问文件和获取网页内容。",
    llm_config={
        "provider": "anthropic",
        "api_key": "sk-ant-...",
        "model": "claude-3-opus-20240229"
    }
)

# 添加文件系统访问
config.add_mcp_server(
    name="filesystem",
    command="npx",
    args=["-y", "@modelcontextprotocol/server-filesystem", "/home"]
)

# 添加网页抓取功能
config.add_mcp_server(
    name="fetch",
    command="uvx",
    args=["mcp-server-fetch"]
)

agent = MinimalAgent(config)
await agent.initialize()

# 智能体会根据需要自动使用工具
response = await agent.run("README.md 文件中有什么内容？")
print(response)

await agent.close()
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

### MinimalAgent

```python
class MinimalAgent:
    def __init__(
        self, 
        config: Union[AgentConfig, Dict[str, Any]],
        mcp_client: Optional[MCPClientInterface] = None,
        llm_provider: Optional[LLMProvider] = None
    )
    async def initialize()
    async def close()
    async def connect()  # 上下文管理器
    async def run(user_input: str, max_iterations: Optional[int] = None) -> str
    def clear_history()
    def get_history() -> List[Dict[str, str]]
```

### AgentConfig

```python
class AgentConfig:
    name: str
    instruction: str
    mcp_servers: Dict[str, MCPServerConfig]
    llm_config: LLMConfig
    max_iterations: int = 10
    debug: bool = False
    
    def add_mcp_server(name: str, command: str, args: Optional[List[str]] = None)
```

### MCPClientInterface

```python
class MCPClientInterface(ABC):
    async def list_tools() -> List[Dict[str, Any]]
    async def call_tool(tool_name: str, arguments: Optional[Dict[str, Any]] = None) -> Dict[str, Any]
    async def initialize() -> None
    async def close() -> None
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

由于项目使用 uv 管理依赖，请使用以下方式运行代码：

```bash
# 运行示例
uv run python src/minimal_agentic/example.py

# 运行测试
uv run python src/test_official_sdk.py

# 或使用提供的脚本
./run_example.sh
```

## 限制

- 需要有效的 API 密钥才能与 LLM 交互
- MCP 服务器需要单独安装和配置
- 工具调用仅支持官方 SDK 提供的格式

## 未来改进

- 支持更多 LLM 提供商（Google、Cohere 等）
- 高级 MCP 协议功能
- 更好的错误处理和重试逻辑
- 执行前的工具调用验证
- 流式响应支持
- 并行工具执行
- 自定义工具处理器的插件系统

## 许可证

这是用于演示目的的示例代码。