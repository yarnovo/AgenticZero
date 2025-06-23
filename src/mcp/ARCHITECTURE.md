# MCP 模块架构设计

## 概述

MCP (Model Context Protocol) 模块为 AgenticZero 提供统一的服务管理和协议封装。该模块负责管理和暴露各种内部服务作为 MCP 协议服务，供其他组件通过标准 MCP 协议进行调用。

## 架构设计原则

1. **模块化设计**：每种服务类型独立封装，易于扩展
2. **职责分离**：保持各模块职责清晰，不混合业务逻辑
3. **标准化接口**：遵循 MCP 协议规范，提供统一的工具调用接口
4. **安全性**：Python 代码执行采用沙盒机制，确保安全隔离

## 模块结构

```
src/mcp/
├── __init__.py
├── python_mcp/              # Python 文件 MCP 服务
│   ├── __init__.py
│   ├── python_file_manager.py      # Python 文件管理
│   ├── python_memory_manager.py    # Python 内存执行管理（沙盒）
│   └── python_mcp_server.py        # Python MCP 服务器
├── graph_mcp/               # Graph MCP 服务
│   ├── __init__.py
│   └── graph_mcp_server.py         # Graph MCP 服务器（封装 GraphManager）
├── mcp_service_manager.py   # MCP 服务统一管理器
├── ARCHITECTURE.md          # 架构设计文档
└── README.md               # 使用说明文档
```

## 核心组件

### 1. MCP 服务管理器 (mcp_service_manager.py)

最外层的 MCP 服务，负责：
- 管理所有子 MCP 服务的生命周期
- 提供服务注册、查询、创建、删除等功能
- 统一的服务池管理
- 对外暴露 stdio MCP 协议接口

主要工具：
- `service_list`: 列出所有可用的 MCP 服务
- `service_create`: 创建新的 MCP 服务实例
- `service_delete`: 删除 MCP 服务实例
- `service_info`: 获取服务详细信息
- `service_call`: 调用特定服务的工具

### 2. Python MCP 服务 (python_mcp/)

#### 2.1 Python 文件管理器 (python_file_manager.py)
- 管理 Python 文件的创建、读取、修改、删除
- 文件验证和语法检查
- 文件索引和搜索功能

#### 2.2 Python 内存管理器 (python_memory_manager.py)
- 沙盒环境管理
- 代码执行隔离
- 内存状态跟踪
- 执行结果管理

#### 2.3 Python MCP 服务器 (python_mcp_server.py)
- 整合文件和内存管理器
- 提供 Python 代码执行相关的 MCP 工具
- 工具包括：
  - `python_create`: 创建 Python 文件
  - `python_read`: 读取 Python 文件
  - `python_update`: 更新 Python 文件
  - `python_delete`: 删除 Python 文件
  - `python_execute`: 在沙盒中执行 Python 代码
  - `python_list`: 列出所有 Python 文件
  - `python_sandbox_status`: 获取沙盒状态

### 3. Graph MCP 服务 (graph_mcp/)

#### 3.1 Graph MCP 服务器 (graph_mcp_server.py)
- 封装现有的 GraphManager
- 提供图管理相关的 MCP 工具
- 工具包括：
  - `graph_create`: 创建新图
  - `graph_load`: 加载图
  - `graph_save`: 保存图
  - `graph_delete`: 删除图
  - `graph_list`: 列出所有图
  - `graph_run`: 执行图
  - `graph_node_add`: 添加节点
  - `graph_node_remove`: 移除节点
  - `graph_edge_add`: 添加边
  - `graph_edge_remove`: 移除边
  - `graph_validate`: 验证图结构

## 集成方式

### 与 Agent 集成

在 `agent.py` 中添加内置 MCP 服务：

```python
def _add_internal_mcp_service(self):
    """添加内置的 MCP 服务管理器"""
    from src.mcp import MCPServiceManager
    from src.agent.internal_mcp_client import InternalMCPClient
    
    # 创建 MCP 服务管理器实例
    mcp_service = MCPServiceManager(
        graph_manager=self.graph_manager  # 传入现有的 graph_manager
    )
    
    # 创建内部客户端
    client = InternalMCPClient(mcp_service)
    
    # 创建会话配置
    session_config = MCPSessionConfig(
        name="mcp_service_manager",
        command="internal:mcp_service",
        args=[],
        env={}
    )
    
    # 添加到会话管理器
    self.mcp_session_manager.add_session(
        session_id="internal_mcp_service",
        session_config=session_config,
        client=client
    )
```

## Python 沙盒设计详解

### 沙盒架构概述

Python 沙盒是 MCP 模块中的核心安全组件，用于安全地执行用户提供的 Python 代码。沙盒设计采用多层防护机制，确保代码执行的安全性和隔离性。

### 核心组件

#### 1. SandboxEnvironment 类

沙盒环境的核心实现，负责创建和管理受限的执行环境。

```python
class SandboxEnvironment:
    def __init__(self):
        self.globals = self._create_safe_globals()  # 安全的全局命名空间
        self.locals = {}                            # 局部命名空间
        self.output_buffer = io.StringIO()          # 输出缓冲
        self.error_buffer = io.StringIO()           # 错误缓冲
```

#### 2. 安全的内置函数白名单

沙盒只允许使用经过筛选的安全内置函数：

