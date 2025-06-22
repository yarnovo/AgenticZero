"""
图代理对象 - 提供操作内存Graph对象的高级API

这个代理对象内部维护一个Graph实例，提供一系列SDK方法来操作图，
包括增删节点、增删边、验证、序列化等功能。
"""

from typing import Any

from .atomic_control_nodes import (
    BranchControlNode,
    ForkControlNode,
    JoinControlNode,
    MergeControlNode,
    SequenceControlNode,
)
from .core import BaseNode, Edge, Graph, NodeStatus
from .graph_validator import GraphValidator
from .node_types import TaskNode


class GraphProxy:
    """
    图代理对象

    内部维护一个Graph实例，提供高级API来操作图结构。
    所有操作都会实时验证，确保图的完整性。
    """

    def __init__(self, graph: Graph | None = None, auto_validate: bool = False):
        """
        初始化图代理

        Args:
            graph: 现有的Graph实例，如果为None则创建新图
            auto_validate: 是否在每次操作后自动验证
        """
        self._graph = graph or Graph()
        self._auto_validate = auto_validate
        self._validator = GraphValidator()
        self._node_factory = self._get_default_node_factory()
        self._description: str = ""

    @classmethod
    def create(cls, name: str, description: str = "") -> "GraphProxy":
        """
        创建一个新的图代理

        Args:
            name: 图的名称
            description: 图的描述

        Returns:
            GraphProxy实例
        """
        graph = Graph(name)
        proxy = cls(graph)
        proxy._description = description
        return proxy

    def _get_default_node_factory(self) -> dict[str, type[BaseNode]]:
        """获取默认的节点工厂"""
        return {
            "TaskNode": TaskNode,
            "SequenceControlNode": SequenceControlNode,
            "BranchControlNode": BranchControlNode,
            "MergeControlNode": MergeControlNode,
            "ForkControlNode": ForkControlNode,
            "JoinControlNode": JoinControlNode,
        }

    # ========== 节点操作 ==========

    def add_node(
        self,
        node_id: str,
        node_type: str | type[BaseNode],
        name: str | None = None,
        **kwargs,
    ) -> bool:
        """
        添加节点

        Args:
            node_id: 节点ID
            node_type: 节点类型字符串或节点类
            name: 节点名称
            **kwargs: 节点的其他参数

        Returns:
            是否添加成功
        """
        try:
            # 确定节点类
            if isinstance(node_type, str):
                if node_type not in self._node_factory:
                    raise ValueError(f"未知的节点类型: {node_type}")
                node_class = self._node_factory[node_type]
            else:
                node_class = node_type

            # 创建节点实例
            node = node_class(node_id, name or node_id, **kwargs)

            # 添加到图中
            self._graph.add_node(node)

            # 验证
            if self._auto_validate:
                valid, _ = self.validate()
                return valid

            return True

        except Exception as e:
            print(f"添加节点失败: {e}")
            return False

    def remove_node(self, node_id: str, cleanup_edges: bool = True) -> bool:
        """
        删除节点

        Args:
            node_id: 节点ID
            cleanup_edges: 是否同时清理相关的边

        Returns:
            是否删除成功
        """
        try:
            # 检查节点是否是起始/结束节点
            if self._graph.start_node_id == node_id:
                self._graph.start_node_id = None
            if node_id in self._graph.end_node_ids:
                self._graph.end_node_ids.remove(node_id)

            # 删除节点
            self._graph.remove_node(node_id)

            # 验证
            if self._auto_validate:
                valid, _ = self.validate()
                return valid

            return True

        except Exception as e:
            print(f"删除节点失败: {e}")
            return False

    def update_node(self, node_id: str, name: str | None = None, **kwargs) -> bool:
        """
        更新节点属性

        Args:
            node_id: 节点ID
            name: 新的节点名称
            **kwargs: 其他要更新的属性

        Returns:
            是否更新成功
        """
        try:
            node = self._graph.get_node(node_id)
            if not node:
                raise ValueError(f"节点 {node_id} 不存在")

            if name is not None:
                node.name = name

            # 更新元数据
            node.metadata.update(kwargs)

            return True

        except Exception as e:
            print(f"更新节点失败: {e}")
            return False

    def get_node(self, node_id: str) -> BaseNode | None:
        """获取节点对象"""
        return self._graph.get_node(node_id)

    def list_nodes(self) -> list[tuple[str, BaseNode]]:
        """列出所有节点"""
        return list(self._graph.nodes.items())

    def has_node(self, node_id: str) -> bool:
        """检查节点是否存在"""
        return node_id in self._graph.nodes

    # ========== 边操作 ==========

    def add_edge(
        self,
        from_id: str,
        to_id: str,
        action: str = "default",
        weight: float = 1.0,
        **metadata,
    ) -> bool:
        """
        添加边

        Args:
            from_id: 起始节点ID
            to_id: 目标节点ID
            action: 动作标识
            weight: 边的权重
            **metadata: 边的元数据

        Returns:
            是否添加成功
        """
        try:
            edge = Edge(from_id, to_id, action, weight)
            edge.metadata = metadata

            self._graph.add_edge(edge)

            # 验证
            if self._auto_validate:
                valid, _ = self.validate()
                return valid

            return True

        except Exception as e:
            print(f"添加边失败: {e}")
            return False

    def remove_edge(self, from_id: str, to_id: str, action: str = "default") -> bool:
        """
        删除边

        Args:
            from_id: 起始节点ID
            to_id: 目标节点ID
            action: 动作标识

        Returns:
            是否删除成功
        """
        try:
            self._graph.remove_edge(from_id, to_id, action)

            # 验证
            if self._auto_validate:
                valid, _ = self.validate()
                return valid

            return True

        except Exception as e:
            print(f"删除边失败: {e}")
            return False

    def update_edge(
        self,
        from_id: str,
        to_id: str,
        action: str = "default",
        weight: float | None = None,
        **metadata,
    ) -> bool:
        """
        更新边属性

        Args:
            from_id: 起始节点ID
            to_id: 目标节点ID
            action: 动作标识
            weight: 新的权重
            **metadata: 要更新的元数据

        Returns:
            是否更新成功
        """
        try:
            edge = self._graph.get_edge(from_id, action)
            if not edge or edge.to_id != to_id:
                raise ValueError(f"边 {from_id} --[{action}]--> {to_id} 不存在")

            if weight is not None:
                edge.weight = weight

            edge.metadata.update(metadata)

            return True

        except Exception as e:
            print(f"更新边失败: {e}")
            return False

    def get_edge(
        self, from_id: str, to_id: str, action: str = "default"
    ) -> Edge | None:
        """获取边对象"""
        edge = self._graph.get_edge(from_id, action)
        return edge if edge and edge.to_id == to_id else None

    def list_edges(self) -> list[Edge]:
        """列出所有边"""
        edges = []
        for edges_dict in self._graph.edges.values():
            edges.extend(edges_dict.values())
        return edges

    def has_edge(self, from_id: str, to_id: str, action: str = "default") -> bool:
        """检查边是否存在"""
        return self.get_edge(from_id, to_id, action) is not None

    # ========== 起始/结束节点操作 ==========

    def set_start_node(self, node_id: str) -> bool:
        """设置起始节点"""
        try:
            self._graph.set_start(node_id)
            return True
        except Exception as e:
            print(f"设置起始节点失败: {e}")
            return False

    def add_end_node(self, node_id: str) -> bool:
        """添加结束节点"""
        try:
            self._graph.add_end(node_id)
            return True
        except Exception as e:
            print(f"添加结束节点失败: {e}")
            return False

    def remove_end_node(self, node_id: str) -> bool:
        """移除结束节点"""
        try:
            if node_id in self._graph.end_node_ids:
                self._graph.end_node_ids.remove(node_id)
            return True
        except Exception as e:
            print(f"移除结束节点失败: {e}")
            return False

    @property
    def start_node(self) -> str | None:
        """获取起始节点ID"""
        return self._graph.start_node_id

    @property
    def end_nodes(self) -> list[str]:
        """获取所有结束节点ID"""
        return list(self._graph.end_node_ids)

    # ========== 图分析操作 ==========

    def get_neighbors(self, node_id: str) -> list[str]:
        """获取节点的所有邻居"""
        return self._graph.get_neighbors(node_id)

    def get_predecessors(self, node_id: str) -> list[str]:
        """获取节点的所有前驱"""
        return self._graph.get_predecessors(node_id)

    def has_path(self, from_id: str, to_id: str) -> bool:
        """检查两个节点间是否有路径"""
        return self._graph.has_path(from_id, to_id)

    def find_all_paths(self, from_id: str, to_id: str) -> list[list[str]]:
        """查找两个节点间的所有路径"""
        return self._graph.find_all_paths(from_id, to_id)

    def detect_cycles(self) -> list[list[str]]:
        """检测图中的环"""
        return self._graph.detect_cycles()

    def topological_sort(self) -> list[str]:
        """拓扑排序"""
        return self._graph.topological_sort()

    # ========== 验证操作 ==========

    def validate(self) -> tuple[bool, list[str]]:
        """验证图的结构"""
        return self._validator.validate(self._graph)

    def is_valid(self) -> bool:
        """检查图是否有效"""
        valid, _ = self.validate()
        return valid

    def get_validation_errors(self) -> list[str]:
        """获取验证错误"""
        _, errors = self.validate()
        return errors

    # ========== 序列化操作 ==========

    def to_dict(self) -> dict[str, Any]:
        """导出为字典"""
        return self._graph.to_dict()

    def to_json(self) -> str:
        """导出为JSON"""
        return self._graph.to_json()

    @classmethod
    def from_dict(
        cls, data: dict[str, Any], node_factory: dict[str, type[BaseNode]] | None = None
    ) -> "GraphProxy":
        """
        从字典创建图代理

        Args:
            data: 图的字典表示
            node_factory: 节点工厂，用于创建节点实例

        Returns:
            GraphProxy实例
        """
        # 创建图
        graph = Graph(data.get("name", "unnamed"))

        # 创建代理
        proxy = cls(graph)
        if node_factory:
            proxy._node_factory.update(node_factory)

        # 添加节点
        nodes = data.get("nodes", {})
        for node_id, node_data in nodes.items():
            node_type = node_data.get("type", "TaskNode")
            name = node_data.get("name", node_id)
            metadata = node_data.get("metadata", {})
            proxy.add_node(node_id, node_type, name, **metadata)

        # 添加边
        edges = data.get("edges", [])
        for edge_data in edges:
            proxy.add_edge(
                edge_data["from"],
                edge_data["to"],
                edge_data.get("action", "default"),
                edge_data.get("weight", 1.0),
                **edge_data.get("metadata", {}),
            )

        # 设置起始和结束节点
        if "start_node" in data:
            proxy.set_start_node(data["start_node"])

        for end_node in data.get("end_nodes", []):
            proxy.add_end_node(end_node)

        return proxy

    # ========== 批量操作 ==========

    def add_nodes_batch(self, nodes: list[tuple[str, str, str, dict]]) -> int:
        """
        批量添加节点

        Args:
            nodes: 节点列表，每个元素为 (node_id, node_type, name, kwargs)

        Returns:
            成功添加的节点数量
        """
        count = 0
        for node_id, node_type, name, kwargs in nodes:
            if self.add_node(node_id, node_type, name, **kwargs):
                count += 1
        return count

    def add_edges_batch(self, edges: list[tuple[str, str, str, float]]) -> int:
        """
        批量添加边

        Args:
            edges: 边列表，每个元素为 (from_id, to_id, action, weight)

        Returns:
            成功添加的边数量
        """
        count = 0
        for from_id, to_id, action, weight in edges:
            if self.add_edge(from_id, to_id, action, weight):
                count += 1
        return count

    # ========== 图操作 ==========

    def clear(self) -> None:
        """清空图"""
        self._graph = Graph(self._graph.name)

    def clone(self) -> "GraphProxy":
        """克隆图代理"""
        data = self.to_dict()
        return GraphProxy.from_dict(data, self._node_factory)

    def merge(self, other: "GraphProxy", prefix: str = "") -> bool:
        """
        合并另一个图

        Args:
            other: 要合并的图代理
            prefix: 节点ID前缀，避免冲突

        Returns:
            是否合并成功
        """
        try:
            # 合并节点
            for node_id, node in other.list_nodes():
                new_id = f"{prefix}{node_id}" if prefix else node_id
                if not self.has_node(new_id):
                    self.add_node(new_id, type(node), node.name, **node.metadata)

            # 合并边
            for edge in other.list_edges():
                new_from = f"{prefix}{edge.from_id}" if prefix else edge.from_id
                new_to = f"{prefix}{edge.to_id}" if prefix else edge.to_id
                self.add_edge(
                    new_from, new_to, edge.action, edge.weight, **edge.metadata
                )

            return True

        except Exception as e:
            print(f"合并图失败: {e}")
            return False

    # ========== 统计信息 ==========

    def get_statistics(self) -> dict[str, Any]:
        """获取图的统计信息"""
        stats = {
            "node_count": self._graph.node_count(),
            "edge_count": self._graph.edge_count(),
            "has_cycles": len(self.detect_cycles()) > 0,
            "is_valid": self.is_valid(),
            "start_node": self.start_node,
            "end_node_count": len(self.end_nodes),
        }

        # 节点类型分布
        node_types = {}
        for _, node in self.list_nodes():
            node_type = type(node).__name__
            node_types[node_type] = node_types.get(node_type, 0) + 1
        stats["node_types"] = node_types

        # 节点度数统计
        max_in_degree = 0
        max_out_degree = 0
        for node_id in self._graph.nodes:
            in_degree = len(self.get_predecessors(node_id))
            out_degree = len(self.get_neighbors(node_id))
            max_in_degree = max(max_in_degree, in_degree)
            max_out_degree = max(max_out_degree, out_degree)
        stats["max_in_degree"] = max_in_degree
        stats["max_out_degree"] = max_out_degree

        return stats

    # ========== 执行状态操作 ==========

    def reset_all_nodes(self) -> None:
        """重置所有节点状态"""
        for node in self._graph.nodes.values():
            node.reset()

    def get_node_status(self, node_id: str) -> NodeStatus | None:
        """获取节点执行状态"""
        node = self.get_node(node_id)
        return node.status if node else None

    def get_failed_nodes(self) -> list[str]:
        """获取所有失败的节点"""
        return [
            node_id
            for node_id, node in self._graph.nodes.items()
            if node.status == NodeStatus.FAILED
        ]

    def get_pending_nodes(self) -> list[str]:
        """获取所有待执行的节点"""
        return [
            node_id
            for node_id, node in self._graph.nodes.items()
            if node.status == NodeStatus.PENDING
        ]

    # ========== 便捷方法 ==========

    def add_sequence(
        self, node_ids: list[str], node_types: list[str] | None = None
    ) -> bool:
        """
        添加一个节点序列

        Args:
            node_ids: 节点ID列表
            node_types: 节点类型列表，如果为None则全部使用TaskNode

        Returns:
            是否添加成功
        """
        if not node_ids:
            return False

        if node_types is None:
            node_types = ["TaskNode"] * len(node_ids)

        if len(node_ids) != len(node_types):
            print("节点ID和类型数量不匹配")
            return False

        # 添加节点
        for node_id, node_type in zip(node_ids, node_types):
            if not self.add_node(node_id, node_type):
                return False

        # 添加边
        for i in range(len(node_ids) - 1):
            if not self.add_edge(node_ids[i], node_ids[i + 1]):
                return False

        return True

    def register_node_type(self, type_name: str, node_class: type[BaseNode]) -> None:
        """注册新的节点类型"""
        self._node_factory[type_name] = node_class

    @property
    def graph(self) -> Graph:
        """获取内部的Graph对象（只读）"""
        return self._graph

    @property
    def name(self) -> str:
        """获取图名称"""
        return self._graph.name

    @name.setter
    def name(self, value: str) -> None:
        """设置图名称"""
        self._graph.name = value

    def __repr__(self) -> str:
        return f"GraphProxy({self._graph})"
