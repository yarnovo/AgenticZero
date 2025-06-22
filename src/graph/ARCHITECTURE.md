# AgenticZero 图框架架构设计

## 架构概述

AgenticZero图框架采用分层架构设计，将节点系统分为三个主要类别，每个类别承担特定的职责。这种设计提供了清晰的关注点分离和高度的可扩展性。

## 设计原则

1. **单一职责原则**：每种节点类型专注于特定功能
2. **开闭原则**：易于扩展新节点类型，无需修改现有代码
3. **依赖倒置原则**：高层模块依赖抽象接口而非具体实现
4. **接口隔离原则**：不同类型的节点有各自特定的接口

## 核心架构

### 图操作系统架构

AgenticZero提供完整的图操作系统，包括图代理、验证器和YAML Schema：

#### 图代理架构

```
GraphProxy
├── 内部Graph实例
├── 节点操作API
│   ├── add_node(支持字符串或类)
│   ├── remove_node(自动清理边)
│   ├── update_node(更新属性)
│   └── 查询和列表操作
├── 边操作API
│   ├── add_edge(支持元数据)
│   ├── remove_edge
│   ├── update_edge
│   └── 查询和列表操作
├── 图分析功能
│   ├── 路径查找
│   ├── 环检测
│   ├── 拓扑排序
│   └── 邻居/前驱查询
├── 实时验证
├── 序列化支持
│   ├── to_dict()
│   ├── to_json()
│   └── from_dict()
└── 高级操作
    ├── 克隆
    ├── 合并
    ├── 批量操作
    └── 统计信息
```

#### 图验证器架构

```
GraphValidator
├── 基础结构验证
│   ├── 节点存在性
│   ├── 起始/结束节点
│   └── 基本完整性
├── 节点验证
│   ├── 类型验证
│   ├── 参数验证
│   └── 状态验证
├── 边验证
│   ├── 节点引用
│   ├── 权重验证
│   └── 重复检查
├── 连通性验证
│   ├── 可达性检查
│   ├── 孤立节点
│   └── 死锁检测
└── 执行路径验证
    ├── 路径完整性
    └── 特殊节点验证
```

#### YAML Schema架构

```
YAMLConfigSchema
├── JSON Schema定义
│   ├── 根级别属性
│   ├── 节点Schema
│   ├── 边Schema
│   └── 元数据Schema
├── 节点类型定义
│   ├── 基础节点类型
│   ├── 控制节点类型
│   ├── 异常节点类型
│   └── AI节点类型
└── 辅助功能
    ├── Schema文件生成
    ├── YAML头部生成
    └── 节点参数Schema
```

### 节点层次结构

```
BaseNode (抽象基类)
├── TaskNode (任务节点)
│   ├── 自定义任务节点
│   └── AITaskNode (AI任务节点)
│       ├── AIAnalyzer
│       ├── AIGenerator
│       └── AIEvaluator
├── ControlNode (控制节点)
│   ├── AtomicControlNode (原子控制节点)
│   │   ├── SequenceControlNode
│   │   ├── BranchControlNode
│   │   ├── MergeControlNode
│   │   ├── ForkControlNode
│   │   └── JoinControlNode
│   ├── CompositeControlNode (复合控制节点)
│   └── AIControlNode (AI控制节点)
│       ├── AIRouter
│       └── AIPlanner
└── ExceptionNode (异常节点)
    ├── TryCatchNode
    ├── RetryNode
    ├── TimeoutNode
    └── CircuitBreakerNode
```

### 执行模型

#### 三阶段执行生命周期

```python
class BaseNode:
    async def run(self):
        # 1. 准备阶段
        await self.prep()
        
        # 2. 执行阶段
        self.result = await self.exec()
        
        # 3. 后处理阶段
        next_node = await self.post()
        
        return next_node
```

#### 执行流程控制

1. **顺序执行**：默认模式，节点按照边的定义顺序执行
2. **条件执行**：通过BranchNode实现条件分支
3. **并行执行**：通过Fork/Join模式实现并行处理
4. **循环执行**：通过控制节点的post()方法实现

### AI集成架构

#### Agent接口设计

