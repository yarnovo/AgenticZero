# MCP (Model Context Protocol) 服务模块

## 模块简介

MCP 模块是 AgenticZero 项目的核心服务组件，负责为 Agent 提供统一的服务管理和协议封装能力。本模块基于 Model Context Protocol (MCP) 标准，为各种内部服务提供标准化的接口和交互协议。

## 模块职责

- **为 Agent 提供内置 MCP 服务**：作为 Agent 的核心组件，提供服务发现、服务创建、服务调用等功能
- **解决 MCP 服务自驱性问题**：通过服务管理器实现服务的动态创建和管理，让 Agent 能够自主扩展其能力
- **统一服务接口**：将不同类型的内部服务（Python 执行、图管理等）统一封装为 MCP 协议
- **服务生命周期管理**：提供服务的完整生命周期管理，包括创建、配置、监控、销毁等

## 功能特性

### 核心特性
- **统一服务管理**：提供服务池管理，支持服务的创建、删除、查询等操作
- **动态服务扩展**：支持在运行时动态创建和配置新的服务实例
- **标准 MCP 协议**：遵循 MCP 标准，确保与其他 MCP 兼容组件的互操作性
- **内置集成**：自动集成到 Agent 中作为内置服务，无需额外配置

### 服务类型
- **Python 代码执行服务**：支持 Python 文件管理和沙盒代码执行
- **图管理服务**：封装 GraphManager，提供图的完整生命周期管理
- **服务管理器**：核心管理组件，负责所有服务实例的协调和管理

### 架构优势
- **模块化设计**：每个服务类型独立封装，易于扩展和维护
- **安全隔离**：服务实例之间相互隔离，确保安全性
- **配置灵活**：支持丰富的配置选项，满足不同使用场景
- **性能优化**：支持服务复用和资源管理，提供良好的性能表现

## 安装与配置

### 自动集成

MCP 模块已自动集成到 AgenticZero 项目中，无需单独安装。当创建 Agent 实例时，系统会自动加载以下内置服务：

1. **memory** - 记忆管理服务
2. **mcp_service_manager** - MCP 服务管理器

### 依赖要求

MCP 模块依赖以下组件：
- Python 3.8+
- AgenticZero Graph 模块
- 标准 Python 库（ast, json, pathlib 等）

### 配置选项

服务创建时可通过 `config` 参数进行配置：

**Python 服务配置：**
```python
{
    "base_dir": "python_scripts",  # Python 文件存储目录
    "timeout": 30,                 # 代码执行超时时间（秒）
    "memory_limit": "100MB"        # 内存限制
}
```

**Graph 服务配置：**
```python
{
    "base_path": "graphs",         # 图文件存储路径
    "auto_save": True,             # 是否自动保存
    "validation": True             # 是否启用图验证
}
```

## 快速开始

### 基本使用流程

1. **创建 Agent 实例**：Agent 会自动加载 MCP 服务
2. **列出可用服务**：使用 `service_list` 查看服务类型
3. **创建服务实例**：使用 `service_create` 创建具体服务
4. **调用服务功能**：使用 `service_call` 执行具体任务

## 使用示例

### 1. 通过 Agent 使用 MCP 服务（推荐方式）

```python
from src.agent import Agent
from src.agent.settings import AgentSettings

# 创建配置
config = AgentSettings(
    name="my_agent",
    instruction="你是一个智能助手",
    llm_settings={
        "provider": "openai",
        "model": "gpt-4"
    }
)

# 创建并初始化 Agent
async with Agent(config).connect() as agent:
    # MCP 服务已自动加载，可以直接使用
    
    # 列出所有服务
    response = await agent.run("使用 service_list 工具列出所有 MCP 服务")
    
    # 创建 Python 服务实例
    response = await agent.run(
        "使用 service_create 工具创建一个 Python MCP 服务，"
        "service_type 为 python，service_id 为 my_python_service"
    )
    
    # 使用 Python 服务执行代码
    response = await agent.run(
        "使用 service_call 工具调用 my_python_service 服务的 python_execute 工具，"
        "执行代码 print('Hello from Python!')"
    )
```

### 2. 直接使用 MCP 服务（不通过 Agent）

```python
from src.mcp import MCPServiceManager
from src.graph import GraphManager

# 创建服务管理器
graph_manager = GraphManager()
mcp_manager = MCPServiceManager(graph_manager=graph_manager)

# 初始化
await mcp_manager.handle_initialize({})

# 列出可用工具
tools = await mcp_manager.handle_list_tools()

# 创建 Python 服务
result = await mcp_manager.handle_call_tool("service_create", {
    "service_type": "python",
    "service_id": "py_service",
    "config": {"base_dir": "my_scripts"}
})

# 创建 Graph 服务
result = await mcp_manager.handle_call_tool("service_create", {
    "service_type": "graph",
    "service_id": "graph_service"
})
```

