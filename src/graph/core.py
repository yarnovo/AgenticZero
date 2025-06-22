"""
核心图数据结构实现

包含图、节点、边的基础定义
"""

import json
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any


class NodeStatus(Enum):
    """节点执行状态"""

    PENDING = "pending"  # 等待执行
    RUNNING = "running"  # 正在执行
    SUCCESS = "success"  # 执行成功
    FAILED = "failed"  # 执行失败
    SKIPPED = "skipped"  # 跳过执行


class BaseNode(ABC):
    """
    抽象基础节点类

    所有节点必须继承此类并实现三个核心方法：
    - prep: 准备阶段，用于初始化
    - exec: 执行阶段，执行主要逻辑
    - post: 后处理阶段，决定下一步动作
    """

    def __init__(self, node_id: str, name: str | None = None, **kwargs):
        """
        初始化节点

        Args:
            node_id: 节点唯一标识符
            name: 节点名称（可选）
            **kwargs: 其他元数据
        """
        self.node_id = node_id
        self.name = name or node_id
        self.status = NodeStatus.PENDING
        self.result = None
        self.error = None
        self.metadata = kwargs

    @abstractmethod
    async def prep(self) -> None:
        """准备阶段 - 在执行前调用"""
        pass

    @abstractmethod
    async def exec(self) -> Any:
        """执行阶段 - 执行主要逻辑并返回结果"""
        pass

    @abstractmethod
    async def post(self) -> str:
        """后处理阶段 - 返回下一步的动作标识"""
        pass

    async def run(self) -> str:
        """
        运行节点的完整生命周期

        Returns:
            下一步的动作标识
        """
        try:
            self.status = NodeStatus.RUNNING
            await self.prep()
            self.result = await self.exec()
            action = await self.post()
            self.status = NodeStatus.SUCCESS
            return action
        except Exception as e:
            self.status = NodeStatus.FAILED
            self.error = str(e)
            raise

    def reset(self):
        """重置节点状态"""
        self.status = NodeStatus.PENDING
        self.result = None
        self.error = None

    def __rshift__(self, other: "BaseNode") -> "BaseNode":
        """
        重载 >> 操作符，用于链式连接节点

        示例:
            node1 >> node2 >> node3
        """
        if not hasattr(self, "_temp_graph"):
            self._temp_graph = Graph()

        # 添加节点（如果不存在）
        if self.node_id not in self._temp_graph.nodes:
            self._temp_graph.add_node(self.node_id, self)
        if other.node_id not in self._temp_graph.nodes:
            self._temp_graph.add_node(other.node_id, other)

        # 添加边
        self._temp_graph.add_edge(self.node_id, other.node_id)
        other._temp_graph = self._temp_graph
        return other

    def __sub__(self, action: str) -> "ConditionalEdge":
        """
        重载 - 操作符，用于创建条件边

        示例:
            node1 - "success" >> node2
            node1 - "failure" >> node3
        """
        return ConditionalEdge(self, action)


class ConditionalEdge:
    """条件边的辅助类"""

    def __init__(self, node: BaseNode, action: str):
        self.node = node
        self.action = action

    def __rshift__(self, other: BaseNode) -> BaseNode:
        """完成条件边的连接"""
        if not hasattr(self.node, "_temp_graph"):
            self.node._temp_graph = Graph()

        # 添加节点（如果不存在）
        if self.node.node_id not in self.node._temp_graph.nodes:
            self.node._temp_graph.add_node(self.node.node_id, self.node)
        if other.node_id not in self.node._temp_graph.nodes:
            self.node._temp_graph.add_node(other.node_id, other)

        # 添加带动作的边
        self.node._temp_graph.add_edge(self.node.node_id, other.node_id, self.action)
        other._temp_graph = self.node._temp_graph
        return other


class Edge:
    """图的边"""

    def __init__(
        self, from_id: str, to_id: str, action: str = "default", weight: float = 1.0
    ):
        """
        初始化边

        Args:
            from_id: 起始节点ID
            to_id: 目标节点ID
            action: 动作标识，用于条件分支
            weight: 边的权重
        """
        self.from_id = from_id
        self.to_id = to_id
        self.action = action
        self.weight = weight
        self.metadata = {}

    def __repr__(self):
        return f"Edge({self.from_id} --[{self.action}]--> {self.to_id})"