```python
class IAgent(ABC):
    @abstractmethod
    async def think(self, messages, context):
        """推理和思考"""
        
    @abstractmethod
    async def plan(self, goal, constraints, context):
        """制定计划"""
        
    @abstractmethod
    async def decide(self, options, criteria, context):
        """做出决策"""
        
    @abstractmethod
    async def evaluate(self, subject, criteria, context):
        """评估结果"""
```

#### AI节点架构

```
AI节点
├── Agent接口 (外部AI系统)
├── 对话历史管理
├── 上下文构建
└── 结果解析
```

### 异常处理架构

独立的异常处理层，提供多种错误恢复策略：

1. **Try-Catch模式**：捕获并处理特定异常
2. **重试机制**：自动重试失败的操作
3. **超时控制**：防止长时间阻塞
4. **熔断器**：保护系统免受连续失败的影响

### 持久化架构

#### 序列化设计

```
图序列化
├── 图结构 (节点、边、起始/结束)
├── 节点配置
├── 元数据
└── 执行状态（可选）
```

#### 快照机制

```
GraphSnapshot
├── 图结构快照
├── 执行状态
├── 节点状态
└── 上下文数据
```

## 关键设计决策

### 1. 节点类型分离

**决策**：将节点分为任务、控制和异常三大类

**理由**：
- 清晰的职责划分
- 不同类型有不同的接口需求
- 便于理解和维护

### 2. AI作为独立层

**决策**：AI功能通过Agent接口集成，而非内置

**理由**：
- 支持多种AI系统
- 避免供应商锁定
- 保持核心框架的轻量级

### 3. 异常节点独立

**决策**：异常处理节点直接继承自BaseNode

**理由**：
- 异常处理是横切关注点
- 可以在任何地方使用
- 不依赖于特定的节点类型

### 4. 快照和恢复

**决策**：实现完整的状态快照和恢复机制

**理由**：
- 支持长时间运行的工作流
- 故障恢复能力
- 调试和审计需求

## 扩展点

### 1. 自定义节点类型

```python
class MyCustomTask(TaskNode):
    async def _execute_task(self, input_data):
        # 自定义逻辑
        return result

class MyCustomControl(ControlNode):
    async def exec(self):
        # 控制逻辑
        return control_data
        
    async def _decide_next(self):
        # 决策逻辑
        return next_node_id
```

### 2. 自定义Agent实现

```python
class OpenAIAgent(IAgent):
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)
        
    async def think(self, messages, context):
        response = await self.client.chat.completions.create(...)
        return AgentResponse(...)
```

### 3. 自定义执行器

```python
class CustomExecutor(ResumableExecutor):
    async def _execute_node(self, node):
        # 自定义执行逻辑
        await super()._execute_node(node)
```

### 4. 自定义序列化

```python
def custom_node_factory(node_data):
    # 自定义节点创建逻辑
    return node_instance
```

## 性能考虑

### 1. 异步执行

- 所有节点操作都是异步的
- 支持并发执行多个独立节点
- 避免阻塞操作

### 2. 内存管理

- 节点状态按需加载
- 执行历史可配置保留策略
- 大数据通过引用传递

### 3. 检查点优化

- 可配置的检查点间隔
- 增量快照支持
- 异步快照保存

## 安全考虑

### 1. 输入验证

- 节点输入类型检查
- 图结构验证
- 循环检测

### 2. 资源限制

- 超时控制
- 内存使用限制
- 并发执行限制

### 3. 错误隔离

- 节点级别的错误隔离
- 异常不会影响整个图执行
- 详细的错误追踪

## 未来演进方向

### 1. 分布式执行

- 跨机器的节点执行
- 分布式状态管理
- 负载均衡

### 2. 可视化支持

- 实时执行监控
- 图形化编辑器
- 性能分析工具

### 3. 更多AI集成

- 多模态AI支持
- Agent协作机制
- 自动优化工作流

### 4. 高级特性

- 事务支持
- 版本控制
- A/B测试能力

## 图操作系统使用指南

### 1. 使用GraphProxy操作图

