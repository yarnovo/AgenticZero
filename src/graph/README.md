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

### YAML配置验证

使用新的Schema验证系统验证和操作图配置：

```python
from src.graph.schema import validate_graph_config
from src.graph.config_proxy import GraphConfigProxy

# 1. 验证配置
config = {
    "name": "示例工作流",
    "nodes": [
        {"id": "start", "type": "TaskNode", "name": "开始"},
        {"id": "process", "type": "BranchControlNode", "name": "分支处理", 
         "params": {"condition_func": "lambda x: 'high' if x > 10 else 'low'"}},
        {"id": "end", "type": "TaskNode", "name": "结束"}
    ],
    "edges": [
        {"from": "start", "to": "process"},
        {"from": "process", "to": "end", "action": "high"},
        {"from": "process", "to": "end", "action": "low"}
    ],
    "start_node": "start",
    "end_nodes": ["end"]
}

valid, errors = validate_graph_config(config)
if valid:
    print("✅ 配置有效")
else:
    for error in errors:
        print(f"❌ {error}")

# 2. 使用配置代理
proxy = GraphConfigProxy.create_empty("我的工作流", "演示配置代理")

# 添加节点
proxy.add_node("task1", "TaskNode", "任务1", "处理数据",
               params={"func": "process_data"})
proxy.add_node("task2", "TaskNode", "任务2", "保存结果")

# 添加边
proxy.add_edge("task1", "task2")

# 设置起始和结束节点
proxy.start_node = "task1"
proxy.add_end_node("task2")

# 验证和保存
if proxy.is_valid():
    proxy.save_to_file("workflow.yaml")
    print("✅ 工作流已保存")

# 获取统计信息
stats = proxy.get_statistics()
print(f"节点数: {stats['node_count']}, 边数: {stats['edge_count']}")
```

### 运行测试

```bash
# 运行所有测试
cd /path/to/AgenticZero
make test

# 运行架构演示测试
python -m src.graph.tests.test_architecture

# 运行Schema验证测试
python -m pytest src/graph/tests/test_schema_validator.py -v

# 运行配置代理测试
python -m pytest src/graph/tests/test_config_proxy.py -v

# 运行配置验证演示
python src/graph/examples/schema_validation_demo.py
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

### YAML配置系统

新的配置系统支持Schema验证和双格式配置：

#### 数组格式配置

```yaml
name: "数据处理工作流"
description: "演示数组格式配置"
version: "1.0"
nodes:
  - id: start
    type: SequenceControlNode
    name: 开始节点
    description: "工作流入口"
    params:
      process_func: "lambda x: x"
  - id: branch
    type: BranchControlNode
    name: 条件分支
    params:
      condition_func: "lambda x: 'high' if x > 10 else 'low'"
  - id: end
    type: TaskNode
    name: 结束节点
edges:
  - from: start
    to: branch
    action: default
    weight: 1.0
  - from: branch
    to: end
    action: high
  - from: branch
    to: end
    action: low
start_node: start
end_nodes: [end]
metadata:
  author: "开发者"
  category: "演示"
```

#### 内联格式配置

```yaml
name: "数据处理工作流"
description: "演示内联格式配置"
start_node: start
end_nodes: [end]
start:
  type: SequenceControlNode
  name: 开始节点
  description: "工作流入口"
  params:
    process_func: "lambda x: x"
branch:
  type: BranchControlNode
  name: 条件分支
  params:
    condition_func: "lambda x: 'high' if x > 10 else 'low'"
end:
  type: TaskNode
  name: 结束节点
edges:
  - from: start
    to: branch
  - from: branch
    to: end
    action: high
  - from: branch
    to: end
    action: low
```

#### 配置验证和加载

```python
from src.graph.schema import validate_graph_config_file
from src.graph.config_proxy import GraphConfigProxy

# 验证YAML文件
valid, errors = validate_graph_config_file("workflow.yaml")
if not valid:
    print("配置验证失败:")
    for error in errors:
        print(f"  - {error}")

# 从文件加载配置代理
proxy = GraphConfigProxy.from_file("workflow.yaml")

# 转换为图对象
from src.graph.core import Graph
graph = Graph.from_dict(proxy.to_dict())
```

## API参考

### 配置系统

#### GraphConfigValidator

YAML配置验证器。

**方法**:
- `validate(config: dict) -> tuple[bool, list[str]]`: 验证配置字典
- `detect_format(config: dict) -> str`: 检测配置格式（array/inline）

**便捷函数**:
- `validate_graph_config(config: dict) -> tuple[bool, list[str]]`: 验证配置
- `validate_graph_config_file(file_path: str) -> tuple[bool, list[str]]`: 验证文件

#### GraphConfigProxy

图配置代理对象，提供操作图配置的高级API。

**创建方法**:
- `create_empty(name: str, description: str = "") -> GraphConfigProxy`: 创建空图
- `from_file(config_file: str) -> GraphConfigProxy`: 从文件创建
- `from_dict(config: dict) -> GraphConfigProxy`: 从字典创建

**节点操作**:
- `add_node(node_id, node_type, name, description="", params=None, metadata=None) -> bool`: 添加节点
- `remove_node(node_id: str) -> bool`: 删除节点
- `update_node(node_id, name=None, description=None, params=None, metadata=None) -> bool`: 更新节点
- `get_node(node_id: str) -> dict | None`: 获取节点
- `has_node(node_id: str) -> bool`: 检查节点是否存在
- `list_nodes() -> list[dict]`: 列出所有节点
- `filter_nodes(node_type: str = None) -> list[dict]`: 过滤节点

**边操作**:
- `add_edge(from_node, to_node, action="default", weight=1.0, metadata=None) -> bool`: 添加边
- `remove_edge(from_node, to_node, action="default") -> bool`: 删除边
- `update_edge(from_node, to_node, action="default", new_weight=None, new_metadata=None) -> bool`: 更新边
- `get_edge(from_node, to_node, action="default") -> dict | None`: 获取边
- `has_edge(from_node, to_node, action="default") -> bool`: 检查边是否存在
- `list_edges() -> list[dict]`: 列出所有边

**验证和序列化**:
- `validate() -> tuple[bool, list[str]]`: 验证配置
- `is_valid() -> bool`: 检查是否有效
- `to_dict() -> dict`: 导出为字典
- `to_yaml(indent=2) -> str`: 导出为YAML字符串
- `save_to_file(file_path: str)`: 保存到文件

**高级操作**:
- `clone() -> GraphConfigProxy`: 克隆代理
- `merge(other, conflict_strategy="error") -> GraphConfigProxy`: 合并配置
- `get_statistics() -> dict`: 获取统计信息

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

- `schema_validation_demo.py` - Schema验证和配置代理演示
- `basic_workflow.py` - 基础工作流
- `ai_workflow.py` - AI增强工作流
- `parallel_workflow.py` - 并行执行和异常处理

### Schema验证演示

运行完整的配置系统演示：

```bash
python src/graph/examples/schema_validation_demo.py
```

该演示包括：
- Schema验证功能（有效和无效配置）
- 配置代理基础操作（创建、添加节点和边）
- 高级操作（节点查询、更新、统计）
- 序列化和合并功能
- 错误处理演示
- 文件验证功能

## 贡献指南

欢迎贡献！请遵循以下步骤：

1. Fork项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 许可证

本项目采用MIT许可证。