```python
safe_builtins = {
    # 基础类型
    'int', 'float', 'str', 'bool', 'list', 'dict', 'set', 'tuple',
    
    # 数学和逻辑函数
    'abs', 'all', 'any', 'max', 'min', 'sum', 'round', 'pow',
    'len', 'range', 'enumerate', 'zip', 'map', 'filter',
    
    # 类型转换
    'chr', 'ord', 'hex', 'oct', 'bin',
    
    # 其他安全函数
    'print', 'sorted', 'reversed', 'isinstance', 'issubclass',
    'hasattr', 'getattr', 'setattr', 'dir', 'help',
    
    # 异常类
    'Exception', 'ValueError', 'TypeError', 'KeyError',
    'IndexError', 'AttributeError', 'RuntimeError'
}
```

#### 3. 受限的执行环境

- **禁止的操作**：
  - 文件系统访问（`open`, `file` 等）
  - 网络操作（`socket`, `urllib` 等）
  - 系统调用（`os`, `sys.exit` 等）
  - 进程操作（`subprocess` 等）
  - 导入模块（`import`, `__import__` 等）
  - 执行其他代码（`eval`, `exec` 等）

- **重定向的 I/O**：
  - `print` 输出重定向到内部缓冲区
  - 标准输出和错误输出被捕获
  - 防止直接终端交互

### 执行隔离机制

#### 1. 命名空间隔离

每个沙盒环境维护独立的全局和局部命名空间：
- 全局命名空间只包含白名单中的内置函数
- 局部命名空间用于存储执行过程中的变量
- 不同沙盒之间完全隔离

#### 2. 进程级隔离

对于高安全需求，支持在独立进程中执行代码：

```python
def execute_code(
    self, 
    code: str, 
    sandbox_id: str | None = None,
    timeout: int = 5,
    use_process: bool = True  # 默认使用进程隔离
) -> dict[str, Any]:
```

- 使用 `ProcessPoolExecutor` 创建独立进程
- 进程崩溃不影响主程序
- 自动超时终止

#### 3. 资源限制

- **执行时间限制**：默认 5 秒超时，可配置
- **内存限制**：通过进程隔离天然限制内存使用
- **CPU 限制**：通过超时机制间接限制 CPU 使用

### 持久沙盒机制

支持创建持久的沙盒环境，用于交互式编程：

```python
# 创建持久沙盒
memory_manager.create_sandbox("my_sandbox")

# 在沙盒中执行代码，变量会保留
memory_manager.execute_code("x = 10", sandbox_id="my_sandbox")
memory_manager.execute_code("print(x * 2)", sandbox_id="my_sandbox")  # 输出: 20

# 查看沙盒状态
status = memory_manager.get_sandbox_status("my_sandbox")
# 返回沙盒中的变量信息
```

### 安全特性

#### 1. 代码验证

执行前进行语法检查：
```python
def _validate_python_syntax(self, code: str) -> tuple[bool, str | None]:
    try:
        ast.parse(code)
        return True, None
    except SyntaxError as e:
        return False, f"语法错误: 第 {e.lineno} 行 - {e.msg}"
```

#### 2. 异常处理

所有异常都被捕获并安全地返回：
- 执行错误不会导致服务崩溃
- 错误信息包含完整的堆栈跟踪
- 敏感信息不会泄露

#### 3. 输出捕获

所有输出都被捕获到缓冲区：
- 防止大量输出导致的性能问题
- 输出可以被检查和过滤
- 支持结构化的结果返回

### 使用示例

```python
# 1. 简单代码执行
result = await mcp_service.execute_code(
    code="print('Hello, World!')",
    timeout=5
)

# 2. 使用持久沙盒
await mcp_service.create_sandbox("data_analysis")
await mcp_service.execute_code(
    "import_data = [1, 2, 3, 4, 5]",
    sandbox_id="data_analysis"
)
await mcp_service.execute_code(
    "result = sum(import_data) / len(import_data)",
    sandbox_id="data_analysis"
)

# 3. 错误处理
result = await mcp_service.execute_code(
    "1 / 0",  # 会安全地返回错误信息
    timeout=1
)
```

### 局限性

1. **无法使用第三方库**：只能使用内置函数
2. **无法进行文件操作**：所有文件操作被禁止
3. **无法进行网络请求**：网络功能被禁用
4. **计算密集型任务受限**：有超时限制

这些限制是有意为之，确保沙盒的安全性。对于需要更多功能的场景，建议使用其他专门的执行环境。

## 安全考虑

1. **权限控制**
   - 服务级别的权限管理
   - 工具调用的权限验证

2. **输入验证**
   - 所有输入参数的严格验证
   - 防止注入攻击

3. **审计日志**
   - 记录所有代码执行历史
   - 可追溯的执行记录

## 扩展性

该架构支持轻松添加新的 MCP 服务类型：

1. 在 `src/mcp/` 下创建新的服务目录
2. 实现相应的 MCP 服务器类
3. 在 `MCPServiceManager` 中注册新服务类型
4. 服务自动可用于 Agent 使用

## 模块间依赖关系

```
Agent
  └── MCPServiceManager
       ├── PythonMCPServer
       │    ├── PythonFileManager
       │    └── PythonMemoryManager
       └── GraphMCPServer
            └── GraphManager (来自 src/graph)
```

注意：保持 `GraphManager` 在 `src/graph` 模块中，MCP 模块仅提供协议封装，避免循环依赖。