#### 基础操作
```python
from src.graph import GraphProxy

# 创建图代理
proxy = GraphProxy.create("工作流", "示例工作流")

# 添加节点（使用字符串类型）
proxy.add_node("task1", "TaskNode", "任务1")
proxy.add_node("branch", "BranchControlNode", "分支",
               condition_func=lambda x: x > 10)

# 添加边
proxy.add_edge("task1", "branch")
proxy.add_edge("branch", "task2", action="high", weight=2.0)

# 设置起始和结束节点
proxy.set_start_node("task1")
proxy.add_end_node("task2")

# 验证图结构
if proxy.is_valid():
    print("✅ 图结构有效")
else:
    for error in proxy.get_validation_errors():
        print(f"❌ {error}")
```

#### 图分析
```python
# 路径查找
if proxy.has_path("task1", "task2"):
    paths = proxy.find_all_paths("task1", "task2")
    print(f"找到{len(paths)}条路径")

# 环检测
cycles = proxy.detect_cycles()
if cycles:
    print(f"发现{len(cycles)}个环")

# 拓扑排序
try:
    order = proxy.topological_sort()
    print(f"拓扑顺序: {order}")
except ValueError:
    print("图中存在环，无法拓扑排序")

# 获取统计信息
stats = proxy.get_statistics()
print(f"节点数: {stats['node_count']}")
print(f"边数: {stats['edge_count']}")
print(f"是否有环: {stats['has_cycles']}")
```

#### 高级操作
```python
# 克隆图
cloned = proxy.clone()

# 合并图
other_proxy = GraphProxy.create("另一个工作流")
other_proxy.add_sequence(["a", "b", "c"])
proxy.merge(other_proxy, prefix="sub_")

# 批量添加节点
nodes = [
    ("n1", "TaskNode", "节点1", {}),
    ("n2", "BranchControlNode", "分支", {"condition_func": lambda x: x}),
]
count = proxy.add_nodes_batch(nodes)

# 添加节点序列
proxy.add_sequence(["step1", "step2", "step3"])

# 注册自定义节点类型
class CustomNode(TaskNode):
    pass

proxy.register_node_type("CustomNode", CustomNode)
proxy.add_node("custom", "CustomNode")
```

### 2. 使用GraphValidator验证

```python
from src.graph import GraphValidator

# 创建验证器
validator = GraphValidator()

# 验证图结构
valid, errors = validator.validate(proxy.graph)
if not valid:
    print("验证失败:")
    for error in errors:
        print(f"  - {error}")

# 获取警告信息
warnings = validator.get_warnings()
for warning in warnings:
    print(f"⚠️ {warning}")

# 验证执行状态
valid, errors = validator.validate_node_execution_state(proxy.graph)
```

### 3. 使用YAML Schema

#### 生成Schema文件
```python
from src.graph import YAMLConfigSchema

# 生成Schema文件
YAMLConfigSchema.save_schema_file("graph-config.schema.json")

# 获取YAML头部
header = YAMLConfigSchema.get_yaml_header()
print(header)
```

#### 配置示例
```yaml
# yaml-language-server: $schema=./graph-config.schema.json
name: "数据处理工作流"
start_node: input
end_nodes: [output]

nodes:
  - id: input
    type: TaskNode
    name: 输入处理
  - id: process
    type: BranchControlNode
    name: 条件判断
    params:
      condition_func: "lambda x: 'high' if x > 100 else 'low'"
  - id: output
    type: TaskNode
    name: 输出结果

edges:
  - from: input
    to: process
  - from: process
    to: output
    action: high
  - from: process
    to: output
    action: low
```

### 4. 常见错误和调试

#### 常见错误
1. **节点不存在**: 添加边时引用不存在的节点
2. **参数错误**: 特定节点类型缺少必需参数
3. **连通性问题**: 从起始节点无法到达结束节点
4. **环检测**: 图中存在循环

#### 调试技巧
```python
# 检查特定节点
if proxy.has_node("task1"):
    node = proxy.get_node("task1")
    print(f"节点类型: {type(node).__name__}")
    print(f"节点状态: {node.status}")

# 检查边
if proxy.has_edge("task1", "task2"):
    edge = proxy.get_edge("task1", "task2")
    print(f"边权重: {edge.weight}")
    print(f"边动作: {edge.action}")

# 列出所有节点
for node_id, node in proxy.list_nodes():
    print(f"{node_id}: {node.name} ({type(node).__name__})")

# 列出所有边
for edge in proxy.list_edges():
    print(f"{edge.from_id} --[{edge.action}]--> {edge.to_id}")
```