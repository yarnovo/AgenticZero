# AgenticZero 图框架架构设计

## 架构概述

AgenticZero图框架采用分层架构设计，将节点系统分为三个主要类别，每个类别承担特定的职责。这种设计提供了清晰的关注点分离和高度的可扩展性。

## 设计原则

1. **单一职责原则**：每种节点类型专注于特定功能
2. **开闭原则**：易于扩展新节点类型，无需修改现有代码
3. **依赖倒置原则**：高层模块依赖抽象接口而非具体实现
4. **接口隔离原则**：不同类型的节点有各自特定的接口

## 核心架构

### 配置系统架构

AgenticZero提供完整的图配置系统，包括Schema验证、配置代理和文件管理：

#### Schema验证架构

```
配置验证系统
├── JSON Schema定义
│   ├── 数组格式Schema (nodes数组)
│   ├── 内联格式Schema (直接节点定义)
│   ├── 节点Schema (类型、参数验证)
│   └── 边Schema (连接关系验证)
├── 语义验证器
│   ├── 节点引用验证
│   ├── 图连通性验证
│   ├── 参数有效性验证
│   └── 循环检测
└── 错误报告
    ├── 中文语义化错误信息
    ├── 错误位置定位
    └── 修复建议
```

#### 配置代理架构

```
GraphConfigProxy
├── 内存图表示
├── CRUD操作API
│   ├── 节点操作 (add/remove/update)
│   ├── 边操作 (add/remove/update)
│   ├── 起始/结束节点管理
│   └── 元数据管理
├── 实时验证
├── 序列化支持
│   ├── YAML格式
│   ├── 字典格式
│   └── 文件读写
└── 高级操作
    ├── 图克隆
    ├── 图合并
    ├── 统计信息
    └── 冲突解决
```

#### 支持的配置格式

**数组格式**（传统格式）：
```yaml
name: "工作流名称"
nodes:
  - id: "node1"
    type: "TaskNode"
    name: "节点1"
edges:
  - from: "node1"
    to: "node2"
start_node: "node1"
end_nodes: ["node2"]
```

**内联格式**（简化格式）：
```yaml
name: "工作流名称"
start_node: "node1"
end_nodes: ["node2"]
node1:
  type: "TaskNode"
  name: "节点1"
node2:
  type: "TaskNode"
  name: "节点2"
edges:
  - from: "node1"
    to: "node2"
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

## 配置系统使用指南

### 1. Schema验证

#### 基础验证
```python
from src.graph.schema import validate_graph_config

config = {
    "name": "示例工作流",
    "nodes": [...],
    "edges": [...],
    "start_node": "start",
    "end_nodes": ["end"]
}

valid, errors = validate_graph_config(config)
if not valid:
    for error in errors:
        print(f"验证错误: {error}")
```

#### 文件验证
```python
from src.graph.schema import validate_graph_config_file

valid, errors = validate_graph_config_file("workflow.yaml")
```

### 2. 配置代理使用

#### 创建和操作图
```python
from src.graph.config_proxy import GraphConfigProxy

# 创建空图
proxy = GraphConfigProxy.create_empty("工作流名称", "描述")

# 添加节点
proxy.add_node("task1", "TaskNode", "任务1", 
               description="处理数据",
               params={"func": "process_data"},
               metadata={"category": "data"})

# 添加边
proxy.add_edge("task1", "task2", action="success", weight=1.0)

# 设置起始和结束节点
proxy.start_node = "task1"
proxy.add_end_node("task2")

# 验证配置
if proxy.is_valid():
    print("✅ 配置有效")
else:
    errors = proxy.get_validation_errors()
    for error in errors:
        print(f"❌ {error}")
```

#### 高级操作
```python
# 克隆图
cloned = proxy.clone()

# 合并图
merged = proxy1.merge(proxy2, conflict_strategy="override")

# 获取统计信息
stats = proxy.get_statistics()
print(f"节点数: {stats['node_count']}")
print(f"边数: {stats['edge_count']}")

# 序列化
yaml_str = proxy.to_yaml()
config_dict = proxy.to_dict()

# 保存到文件
proxy.save_to_file("workflow.yaml")
```

### 3. 节点类型和参数

#### 支持的节点类型
- **TaskNode**: 基础任务节点，无特殊参数要求
- **BranchControlNode**: 分支节点，必需参数：`condition_func`
- **RetryNode**: 重试节点，参数：`max_retries` (正整数), `retry_delay` (非负数)
- **TimeoutNode**: 超时节点，参数：`timeout_seconds` (正数)
- **AIRouter**: AI路由节点，必需参数：`routes` (至少2个元素的列表)

#### 参数验证规则
```python
# 分支节点示例
proxy.add_node("branch", "BranchControlNode", "条件分支",
               params={"condition_func": "lambda x: x > 10"})

# 重试节点示例
proxy.add_node("retry", "RetryNode", "重试处理",
               params={"max_retries": 3, "retry_delay": 1.0})

# AI路由节点示例
proxy.add_node("router", "AIRouter", "智能路由",
               params={"routes": ["path_a", "path_b", "path_c"]})
```

### 4. 错误处理和调试

#### 常见错误类型
1. **节点引用错误**: 起始节点、结束节点或边引用不存在的节点
2. **参数验证错误**: 节点类型特定的参数缺失或无效
3. **连通性错误**: 从起始节点无法到达结束节点
4. **重复定义**: 节点ID重复定义

#### 调试技巧
```python
# 获取详细的验证信息
valid, errors = proxy.validate()
if not valid:
    print("配置验证失败:")
    for i, error in enumerate(errors, 1):
        print(f"  {i}. {error}")

# 检查图连通性
stats = proxy.get_statistics()
if stats["isolated_nodes"]:
    print(f"发现孤立节点: {stats['isolated_nodes']}")

# 分析节点和边
print(f"节点类型分布: {stats['node_types']}")
print(f"最大入度: {stats['max_in_degree']}")
print(f"最大出度: {stats['max_out_degree']}")
```