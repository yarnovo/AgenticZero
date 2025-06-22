"""
YAML 配置解析器

将 YAML 配置文件转换为图结构
"""

import importlib
from typing import Any

import yaml

from .ai_control_nodes import (
    AIPlanner,
    AIRouter,
)
from .ai_task_nodes import (
    AIAnalyzer,
    AIEvaluator,
    AIGenerator,
)

# 导入新的节点类型
from .atomic_control_nodes import (
    BranchControlNode,
    ForkControlNode,
    JoinControlNode,
    MergeControlNode,
    SequenceControlNode,
)
from .composite_control_nodes import (
    CompositeControlNode,
)
from .core import BaseNode, Graph
from .exception_nodes import (
    CircuitBreakerNode,
    RetryNode,
    TimeoutNode,
    TryCatchNode,
)
from .node_types import (
    ControlNode,
    ExceptionNode,
    TaskNode,
)


class GraphConfigParser:
    """图配置解析器"""

    # 内置节点类型映射
    BUILTIN_NODE_TYPES = {
        # 基础节点类型
        "TaskNode": TaskNode,
        "ControlNode": ControlNode,
        "ExceptionNode": ExceptionNode,
        # 原子控制节点
        "SequenceControlNode": SequenceControlNode,
        "BranchControlNode": BranchControlNode,
        "MergeControlNode": MergeControlNode,
        "ForkControlNode": ForkControlNode,
        "JoinControlNode": JoinControlNode,
        # 异常处理节点
        "TryCatchNode": TryCatchNode,
        "RetryNode": RetryNode,
        "TimeoutNode": TimeoutNode,
        "CircuitBreakerNode": CircuitBreakerNode,
        # 复合控制节点
        "CompositeControlNode": CompositeControlNode,
        # AI控制节点
        "AIRouter": AIRouter,
        "AIPlanner": AIPlanner,
        # AI任务节点
        "AIAnalyzer": AIAnalyzer,
        "AIGenerator": AIGenerator,
        "AIEvaluator": AIEvaluator,
        # 保留原有名称的兼容性映射
        "SequenceNode": SequenceControlNode,
        "BranchNode": BranchControlNode,
        "MergeNode": MergeControlNode,
        "ForkNode": ForkControlNode,
        "JoinNode": JoinControlNode,
    }

    def __init__(self):
        """初始化解析器"""
        self.custom_node_types: dict[str, type[BaseNode]] = {}

    def register_node_type(self, name: str, node_class: type[BaseNode]) -> None:
        """
        注册自定义节点类型

        Args:
            name: 节点类型名称
            node_class: 节点类
        """
        self.custom_node_types[name] = node_class

    def parse_file(self, config_file: str) -> Graph:
        """
        从 YAML 文件解析图配置

        Args:
            config_file: YAML 配置文件路径

        Returns:
            Graph: 解析得到的图对象
        """
        with open(config_file, encoding="utf-8") as f:
            config = yaml.safe_load(f)

        return self.parse_config(config)

    def parse_config(self, config: dict[str, Any]) -> Graph:
        """
        从字典配置解析图

        Args:
            config: 配置字典

        Returns:
            Graph: 解析得到的图对象
        """
        # 创建图
        graph_name = config.get("name", "unnamed_graph")
        graph = Graph(graph_name)

        # 注册自定义节点类型（如果有）
        if "custom_nodes" in config and config["custom_nodes"]:
            self._load_custom_nodes(config["custom_nodes"])

        # 解析节点
        nodes_config = config.get("nodes", [])
        for node_config in nodes_config:
            node = self._create_node(node_config)
            graph.add_node(node.node_id, node)

        # 解析边
        edges_config = config.get("edges", [])
        for edge_config in edges_config:
            self._create_edge(graph, edge_config)

        # 设置起始节点
        if "start_node" in config:
            graph.set_start(config["start_node"])

        # 设置结束节点
        end_nodes = config.get("end_nodes", [])
        for node_id in end_nodes:
            graph.add_end(node_id)

        # 验证图结构
        valid, errors = graph.validate()
        if not valid:
            raise ValueError(f"图配置无效: {'; '.join(errors)}")

        return graph

    def _load_custom_nodes(self, custom_nodes_config: dict[str, str]) -> None:
        """
        加载自定义节点类型

        Args:
            custom_nodes_config: 自定义节点配置，格式为 {节点类型名: 模块路径}
        """
        for node_type, module_path in custom_nodes_config.items():
            try:
                # 分离模块路径和类名
                module_name, class_name = module_path.rsplit(".", 1)

                # 导入模块
                module = importlib.import_module(module_name)

                # 获取类
                node_class = getattr(module, class_name)

                # 注册节点类型
                self.register_node_type(node_type, node_class)

            except Exception as e:
                raise ValueError(f"无法加载自定义节点类型 {node_type}: {e}")

    def _create_node(self, node_config: dict[str, Any]) -> BaseNode:
        """
        创建节点实例

        Args:
            node_config: 节点配置

        Returns:
            BaseNode: 节点实例
        """
        node_id = node_config.get("id")
        if not node_id:
            raise ValueError("节点必须有 id 字段")

        node_type = node_config.get("type", "SimpleNode")
        node_name = node_config.get("name", node_id)

        # 获取节点类
        if node_type in self.BUILTIN_NODE_TYPES:
            node_class = self.BUILTIN_NODE_TYPES[node_type]
        elif node_type in self.custom_node_types:
            node_class = self.custom_node_types[node_type]
        else:
            raise ValueError(f"未知的节点类型: {node_type}")

        # 获取节点参数
        params = node_config.get("params", {})
        metadata = node_config.get("metadata", {})

        # 创建节点实例
        node = node_class(node_id=node_id, name=node_name, **metadata)

        # 设置节点参数
        for param_name, param_value in params.items():
            if hasattr(node, param_name):
                setattr(node, param_name, param_value)

        return node

    def _create_edge(self, graph: Graph, edge_config: dict[str, Any]) -> None:
        """
        创建边

        Args:
            graph: 图对象
            edge_config: 边配置
        """
        from_id = edge_config.get("from")
        to_id = edge_config.get("to")

        if not from_id or not to_id:
            raise ValueError("边必须有 from 和 to 字段")

        action = edge_config.get("action", "default")
        weight = edge_config.get("weight", 1.0)

        graph.add_edge(from_id, to_id, action, weight)


def load_graph_from_yaml(config_file: str) -> Graph:
    """
    便捷函数：从 YAML 文件加载图

    Args:
        config_file: YAML 配置文件路径

    Returns:
        Graph: 解析得到的图对象
    """
    parser = GraphConfigParser()
    return parser.parse_file(config_file)


def load_graph_from_dict(config: dict[str, Any]) -> Graph:
    """
    便捷函数：从字典配置加载图

    Args:
        config: 配置字典

    Returns:
        Graph: 解析得到的图对象
    """
    parser = GraphConfigParser()
    return parser.parse_config(config)
