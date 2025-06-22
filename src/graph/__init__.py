"""
图数据结构实现包

这个包提供了一个轻量级的图数据结构实现，支持：
- 节点和边的创建与管理
- 图的遍历和执行
- 条件分支和循环
- 数据在节点间的传递
"""

from .core import BaseNode, Edge, Graph, NodeStatus
from .executor import ExecutionContext, GraphExecutor
from .nodes import (
    AccumulatorNode,
    ConditionalNode,
    DataProcessorNode,
    DelayNode,
    ErrorNode,
    FunctionNode,
    LoggingNode,
    RandomChoiceNode,
    SimpleNode,
)

__all__ = [
    # 核心类
    "Graph",
    "BaseNode",
    "Edge",
    "NodeStatus",
    # 执行器
    "GraphExecutor",
    "ExecutionContext",
    # 节点类型
    "SimpleNode",
    "DataProcessorNode",
    "ConditionalNode",
    "LoggingNode",
    "DelayNode",
    "ErrorNode",
    "RandomChoiceNode",
    "AccumulatorNode",
    "FunctionNode",
]