# 图执行框架

这是一个基于原子化控制流节点的图执行框架，支持创建复杂的工作流和数据处理管道。

## 核心概念

### 1. 节点 (Node)
节点是图中的基本执行单元，每个节点都有三个生命周期方法：
- `prep()`: 准备阶段，用于初始化
- `exec()`: 执行阶段，执行主要逻辑
- `post()`: 后处理阶段，决定下一步动作

### 2. 边 (Edge)
边连接节点，定义执行流程。支持：
- 默认边：简单的顺序执行
- 条件边：根据节点返回的动作选择不同路径

### 3. 图 (Graph)
图是节点和边的集合，定义了完整的工作流。图是单入口单出口的设计。

## 原子化控制流节点

框架提供了5种基础的原子化控制流节点，可以组合实现复杂的控制流模式：

### 1. SequenceNode（顺序节点）
- **特征**：一个输入，一个输出
- **用途**：直接执行，无条件传递
- **示例**：
```python
node = SequenceNode("process", "处理节点", lambda x: x * 2)
```

### 2. BranchNode（分支节点）
- **特征**：一个输入，多个输出
- **用途**：根据条件选择一个输出路径
- **示例**：
```python
branch = BranchNode("check", "条件检查", 
    lambda x: "high" if x > 50 else "low")
```

### 3. MergeNode（合并节点）
- **特征**：多个输入，一个输出
- **用途**：任意一个输入到达即可继续
- **示例**：
```python
merge = MergeNode("merge", "合并点")
```

### 4. ForkNode（分叉节点）
- **特征**：一个输入，多个输出
- **用途**：同时激活所有输出路径（并行开始）
- **示例**：
```python
fork = ForkNode("fork", "分叉点")
```

### 5. JoinNode（汇聚节点）
- **特征**：多个输入，一个输出
- **用途**：所有输入都到达才继续（并行结束）
- **示例**：
```python
join = JoinNode("join", "汇聚点", 
    lambda results: sum(results), expected_inputs=3)
```

## 高级控制流模式

通过组合原子节点，可以实现：

### 1. 循环模式
- **组合**：分支节点 + 合并节点（形成回路）
- **示例**：计算累加和、迭代处理

### 2. 条件执行
- **组合**：分支节点 + 合并节点
- **示例**：权限检查、条件路由

### 3. 并行执行
- **组合**：分叉节点 + 汇聚节点
- **示例**：并行数据处理、多任务执行

### 4. 异常处理
- **组合**：分支节点的特殊应用
- **示例**：错误恢复、重试机制

## 使用方式

### 1. 程序化创建

```python
from src.graph import Graph, GraphExecutor, SequenceNode, Edge

# 创建图
graph = Graph()

# 添加节点
node1 = SequenceNode("input", "输入节点")
node2 = SequenceNode("process", "处理节点", lambda x: x * 2)
graph.add_node(node1)
graph.add_node(node2)

# 连接节点
graph.add_edge(Edge("input", "process"))

# 设置起始节点
graph.set_start_node("input")

# 执行
executor = GraphExecutor(graph)
context = await executor.execute()
```

### 2. YAML配置方式

```yaml
name: "示例工作流"
start_node: "input"

nodes:
  - id: input
    type: SequenceNode
    name: "输入节点"
    
  - id: branch
    type: BranchNode
    name: "条件分支"
    
  - id: process_high
    type: SequenceNode
    name: "高值处理"
    
  - id: process_low
    type: SequenceNode
    name: "低值处理"
    
  - id: merge
    type: MergeNode
    name: "合并节点"

edges:
  - source: input
    target: branch
    
  - source: branch
    target: process_high
    action: "high"
    
  - source: branch
    target: process_low
    action: "low"
    
  - source: process_high
    target: merge
    
  - source: process_low
    target: merge
```

## 功能节点

除了原子化控制流节点，框架还提供了多种功能节点：

### SimpleNode
基础节点，用于简单的消息传递。

### DataProcessorNode
数据处理节点，支持各种数据转换操作。

### ConditionalNode
条件判断节点（旧版本，建议使用BranchNode）。

### LoggingNode
日志记录节点，用于调试和监控。

### DelayNode
延迟节点，用于控制执行节奏。

### ErrorNode
错误处理节点，用于测试错误流程。

### RandomChoiceNode
随机选择节点，模拟随机行为。

### AccumulatorNode
累加器节点，收集多个输入。

### FunctionNode
函数节点，执行自定义Python函数。

## 执行器特性

### GraphExecutor
- 支持异步执行
- 自动处理并行节点
- 提供执行上下文管理
- 支持钩子函数（before_node, after_node, on_error, on_complete）
- 防止无限循环（max_iterations）

### ExecutionContext
- 维护共享数据
- 记录执行历史
- 提供执行统计

## 示例

查看 `examples/` 目录下的示例：

1. **atomic_nodes_basic.py** - 基础原子节点使用示例
2. **atomic_nodes_advanced.py** - 高级控制流模式示例
3. **simple_graph_example.py** - 简单图构建示例
4. **run_graph.py** - YAML配置执行示例

## 最佳实践

1. **单一职责**：每个节点应该只负责一个具体的任务
2. **错误处理**：使用分支节点实现错误处理和恢复
3. **并行优化**：合理使用分叉和汇聚节点提高性能
4. **循环控制**：使用分支节点控制循环退出条件，避免无限循环
5. **数据传递**：通过执行上下文在节点间传递数据

## 扩展

可以通过继承 `BaseNode` 创建自定义节点类型：

```python
from src.graph.core import BaseNode

class CustomNode(BaseNode):
    def __init__(self, node_id: str, name: str = None):
        super().__init__(node_id, name)
        
    def exec(self, input_data):
        # 实现自定义逻辑
        return processed_data
```

## 注意事项

1. 图必须是有向无环图（除非特意创建循环）
2. 每个图必须有一个起始节点
3. 节点ID必须唯一
4. 执行器有最大迭代次数限制，防止无限循环