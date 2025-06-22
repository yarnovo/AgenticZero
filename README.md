# AgenticZero

一个强大的、支持AI智能决策和中断恢复的图执行框架。

## 概述

AgenticZero是一个基于Python的图执行框架，提供了丰富的节点类型、AI集成能力、异常处理机制，以及完整的序列化和恢复支持。

### 主要特性

- **灵活的图结构**：支持任务节点、控制节点、异常节点的完整执行引擎
- **图代理API**：提供高级API操作内存中的图结构，包括增删节点、增删边、验证等
- **YAML配置支持**：通过JSON Schema提供完整的YAML配置文件验证
- **AI智能集成**：支持任意AI Agent的接入，实现智能路由和决策
- **并行执行支持**：Fork/Join模式的并行任务处理
- **异常处理**：Try-Catch、重试、超时、熔断器等完整异常处理机制
- **中断恢复**：完整的快照和恢复机制，支持长时间运行的工作流
- **可扩展设计**：易于添加自定义节点类型

## 快速开始

### 安装

```bash
git clone https://github.com/yourusername/agenticzero.git
cd agenticzero
pip install -e .
```

### 基础示例

使用GraphProxy创建和操作图：

```python
from src.graph import GraphProxy

# 创建图代理
proxy = GraphProxy.create("示例工作流", "演示基本功能")

# 添加节点
proxy.add_node("start", "TaskNode", "开始")
proxy.add_node("process", "BranchControlNode", "处理",
               condition_func=lambda x: "high" if x > 10 else "low")
proxy.add_node("end", "TaskNode", "结束")

# 添加边
proxy.add_edge("start", "process")
proxy.add_edge("process", "end", action="high")
proxy.add_edge("process", "end", action="low")

# 设置起始和结束节点
proxy.set_start_node("start")
proxy.add_end_node("end")

# 验证图结构
if proxy.is_valid():
    print("✅ 图结构有效")
```

### YAML配置

```yaml
# yaml-language-server: $schema=./graph-config.schema.json
name: 数据处理工作流
start_node: input
end_nodes: [output]

nodes:
  - id: input
    type: TaskNode
    name: 输入处理
  - id: branch
    type: BranchControlNode  
    name: 条件判断
    params:
      condition_func: "lambda x: 'high' if x > 100 else 'low'"
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
```

## 文档

- [架构设计](src/graph/ARCHITECTURE.md) - 系统架构和设计决策
- [API文档](src/graph/README.md) - 详细的API参考和使用指南
- [示例代码](src/graph/examples/) - 各种使用场景的示例

## 运行测试

```bash
# 运行所有测试
make test

# 运行代码检查
make check

# 格式化代码
make format
```

## 贡献

欢迎贡献！请遵循以下步骤：

1. Fork项目
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m '添加一些很棒的功能'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

## 许可证

本项目采用MIT许可证。详见[LICENSE](LICENSE)文件。