class Graph:
    """
    图数据结构

    管理节点和边，提供图操作和分析功能
    """

    def __init__(self, name: str | None = None):
        """
        初始化图

        Args:
            name: 图的名称
        """
        self.name = name or "unnamed_graph"
        self.nodes: dict[str, BaseNode] = {}
        self.edges: dict[str, dict[str, Edge]] = {}  # {from_id: {action: Edge}}
        self.start_node_id: str | None = None
        self.end_node_ids: set[str] = set()

    def add_node(self, node_id: str, node: BaseNode) -> None:
        """添加节点到图中"""
        if node_id in self.nodes:
            raise ValueError(f"节点 {node_id} 已经存在")
        self.nodes[node_id] = node
        if node_id not in self.edges:
            self.edges[node_id] = {}

    def add_edge(
        self, from_id: str, to_id: str, action: str = "default", weight: float = 1.0
    ) -> None:
        """
        添加边到图中

        Args:
            from_id: 起始节点ID
            to_id: 目标节点ID
            action: 动作标识
            weight: 边的权重
        """
        if from_id not in self.nodes:
            raise ValueError(f"起始节点 {from_id} 不存在")
        if to_id not in self.nodes:
            raise ValueError(f"目标节点 {to_id} 不存在")

        edge = Edge(from_id, to_id, action, weight)
        self.edges[from_id][action] = edge

        # 确保目标节点在边字典中
        if to_id not in self.edges:
            self.edges[to_id] = {}

    def remove_node(self, node_id: str) -> None:
        """从图中移除节点及其相关的边"""
        if node_id not in self.nodes:
            raise ValueError(f"节点 {node_id} 不存在")

        # 删除节点
        del self.nodes[node_id]

        # 删除从该节点出发的边
        if node_id in self.edges:
            del self.edges[node_id]

        # 删除指向该节点的边
        for edges_dict in self.edges.values():
            to_remove = [
                action for action, edge in edges_dict.items() if edge.to_id == node_id
            ]
            for action in to_remove:
                del edges_dict[action]

    def remove_edge(self, from_id: str, to_id: str, action: str = "default") -> None:
        """移除指定的边"""
        if from_id in self.edges and action in self.edges[from_id]:
            edge = self.edges[from_id][action]
            if edge.to_id == to_id:
                del self.edges[from_id][action]

    def set_start(self, node_id: str) -> None:
        """设置起始节点"""
        if node_id not in self.nodes:
            raise ValueError(f"节点 {node_id} 不存在")
        self.start_node_id = node_id

    def add_end(self, node_id: str) -> None:
        """添加结束节点"""
        if node_id not in self.nodes:
            raise ValueError(f"节点 {node_id} 不存在")
        self.end_node_ids.add(node_id)

    def get_node(self, node_id: str) -> BaseNode | None:
        """获取节点"""
        return self.nodes.get(node_id)

    def get_edge(self, from_id: str, action: str = "default") -> Edge | None:
        """获取边"""
        return self.edges.get(from_id, {}).get(action)

    def get_next_node_id(self, current_id: str, action: str = "default") -> str | None:
        """根据当前节点和动作获取下一个节点ID"""
        edge = self.get_edge(current_id, action)
        return edge.to_id if edge else None

    def get_outgoing_edges(self, node_id: str) -> list[Edge]:
        """获取从指定节点出发的所有边"""
        return list(self.edges.get(node_id, {}).values())

    def get_incoming_edges(self, node_id: str) -> list[Edge]:
        """获取指向指定节点的所有边"""
        incoming = []
        for edges_dict in self.edges.values():
            for edge in edges_dict.values():
                if edge.to_id == node_id:
                    incoming.append(edge)
        return incoming

    def get_neighbors(self, node_id: str) -> list[str]:
        """获取节点的所有邻居节点ID"""
        edges = self.get_outgoing_edges(node_id)
        return [edge.to_id for edge in edges]

    def get_predecessors(self, node_id: str) -> list[str]:
        """获取节点的所有前驱节点ID"""
        edges = self.get_incoming_edges(node_id)
        return [edge.from_id for edge in edges]

    def has_path(self, from_id: str, to_id: str) -> bool:
        """检查两个节点之间是否存在路径"""
        if from_id not in self.nodes or to_id not in self.nodes:
            return False

        visited = set()
        queue = [from_id]

        while queue:
            current = queue.pop(0)
            if current == to_id:
                return True

            if current in visited:
                continue

            visited.add(current)
            neighbors = self.get_neighbors(current)
            queue.extend(neighbors)

        return False

    def find_all_paths(self, from_id: str, to_id: str) -> list[list[str]]:
        """查找两个节点之间的所有路径"""
        if from_id not in self.nodes or to_id not in self.nodes:
            return []

        paths = []

        def dfs(current: str, target: str, path: list[str]):
            if current == target:
                paths.append(path.copy())
                return

            for neighbor in self.get_neighbors(current):
                if neighbor not in path:  # 避免循环
                    path.append(neighbor)
                    dfs(neighbor, target, path)
                    path.pop()

        dfs(from_id, to_id, [from_id])
        return paths

    def detect_cycles(self) -> list[list[str]]:
        """检测图中的所有环"""
        cycles = []

        def dfs(node_id: str, visited: set[str], path: list[str]):
            visited.add(node_id)
            path.append(node_id)

            for neighbor in self.get_neighbors(node_id):
                if neighbor in path:
                    cycle_start = path.index(neighbor)
                    cycles.append(path[cycle_start:] + [neighbor])
                elif neighbor not in visited:
                    dfs(neighbor, visited, path)

            path.pop()

        visited = set()
        for node_id in self.nodes:
            if node_id not in visited:
                dfs(node_id, visited, [])

        return cycles

    def topological_sort(self) -> list[str]:
        """拓扑排序"""
        in_degree = {node_id: 0 for node_id in self.nodes}

        # 计算入度
        for edges_dict in self.edges.values():
            for edge in edges_dict.values():
                in_degree[edge.to_id] += 1

        # 找出所有入度为0的节点
        queue = [node_id for node_id, degree in in_degree.items() if degree == 0]
        result = []

        while queue:
            current = queue.pop(0)
            result.append(current)

            # 更新邻居的入度
            for edge in self.get_outgoing_edges(current):
                in_degree[edge.to_id] -= 1
                if in_degree[edge.to_id] == 0:
                    queue.append(edge.to_id)

        if len(result) != len(self.nodes):
            raise ValueError("图中存在环，无法进行拓扑排序")

        return result

    def validate(self) -> tuple[bool, list[str]]:
        """验证图的结构完整性"""
        errors = []

        # 检查是否设置了起始节点
        if not self.start_node_id:
            errors.append("未设置起始节点")

        # 检查没有出边的节点是否标记为结束节点
        for node_id in self.nodes:
            outgoing = self.get_outgoing_edges(node_id)
            if not outgoing and node_id not in self.end_node_ids:
                errors.append(f"节点 {node_id} 没有出边且未标记为结束节点")

        # 检查是否有不可达节点
        unreachable = []
        if self.start_node_id:
            for node_id in self.nodes:
                if node_id != self.start_node_id and not self.has_path(
                    self.start_node_id, node_id
                ):
                    unreachable.append(node_id)

        if unreachable:
            errors.append(f"从起始节点无法到达的节点: {unreachable}")

        # 检查是否存在环
        cycles = self.detect_cycles()
        if cycles:
            errors.append(f"图中存在环: {cycles}")

        return len(errors) == 0, errors

    def to_dict(self) -> dict[str, Any]:
        """将图转换为字典格式"""
        return {
            "name": self.name,
            "nodes": {
                node_id: {
                    "name": node.name,
                    "status": node.status.value,
                    "metadata": node.metadata,
                }
                for node_id, node in self.nodes.items()
            },
            "edges": [
                {
                    "from": edge.from_id,
                    "to": edge.to_id,
                    "action": edge.action,
                    "weight": edge.weight,
                }
                for edges_dict in self.edges.values()
                for edge in edges_dict.values()
            ],
            "start_node": self.start_node_id,
            "end_nodes": list(self.end_node_ids),
        }

    def to_json(self) -> str:
        """将图转换为JSON格式"""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)

    def node_count(self) -> int:
        """获取节点数量"""
        return len(self.nodes)

    def edge_count(self) -> int:
        """获取边的数量"""
        return sum(len(edges_dict) for edges_dict in self.edges.values())

    def __repr__(self):
        return f"Graph(name={self.name}, nodes={self.node_count()}, edges={self.edge_count()})"
