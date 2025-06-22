# 图执行框架

这是一个基于 YAML 配置的图执行框架，支持创建复杂的工作流和数据处理管道。参考了 PocketFlow 的设计理念，提供了灵活的节点类型和执行模式。

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
图是节点和边的集合，定义了完整的工作流。

## 内置节点类型

### SimpleNode
最基础的节点类型，用于简单的消息传递或占位。

```yaml
- id: my_node
  type: SimpleNode
  params:
    message: "Hello World"
```

### DataProcessorNode
数据处理节点，支持多种数据转换操作。

```yaml
- id: processor
  type: DataProcessorNode
  params:
    process_type: "uppercase"  # 可选: uppercase, lowercase, reverse
```

### ConditionalNode
条件判断节点，根据条件返回不同的动作。

```yaml
- id: condition
  type: ConditionalNode
  params:
    condition_type: "value_check"
    threshold: 50
```

### LoggingNode
日志记录节点，用于调试和监控。

```yaml
- id: logger
  type: LoggingNode
  params:
    level: "info"  # 可选: debug, info, warning, error
    message: "Custom log message"
```

### DelayNode
延迟节点，用于模拟耗时操作或控制执行节奏。

```yaml
- id: delay
  type: DelayNode
  params:
    delay: 2.0  # 延迟秒数
    message: "Waiting..."
```

### ErrorNode
错误处理节点，用于测试错误处理流程。

```yaml
- id: error
  type: ErrorNode
  params:
    error_message: "Something went wrong"
    recover: true  # 是否可恢复
```

### RandomChoiceNode
随机选择节点，用于模拟随机行为。

```yaml
- id: random
  type: RandomChoiceNode
  params:
    choices: ["option1", "option2", "option3"]
    weights: [0.5, 0.3, 0.2]  # 可选，各选项的权重
```

### AccumulatorNode
累加器节点，用于收集多个输入。

```yaml
- id: accumulator
  type: AccumulatorNode
  params:
    wait_for: 3  # 等待的输入数量
```

### FunctionNode
函数节点，调用自定义 Python 函数。

```yaml
- id: custom_func
  type: FunctionNode
  params:
    function: "module.path:function_name"
```

## YAML 配置格式

### 基本结构

```yaml
# 图的名称
name: "我的工作流"

# 自定义节点类型（可选）
custom_nodes:
  MyCustomNode: "my_module.nodes:MyCustomNode"

# 节点定义
nodes:
  - id: node1          # 唯一标识符
    type: SimpleNode   # 节点类型
    name: "节点1"      # 显示名称（可选）
    params:            # 节点参数
      key: value
    metadata:          # 元数据（可选）
      author: "me"

# 边定义
edges:
  - from: node1        # 起始节点
    to: node2          # 目标节点
    action: "default"  # 动作标识（可选）
    weight: 1.0        # 权重（可选）

# 起始节点
start_node: node1

# 结束节点（可多个）
end_nodes: [node3, node4]
```

### 条件分支

```yaml
edges:
  # 条件节点根据返回的动作选择路径
  - from: condition_node
    to: success_node
    action: "success"
    
  - from: condition_node
    to: failure_node
    action: "failure"
```

### 并行执行

```yaml
nodes:
  - id: splitter
    type: SimpleNode
    
  - id: parallel1
    type: DataProcessorNode
    
  - id: parallel2
    type: DataProcessorNode
    
  - id: collector
    type: AccumulatorNode
    params:
      wait_for: 2

edges:
  # 分发到多个并行任务
  - from: splitter
    to: parallel1
    action: "task1"
    
  - from: splitter
    to: parallel2
    action: "task2"
    
  # 收集结果
  - from: parallel1
    to: collector
    
  - from: parallel2
    to: collector
```

## 使用示例

### 1. 加载和执行图

```python
from src.graph import load_graph_from_yaml, GraphExecutor

# 从 YAML 文件加载图
graph = load_graph_from_yaml("path/to/config.yaml")

# 创建执行器
executor = GraphExecutor(graph)

# 执行图
result = await executor.execute({"input": "data"})
```

