"""
图数据结构实现包

这个包提供了一个轻量级的图数据结构实现，支持：
- 节点和边的创建与管理
- 图的遍历和执行
- 条件分支和循环
- 数据在节点间的传递
- 基于 YAML 的配置解析
- 原子化控制流节点（顺序、分支、合并、分叉、汇聚）
"""

from .atomic_nodes import (
    BranchNode,
    ForkNode,
    JoinNode,
    MergeNode,
    SequenceNode,
)
from .composite_nodes import (
    BatchNode,
    BreakNode,
    ContinueNode,
    DoWhileNode,
    ForEachNode,
    ForNode,
    IfElseNode,
    ParallelNode,
    RaceNode,
    SwitchNode,
    ThrottleNode,
    WhileNode,
)
from .config_parser import GraphConfigParser, load_graph_from_dict, load_graph_from_yaml
from .core import BaseNode, Edge, Graph, NodeStatus
from .executor import ExecutionContext, GraphExecutor

__all__ = [
    # 核心类
    "Graph",
    "BaseNode",
    "Edge",
    "NodeStatus",
    # 执行器
    "GraphExecutor",
    "ExecutionContext",
    # 原子化控制流节点
    "SequenceNode",
    "BranchNode",
    "MergeNode",
    "ForkNode",
    "JoinNode",
    # 复合节点
    "IfElseNode",
    "SwitchNode",
    "WhileNode",
    "DoWhileNode",
    "ForNode",
    "ForEachNode",
    "BreakNode",
    "ContinueNode",
    "ParallelNode",
    "RaceNode",
    "ThrottleNode",
    "BatchNode",
    # 配置解析
    "GraphConfigParser",
    "load_graph_from_yaml",
    "load_graph_from_dict",
]
