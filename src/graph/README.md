# AgenticZero 图执行框架

一个强大的、支持AI智能决策和中断恢复的图执行框架。

## 目录

- [概述](#概述)
- [核心概念](#核心概念)
- [快速开始](#快速开始)
- [节点类型](#节点类型)
- [高级功能](#高级功能)
- [API参考](#api参考)
- [最佳实践](#最佳实践)

## 概述

AgenticZero图执行框架是一个用于构建复杂工作流的Python库。它提供了丰富的节点类型、AI集成能力、异常处理机制，以及完整的序列化和恢复支持。

### 主要特性

- **YAML配置系统**：完整的JSON Schema定义，支持双格式配置和语义化验证
- **配置代理API**：提供高级API操作图配置，支持增删节点和边，实时验证
- **清晰的节点层次结构**：任务节点、控制节点、异常节点
- **AI智能集成**：支持任意AI Agent的接入
- **并行执行支持**：Fork/Join模式
- **异常处理**：Try-Catch、重试、超时、熔断器
- **中断恢复**：完整的快照和恢复机制
- **可扩展设计**：易于添加自定义节点类型

## 核心概念

### 节点层次结构

```
BaseNode (抽象基类)
├── TaskNode (任务节点 - 执行具体业务逻辑)
│   └── AITaskNode (AI任务节点)
├── ControlNode (控制节点 - 控制执行流程)
│   ├── AtomicControlNode (原子控制节点)
│   ├── CompositeControlNode (复合控制节点)
│   └── AIControlNode (AI控制节点)
└── ExceptionNode (异常节点 - 处理异常情况)
```

### 执行生命周期

每个节点都遵循三阶段执行模型：

1. **prep()** - 准备阶段
2. **exec()** - 执行阶段
3. **post()** - 后处理阶段

## 快速开始

### 图代理API

使用GraphProxy操作内存中的图结构：

```python
from src.graph import GraphProxy, TaskNode, BranchControlNode

# 1. 创建图代理
proxy = GraphProxy.create("示例工作流", "演示图代理API")

# 2. 添加节点
proxy.add_node("start", "TaskNode", "开始")
proxy.add_node("process", "BranchControlNode", "分支处理",
               condition_func=lambda x: "high" if x > 10 else "low")
proxy.add_node("end", "TaskNode", "结束")

# 3. 添加边
proxy.add_edge("start", "process")
proxy.add_edge("process", "end", action="high")
proxy.add_edge("process", "end", action="low")

# 4. 设置起始和结束节点
proxy.set_start_node("start")
proxy.add_end_node("end")

# 5. 验证图结构
if proxy.is_valid():
    print("✅ 图结构有效")
else:
    errors = proxy.get_validation_errors()
    for error in errors:
        print(f"❌ {error}")

# 6. 获取统计信息
stats = proxy.get_statistics()
print(f"节点数: {stats['node_count']}, 边数: {stats['edge_count']}")

# 7. 序列化
data = proxy.to_dict()
json_str = proxy.to_json()

# 8. 图分析
paths = proxy.find_all_paths("start", "end")
print(f"从start到end的路径数: {len(paths)}")
```

### YAML配置Schema

为YAML配置文件生成JSON Schema：

```python
from src.graph import YAMLConfigSchema

# 生成Schema文件
YAMLConfigSchema.save_schema_file("graph-config.schema.json")

# 在YAML文件中引用Schema
yaml_content = YAMLConfigSchema.get_yaml_header() + """
name: 数据处理工作流
description: 处理用户数据
start_node: input
end_nodes: [output]

nodes:
  - id: input
    type: TaskNode
    name: 输入处理
  - id: branch
    type: BranchControlNode
    name: 条件分支
    params:
      condition_func: "lambda x: x['score'] > 80"
  - id: output
    type: TaskNode
    name: 输出结果

edges:
  - from: input
    to: branch
  - from: branch
    to: output
    action: high
  - from: branch
    to: output
    action: low
"""
```

### 运行测试

```bash
# 运行所有测试
cd /path/to/AgenticZero
make test

# 运行架构演示测试
python -m src.graph.tests.test_architecture

# 运行图代理测试
python -m pytest src/graph/tests/test_graph_proxy.py -v

# 运行图验证器测试
python -m pytest src/graph/tests/test_graph_validator.py -v
```

### 基础示例

```python
import asyncio
from src.graph import (
    EnhancedGraph,
    SequenceControlNode,
    BranchControlNode,
    TaskNode,
    ResumableExecutor
)

# 创建图
graph = EnhancedGraph("my_workflow")

# 创建节点
start = SequenceControlNode("start", "开始", lambda x: {"data": x})
process = TaskNode("process", "处理", lambda x: x["data"] * 2)
end = TaskNode("end", "结束", lambda x: {"result": x})

# 添加节点和边
graph.add_node(start)
graph.add_node(process)
graph.add_node(end)

graph.add_edge("start", "process")
graph.add_edge("process", "end")

graph.set_start("start")
graph.add_end("end")

# 执行
executor = ResumableExecutor(graph)
context = await executor.execute_with_checkpoints(initial_input=10)
print(f"结果: {context.graph_output}")  # 结果: {"result": 20}
```

### AI节点示例

```python
from src.graph import AIAnalyzer, AIRouter, IAgent

# 实现自定义Agent
class MyAgent(IAgent):
    async def think(self, messages, context=None):
        # 实现AI思考逻辑
        return AgentResponse(content="分析结果", confidence=0.9)
    
    async def decide(self, options, criteria=None, context=None):
        # 实现决策逻辑
        return options[0]

# 使用AI节点
agent = MyAgent()
analyzer = AIAnalyzer("analyzer", "智能分析", agent=agent)
router = AIRouter("router", "智能路由", routes=["path1", "path2"], agent=agent)
```

## 节点类型

### 任务节点 (TaskNode)

执行具体的业务逻辑。

```python
# 使用函数
node = TaskNode("task1", "任务1", process_func=lambda x: x * 2)

# 自定义任务节点
class MyTask(TaskNode):
    async def _execute_task(self, input_data):
        # 自定义处理逻辑
        return {"processed": input_data}
```

### 控制节点 (ControlNode)

控制执行流程。

#### 原子控制节点

- **SequenceControlNode**: 顺序执行
- **BranchControlNode**: 条件分支
- **MergeControlNode**: 合并多个输入
- **ForkControlNode**: 并行分叉
- **JoinControlNode**: 并行汇聚

```python
# 条件分支
branch = BranchControlNode(
    "branch",
    "条件判断",
    condition_func=lambda x: "high" if x > 10 else "low"
)

# 并行执行
fork = ForkControlNode("fork", "分叉", fork_count=3)
join = JoinControlNode("join", "汇聚")
```

### AI节点

#### AI任务节点

- **AIAnalyzer**: 智能分析
- **AIGenerator**: 智能生成
- **AIEvaluator**: 智能评估

#### AI控制节点

- **AIRouter**: 智能路由
- **AIPlanner**: 智能规划

### 异常节点 (ExceptionNode)

处理异常情况。

- **TryCatchNode**: 异常捕获
- **RetryNode**: 自动重试
- **TimeoutNode**: 超时控制
- **CircuitBreakerNode**: 熔断保护

```python
# 重试机制
retry = RetryNode(
    "retry",
    "重试任务",
    target_func=unstable_func,
    max_retries=3,
    retry_delay=1.0
)

# 超时控制
timeout = TimeoutNode(
    "timeout",
    "限时任务",
    target_func=slow_func,
    timeout_seconds=30.0
)
```

## 高级功能

### 序列化和反序列化

```python
# 序列化图
serialized = graph.serialize()

# 保存到文件
import json
with open("graph.json", "w") as f:
    json.dump(serialized, f)

# 反序列化
node_factory = {
    "SequenceControlNode": SequenceControlNode,
    "BranchControlNode": BranchControlNode,
    # ... 其他节点类型
}
restored_graph = EnhancedGraph.deserialize(data, node_factory)
```

### 中断和恢复

```python
# 创建可恢复的执行器
executor = ResumableExecutor(graph)

# 带检查点执行
def on_checkpoint(snapshot):
    # 保存快照
    graph.save_snapshot(snapshot, f"checkpoint_{snapshot.timestamp}.json")

try:
    context = await executor.execute_with_checkpoints(
        initial_input=data,
        checkpoint_callback=on_checkpoint
    )
except Exception as e:
    # 从最后的检查点恢复
    last_snapshot = executor.snapshots[-1]
    context = await executor.resume_from_snapshot(last_snapshot)
```

### 钩子机制

```python
# 注册钩子
def on_node_start(node):
    print(f"开始执行: {node.node_id}")

def on_node_complete(node):
    print(f"完成执行: {node.node_id}")

executor.register_hook("node_start", on_node_start)
executor.register_hook("node_complete", on_node_complete)
```

### YAML配置支持

#### 生成JSON Schema

```python
from src.graph import YAMLConfigSchema

# 生成Schema文件供编辑器使用
YAMLConfigSchema.save_schema_file("graph-config.schema.json")
```

#### YAML配置示例

```yaml
# yaml-language-server: $schema=./graph-config.schema.json
name: "数据处理工作流"
description: "演示工作流配置"
version: "1.0"
start_node: start
end_nodes: [end]

nodes:
  - id: start
    type: TaskNode
    name: 开始处理
    description: "初始化数据"
    params:
      timeout: 30
  - id: branch
    type: BranchControlNode
    name: 条件判断
    params:
      condition_func: "lambda x: 'high' if x > 10 else 'low'"
  - id: end
    type: TaskNode
    name: 结束

edges:
  - from: start
    to: branch
  - from: branch
    to: end
    action: high
  - from: branch
    to: end  
    action: low

metadata:
  author: "系统"
  category: "ETL"
```

#### 加载YAML配置到图代理

```python
from src.graph import GraphProxy, load_graph_from_yaml
import yaml

# 加载YAML配置
with open("workflow.yaml") as f:
    config = yaml.safe_load(f)

# 转换为图代理
proxy = GraphProxy.from_dict(config)

# 或者直接使用配置解析器
graph = load_graph_from_yaml("workflow.yaml")
```

## API参考

### 图操作系统

#### GraphProxy

图代理对象，内部维护Graph实例，提供操作图的高级API。

**创建方法**:
- `create(name: str, description: str = "") -> GraphProxy`: 创建新图代理
- `from_dict(data: dict, node_factory: dict = None) -> GraphProxy`: 从字典创建

**节点操作**:
- `add_node(node_id, node_type, name=None, **kwargs) -> bool`: 添加节点
- `remove_node(node_id: str, cleanup_edges=True) -> bool`: 删除节点
- `update_node(node_id, name=None, **kwargs) -> bool`: 更新节点
- `get_node(node_id: str) -> BaseNode | None`: 获取节点
- `has_node(node_id: str) -> bool`: 检查节点是否存在
- `list_nodes() -> list[tuple[str, BaseNode]]`: 列出所有节点

**边操作**:
- `add_edge(from_id, to_id, action="default", weight=1.0, **metadata) -> bool`: 添加边
- `remove_edge(from_id, to_id, action="default") -> bool`: 删除边
- `update_edge(from_id, to_id, action="default", weight=None, **metadata) -> bool`: 更新边
- `get_edge(from_id, to_id, action="default") -> Edge | None`: 获取边
- `has_edge(from_id, to_id, action="default") -> bool`: 检查边是否存在
- `list_edges() -> list[Edge]`: 列出所有边

**起始/结束节点**:
- `set_start_node(node_id: str) -> bool`: 设置起始节点
- `add_end_node(node_id: str) -> bool`: 添加结束节点
- `remove_end_node(node_id: str) -> bool`: 移除结束节点
- `start_node: str | None`: 获取起始节点ID
- `end_nodes: list[str]`: 获取所有结束节点ID

**图分析**:
- `get_neighbors(node_id: str) -> list[str]`: 获取节点的邻居
- `get_predecessors(node_id: str) -> list[str]`: 获取节点的前驱
- `has_path(from_id, to_id) -> bool`: 检查路径是否存在
- `find_all_paths(from_id, to_id) -> list[list[str]]`: 查找所有路径
- `detect_cycles() -> list[list[str]]`: 检测环
- `topological_sort() -> list[str]`: 拓扑排序

**验证和序列化**:
- `validate() -> tuple[bool, list[str]]`: 验证图结构
- `is_valid() -> bool`: 检查是否有效
- `to_dict() -> dict`: 导出为字典
- `to_json() -> str`: 导出为JSON

**高级操作**:
- `clone() -> GraphProxy`: 克隆图代理
- `merge(other, prefix="") -> bool`: 合并另一个图
- `get_statistics() -> dict`: 获取统计信息
- `add_sequence(node_ids, node_types=None) -> bool`: 添加节点序列
- `register_node_type(type_name, node_class)`: 注册新节点类型

#### GraphValidator

运行时图验证器。

**方法**:
- `validate(graph: Graph) -> tuple[bool, list[str]]`: 验证图结构
- `get_warnings() -> list[str]`: 获取警告信息
- `validate_node_execution_state(graph) -> tuple[bool, list[str]]`: 验证执行状态

#### YAMLConfigSchema

YAML配置文件的JSON Schema定义。

**方法**:
- `get_schema() -> dict`: 获取完整的JSON Schema
- `get_node_param_schema(node_type: str) -> dict`: 获取节点参数Schema
- `save_schema_file(filepath: str)`: 保存Schema到文件
- `get_yaml_header() -> str`: 获取YAML文件头部

### 基础类

#### BaseNode

所有节点的基类。

**方法**:
- `async prep()`: 准备阶段
- `async exec()`: 执行阶段
- `async post()`: 后处理阶段
- `async reset()`: 重置节点状态

#### Graph

基础图结构。

**方法**:
- `add_node(node)`: 添加节点
- `add_edge(from_node, to_node, condition=None)`: 添加边
- `set_start(node_id)`: 设置起始节点
- `add_end(node_id)`: 添加结束节点
- `validate()`: 验证图结构

#### GraphExecutor

图执行器。

**方法**:
- `async execute(initial_input=None, start_node_id=None)`: 执行图
- `add_hook(event, callback)`: 添加钩子

### 增强功能类

#### EnhancedGraph

支持序列化和快照的增强图。

**方法**:
- `serialize()`: 序列化为字典
- `deserialize(data, node_factory)`: 从字典反序列化
- `create_snapshot()`: 创建快照
- `save_snapshot(snapshot, filepath)`: 保存快照
- `load_snapshot(filepath)`: 加载快照

#### ResumableExecutor

可恢复的执行器。

**方法**:
- `execute_with_checkpoints(initial_input, checkpoint_callback)`: 带检查点执行
- `resume_from_snapshot(snapshot)`: 从快照恢复
- `pause()`: 暂停执行
- `resume()`: 恢复执行
- `register_hook(event, callback)`: 注册钩子

### Agent接口

#### IAgent

AI Agent的抽象接口。

**方法**:
- `async think(messages, context)`: 思考/推理
- `async plan(goal, constraints, context)`: 制定计划
- `async decide(options, criteria, context)`: 做出决策
- `async evaluate(subject, criteria, context)`: 评估

## 最佳实践

### 1. 选择合适的节点类型

- 业务逻辑 → TaskNode
- 流程控制 → ControlNode
- 异常处理 → ExceptionNode
- AI增强 → AI节点

### 2. 错误处理

始终考虑错误处理：

```python
# 使用Try-Catch包装不稳定的操作
try_catch = TryCatchNode(
    "safe_operation",
    "安全操作",
    try_func=risky_operation,
    catch_func=handle_error
)

# 对外部服务使用超时控制
timeout = TimeoutNode(
    "api_call",
    "API调用",
    target_func=call_external_api,
    timeout_seconds=30.0
)
```

### 3. 性能优化

- 使用并行节点处理独立任务
- 合理设置检查点间隔
- 避免在节点中执行长时间阻塞操作

### 4. 可维护性

- 为节点使用描述性的ID和名称
- 将复杂逻辑封装为自定义节点类
- 使用配置文件管理大型工作流

### 5. 测试

```python
# 单元测试节点
@pytest.mark.asyncio
async def test_my_node():
    node = MyCustomNode("test", "测试")
    node._input_data = test_input
    result = await node.exec()
    assert result == expected_output

# 集成测试工作流
@pytest.mark.asyncio
async def test_workflow():
    graph = create_test_graph()
    executor = ResumableExecutor(graph)
    context = await executor.execute(test_data)
    assert context.graph_output == expected_result
```

## 示例项目

查看 `examples/` 目录获取更多示例：

- `graph_proxy_demo.py` - 图代理API演示
- `basic_workflow.py` - 基础工作流
- `ai_workflow.py` - AI增强工作流
- `parallel_workflow.py` - 并行执行和异常处理

### 图代理演示

运行完整的图代理系统演示：

```bash
python src/graph/examples/graph_proxy_demo.py
```

该演示包括：
- 图代理创建和基础操作
- 节点和边的增删改查
- 图结构验证
- 图分析功能（路径查找、环检测）
- 序列化和反序列化
- 批量操作和高级功能

## 贡献指南

欢迎贡献！请遵循以下步骤：

1. Fork项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 许可证

本项目采用MIT许可证。