### 2. 程序化创建图

```python
from src.graph import Graph, SimpleNode, DataProcessorNode

# 创建图
graph = Graph("my_graph")

# 创建节点
start = SimpleNode("start", "开始")
process = DataProcessorNode("process", "处理")
end = SimpleNode("end", "结束")

# 添加节点到图
graph.add_node("start", start)
graph.add_node("process", process)
graph.add_node("end", end)

# 添加边
graph.add_edge("start", "process")
graph.add_edge("process", "end")

# 设置起始和结束节点
graph.set_start("start")
graph.add_end("end")
```

### 3. 使用链式语法

```python
from src.graph import SimpleNode, DataProcessorNode

# 使用 >> 操作符链接节点
start = SimpleNode("start")
process = DataProcessorNode("process")
end = SimpleNode("end")

# 创建流程
start >> process >> end

# 使用 - 操作符创建条件边
condition = ConditionalNode("check")
success = SimpleNode("success")
failure = SimpleNode("failure")

condition - "true" >> success
condition - "false" >> failure
```

## 自定义节点

创建自定义节点需要继承 `BaseNode` 类：

```python
from src.graph import BaseNode

class MyCustomNode(BaseNode):
    def __init__(self, node_id: str, name: str = None, **kwargs):
        super().__init__(node_id, name, **kwargs)
        self.my_param = kwargs.get("my_param", "default")
    
    async def prep(self) -> None:
        """准备阶段"""
        print(f"Preparing {self.name}")
    
    async def exec(self) -> Any:
        """执行主逻辑"""
        # 执行自定义逻辑
        result = self.my_param.upper()
        return result
    
    async def post(self) -> str:
        """决定下一步动作"""
        if self.result:
            return "success"
        else:
            return "failure"
```

然后在 YAML 中注册和使用：

```yaml
custom_nodes:
  MyCustomNode: "my_module:MyCustomNode"

nodes:
  - id: custom
    type: MyCustomNode
    params:
      my_param: "hello"
```

## 执行上下文

执行器维护一个共享的上下文，节点可以通过它传递数据：

```python
class DataNode(BaseNode):
    async def exec(self) -> Any:
        # 从上下文读取数据
        input_data = self.context.get("input_data")
        
        # 处理数据
        processed = process(input_data)
        
        # 写入上下文
        self.context["processed_data"] = processed
        
        return processed
```

## 错误处理

框架支持多种错误处理策略：

1. **节点级重试**：节点可以定义重试逻辑
2. **错误恢复**：通过 ErrorNode 实现错误恢复流程
3. **全局错误处理**：执行器级别的错误处理

## 最佳实践

1. **保持节点简单**：每个节点应该只做一件事
2. **使用有意义的 ID**：节点 ID 应该描述其功能
3. **合理使用条件分支**：避免过度复杂的分支逻辑
4. **错误处理**：始终考虑错误情况和恢复策略
5. **文档化**：为自定义节点添加详细的文档字符串

## 调试和监控

使用 LoggingNode 添加调试信息：

```yaml
nodes:
  - id: debug
    type: LoggingNode
    params:
      level: "debug"
      message: "Current state: {context}"
```

或者使用执行器的事件监听：

```python
executor = GraphExecutor(graph)
executor.on_node_start = lambda node: print(f"Starting {node.name}")
executor.on_node_complete = lambda node: print(f"Completed {node.name}")
```

## 示例配置

查看 `examples/graph_configs/` 目录下的示例配置：

- `simple_flow.yaml`: 简单的顺序流程
- `conditional_flow.yaml`: 条件分支示例
- `parallel_flow.yaml`: 并行执行示例
- `error_handling_flow.yaml`: 错误处理示例
- `function_flow.yaml`: 函数节点示例

## 参考资料

本项目参考了 [PocketFlow](https://github.com/pocketflow/pocketflow) 的设计理念，提供了更简洁的 YAML 配置方式和更丰富的内置节点类型。