## API 接口说明

### MCP 服务管理器 API

MCP 服务管理器提供统一的服务管理接口：

| 工具名称 | 功能描述 | 参数 |
|---------|---------|------|
| `service_list` | 列出所有服务类型和实例 | `show_instances`: 是否显示实例（默认 true） |
| `service_create` | 创建服务实例 | `service_type`: 服务类型<br>`service_id`: 服务ID<br>`config`: 配置参数（可选） |
| `service_delete` | 删除服务实例 | `service_id`: 服务ID |
| `service_info` | 获取服务信息 | `service_id`: 服务ID |
| `service_call` | 调用服务工具 | `service_id`: 服务ID<br>`tool_name`: 工具名称<br>`arguments`: 工具参数 |
| `service_list_tools` | 列出服务的所有工具 | `service_id`: 服务ID |

### 标准 MCP 协议

每个服务都实现标准的 MCP 协议接口：

- `handle_initialize()` - 初始化服务
- `handle_list_tools()` - 列出可用工具
- `handle_call_tool()` - 执行工具调用

## 服务类型详解

### 1. Python MCP 服务

管理和执行 Python 代码的服务。

**主要功能：**
- 文件管理：创建、读取、更新、删除 Python 文件
- 代码执行：在安全沙盒中执行 Python 代码
- 沙盒管理：创建持久沙盒环境，管理执行状态

**工具列表：**
- `python_create` - 创建 Python 文件
- `python_read` - 读取 Python 文件
- `python_update` - 更新 Python 文件
- `python_delete` - 删除 Python 文件
- `python_list` - 列出所有 Python 文件
- `python_search` - 搜索 Python 文件
- `python_execute` - 执行 Python 代码
- `python_execute_file` - 执行 Python 文件
- `python_sandbox_create` - 创建沙盒环境
- `python_sandbox_delete` - 删除沙盒环境
- `python_sandbox_status` - 获取沙盒状态
- `python_sandbox_list` - 列出所有沙盒

### 2. Graph MCP 服务

封装 GraphManager 的图管理服务。

**主要功能：**
- 图生命周期管理：创建、加载、保存、删除图
- 图结构操作：添加/删除节点和边
- 图执行：运行图并获取结果

**工具列表：**
- `graph_create` - 创建新图
- `graph_load` - 加载图
- `graph_save` - 保存图
- `graph_delete` - 删除图
- `graph_list` - 列出所有图
- `graph_info` - 获取图信息
- `graph_run` - 执行图
- `graph_node_add` - 添加节点
- `graph_node_remove` - 移除节点
- `graph_edge_add` - 添加边
- `graph_edge_remove` - 移除边
- `graph_validate` - 验证图结构

## 高级用法

### 创建多个服务实例

```python
# 创建多个 Python 服务实例，用于不同项目
await agent.run(
    "创建三个 Python 服务：project_a、project_b 和 project_c，"
    "分别使用不同的 base_dir 配置"
)

# 在特定服务中创建文件
await agent.run(
    "在 project_a 服务中创建一个名为 utils 的 Python 文件，"
    "包含一些通用工具函数"
)
```

### 组合使用 Python 和 Graph 服务

```python
# 创建一个图来协调 Python 代码执行
await agent.run(
    "创建一个名为 data_pipeline 的图，"
    "包含多个节点来执行数据处理任务"
)

# 在 Python 服务中准备处理脚本
await agent.run(
    "创建一个 process_data.py 文件，"
    "实现数据清洗和转换功能"
)

# 将 Python 脚本集成到图中
await agent.run(
    "在 data_pipeline 图中添加一个节点，"
    "调用 process_data.py 进行数据处理"
)
```

### 使用持久沙盒

```python
# 创建持久沙盒用于交互式开发
await agent.run(
    "创建一个名为 dev_sandbox 的 Python 沙盒环境"
)

# 在沙盒中定义变量和函数
await agent.run(
    "在 dev_sandbox 沙盒中执行代码："
    "def greet(name): return f'Hello, {name}!'"
)

# 使用之前定义的函数
await agent.run(
    "在 dev_sandbox 沙盒中执行代码："
    "print(greet('World'))"
)

# 查看沙盒状态
await agent.run(
    "获取 dev_sandbox 沙盒的状态信息"
)
```

## 安全性

### Python 代码执行安全

