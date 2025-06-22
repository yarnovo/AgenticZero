"""
图数据结构实现包 - 重新设计版本

基于新的节点层次结构：
- BaseNode
  ├── TaskNode (任务节点)
  │   └── AITaskNode (AI任务节点)
  ├── ControlNode (控制节点)
  │   ├── AtomicControlNode (原子控制节点)
  │   ├── CompositeControlNode (复合控制节点)
  │   └── AIControlNode (AI控制节点)
  └── ExceptionNode (异常节点)
"""

# 核心基础
from .core import BaseNode, Edge, Graph, NodeStatus
from .executor import ExecutionContext, GraphExecutor

# 节点类型基类
from .node_types import (
    NodeCategory,
    TaskNode,
    ControlNode,
    ExceptionNode,
)

# 原子控制节点
from .atomic_control_nodes import (
    AtomicControlNode,
    SequenceControlNode,
    BranchControlNode,
    MergeControlNode,
    ForkControlNode,
    JoinControlNode,
)

# 复合控制节点
from .composite_control_nodes import (
    CompositeControlNode,
)

# AI控制节点
from .ai_control_nodes import (
    AIControlNode,
    AIRouter,
    AIPlanner,
)

# AI任务节点
from .ai_task_nodes import (
    AITaskNode,
    AIAnalyzer,
    AIGenerator,
    AIEvaluator,
)

# 异常节点
from .exception_nodes import (
    TryCatchNode,
    RetryNode,
    TimeoutNode,
    CircuitBreakerNode,
)

# Agent接口
from .agent_interface import (
    IAgent,
    AgentProxy,
    AgentMessage,
    AgentResponse,
)

# 增强功能
from .enhanced_graph import (
    EnhancedGraph,
    GraphSnapshot,
    ResumableExecutor,
)

# 配置解析（保留原有功能）
from .config_parser import (
    GraphConfigParser,
    load_graph_from_yaml,
    load_graph_from_dict,
)

__all__ = [
    # 核心类
    "BaseNode",
    "Edge", 
    "Graph",
    "NodeStatus",
    "GraphExecutor",
    "ExecutionContext",
    
    # 节点类型
    "NodeCategory",
    "TaskNode",
    "ControlNode",
    "ExceptionNode",
    
    # 原子控制节点
    "AtomicControlNode",
    "SequenceControlNode",
    "BranchControlNode",
    "MergeControlNode",
    "ForkControlNode",
    "JoinControlNode",
    
    # 复合控制节点
    "CompositeControlNode",
    
    # AI控制节点
    "AIControlNode",
    "AIRouter",
    "AIPlanner",
    
    # AI任务节点
    "AITaskNode",
    "AIAnalyzer",
    "AIGenerator",
    "AIEvaluator",
    
    # 异常节点
    "TryCatchNode",
    "RetryNode", 
    "TimeoutNode",
    "CircuitBreakerNode",
    
    # Agent接口
    "IAgent",
    "AgentProxy",
    "AgentMessage",
    "AgentResponse",
    
    # 增强功能
    "EnhancedGraph",
    "GraphSnapshot",
    "ResumableExecutor",
    
    # 配置解析
    "GraphConfigParser",
    "load_graph_from_yaml",
    "load_graph_from_dict",
]

# 版本信息
__version__ = "2.0.0"  # 重新设计版本