- **沙盒隔离**：所有代码在受限环境中执行
- **资源限制**：可配置 CPU、内存和执行时间限制
- **白名单机制**：仅允许安全的内置函数
- **进程隔离**：支持在独立进程中执行代码

### 访问控制

- 服务实例相互隔离
- 文件访问受限于配置的目录
- 不允许系统级操作

## 扩展开发

### 添加新的 MCP 服务类型

要扩展 MCP 模块并添加新的服务类型，请遵循以下步骤：

#### 1. 创建服务目录结构
```
src/mcp/
├── my_service/
│   ├── __init__.py
│   ├── my_mcp_server.py      # 主服务器类
│   ├── my_manager.py         # 业务逻辑管理器（可选）
│   └── tests/
│       └── test_my_service.py
```

#### 2. 实现 MCP 服务器类

```python
# my_service/my_mcp_server.py
from typing import Any, Dict, List

class MyMCPServer:
    """自定义 MCP 服务器实现"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """初始化服务器
        
        Args:
            config: 服务配置参数
        """
        self.config = config or {}
        self.initialized = False
    
    async def handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """初始化服务"""
        self.initialized = True
        return {
            "capabilities": {
                "tools": {"available": True}
            },
            "serverInfo": {
                "name": "my_custom_service",
                "version": "1.0.0"
            }
        }
    
    async def handle_list_tools(self) -> List[Dict[str, Any]]:
        """列出可用工具"""
        return [
            {
                "name": "my_tool",
                "description": "执行自定义任务",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "param1": {"type": "string", "description": "参数1"},
                        "param2": {"type": "integer", "description": "参数2"}
                    },
                    "required": ["param1"]
                }
            }
        ]
    
    async def handle_call_tool(self, name: str, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """执行工具调用"""
        if name == "my_tool":
            param1 = arguments.get("param1")
            param2 = arguments.get("param2", 0)
            
            # 执行业务逻辑
            result = f"处理参数: {param1}, {param2}"
            
            return [{"type": "text", "text": result}]
        
        raise ValueError(f"未知工具: {name}")
```

#### 3. 注册服务类型

在 `src/mcp/mcp_service_manager.py` 中注册新服务：

```python
# 导入新服务
from .my_service.my_mcp_server import MyMCPServer

class MCPServiceManager:
    def __init__(self, ...):
        # 注册服务类型
        self.service_types = {
            "python": {"class": PythonMCPServer, "description": "Python 代码管理和执行服务"},
            "graph": {"class": GraphMCPServer, "description": "图管理和执行服务"},
            "my_service": {"class": MyMCPServer, "description": "我的自定义服务"},  # 新增
        }
```

#### 4. 编写测试

```python
# my_service/tests/test_my_service.py
import pytest
from ..my_mcp_server import MyMCPServer

@pytest.mark.unit
@pytest.mark.asyncio
async def test_my_service_initialize():
    """测试服务初始化"""
    server = MyMCPServer()
    result = await server.handle_initialize({})
    
    assert result["serverInfo"]["name"] == "my_custom_service"
    assert result["capabilities"]["tools"]["available"] is True

@pytest.mark.unit
@pytest.mark.asyncio
async def test_my_service_tools():
    """测试工具列表"""
    server = MyMCPServer()
    tools = await server.handle_list_tools()
    
    assert len(tools) == 1
    assert tools[0]["name"] == "my_tool"
```

#### 5. 使用新服务

```python
# 创建自定义服务实例
await agent.run(
    "使用 service_create 工具创建自定义服务，"
    "service_type 为 my_service，service_id 为 my_instance"
)

# 调用自定义工具
await agent.run(
    "使用 service_call 工具调用 my_instance 服务的 my_tool 工具，"
    "参数为 param1='test', param2=42"
)
```

## 故障排查

### 常见问题

1. **服务创建失败**
   - 检查服务 ID 是否已存在
   - 确认服务类型正确
   - 验证配置参数

2. **Python 执行错误**
   - 检查代码语法
   - 确认使用的函数在白名单中
   - 查看详细错误信息

3. **图执行失败**
   - 验证图结构
   - 检查节点配置
   - 确认所有依赖节点存在

### 调试技巧

- 使用 `service_info` 查看服务配置
- 使用 `service_list_tools` 了解可用工具
- 查看执行结果中的错误详情
- 检查日志输出获取更多信息

## 性能优化

- **服务复用**：避免频繁创建和删除服务
- **批量操作**：使用单个服务处理多个任务
- **沙盒管理**：合理使用持久沙盒避免重复初始化
- **资源清理**：及时删除不需要的服务和沙盒