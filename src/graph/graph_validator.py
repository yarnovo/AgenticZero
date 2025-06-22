"""
图验证器 - 运行时验证Graph对象的结构

验证Graph对象是否符合执行要求，包括：
- 基础结构验证
- 节点类型验证
- 连通性验证
- 执行路径验证
"""

from .atomic_control_nodes import BranchControlNode, ForkControlNode
from .core import BaseNode, Graph, NodeStatus


class GraphValidator:
    """
    图验证器

    用于验证Graph对象的运行时结构是否符合规范。
    """

    def __init__(self):
        """初始化验证器"""
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def validate(self, graph: Graph) -> tuple[bool, list[str]]:
        """
        验证图结构

        Args:
            graph: 要验证的Graph对象

        Returns:
            (是否有效, 错误信息列表)
        """
        self.errors = []
        self.warnings = []

        # 基础验证
        self._validate_basic_structure(graph)

        # 节点验证
        self._validate_nodes(graph)

        # 边验证
        self._validate_edges(graph)

        # 连通性验证
        self._validate_connectivity(graph)

        # 执行路径验证
        self._validate_execution_paths(graph)

        # 特殊节点验证
        self._validate_special_nodes(graph)

        return len(self.errors) == 0, self.errors

    def _validate_basic_structure(self, graph: Graph) -> None:
        """验证基础结构"""
        # 检查是否有节点
        if graph.node_count() == 0:
            self.errors.append("图中没有任何节点")
            return

        # 检查起始节点
        if not graph.start_node_id:
            self.errors.append("未设置起始节点")
        elif graph.start_node_id not in graph.nodes:
            self.errors.append(f"起始节点 '{graph.start_node_id}' 不存在")

        # 检查结束节点
        if not graph.end_node_ids:
            self.errors.append("未设置结束节点")
        else:
            for end_node_id in graph.end_node_ids:
                if end_node_id not in graph.nodes:
                    self.errors.append(f"结束节点 '{end_node_id}' 不存在")

    def _validate_nodes(self, graph: Graph) -> None:
        """验证节点"""
        for node_id, node in graph.nodes.items():
            # 检查节点是否是BaseNode的实例
            if not isinstance(node, BaseNode):
                self.errors.append(f"节点 '{node_id}' 不是BaseNode的实例")
                continue

            # 检查节点ID是否匹配
            if node.node_id != node_id:
                self.errors.append(
                    f"节点ID不匹配: 图中为 '{node_id}'，节点对象为 '{node.node_id}'"
                )

            # 验证特定类型节点的参数
            self._validate_node_params(node)

    def _validate_node_params(self, node: BaseNode) -> None:
        """验证节点参数"""
        node_type = type(node).__name__

        # BranchControlNode验证
        if isinstance(node, BranchControlNode):
            if not node.condition_func:
                self.errors.append(
                    f"分支节点 '{node.node_id}' 缺少必需的 condition_func"
                )

        # ForkControlNode验证
        elif isinstance(node, ForkControlNode):
            if not isinstance(node.fork_count, int) or node.fork_count < 2:
                self.errors.append(
                    f"分叉节点 '{node.node_id}' 的 fork_count 必须是大于等于2的整数"
                )

        # RetryNode验证
        elif node_type == "RetryNode":
            if hasattr(node, "max_retries"):
                max_retries = getattr(node, "max_retries")
                if not isinstance(max_retries, int) or max_retries < 1:
                    self.errors.append(
                        f"重试节点 '{node.node_id}' 的 max_retries 必须是正整数"
                    )

        # TimeoutNode验证
        elif node_type == "TimeoutNode":
            if hasattr(node, "timeout_seconds"):
                timeout_seconds = getattr(node, "timeout_seconds")
                if not isinstance(timeout_seconds, int | float) or timeout_seconds <= 0:
                    self.errors.append(
                        f"超时节点 '{node.node_id}' 的 timeout_seconds 必须是正数"
                    )

    def _validate_edges(self, graph: Graph) -> None:
        """验证边"""
        # 收集所有边
        all_edges = []
        for from_id, edges_dict in graph.edges.items():
            for action, edge in edges_dict.items():
                all_edges.append(edge)

                # 验证边的起始节点
                if edge.from_id != from_id:
                    self.errors.append(
                        f"边的起始节点不匹配: 期望 '{from_id}'，实际 '{edge.from_id}'"
                    )

                # 验证边的目标节点存在
                if edge.to_id not in graph.nodes:
                    self.errors.append(
                        f"边 {edge.from_id} --[{edge.action}]--> {edge.to_id} 的目标节点不存在"
                    )

                # 验证权重
                if not isinstance(edge.weight, int | float) or edge.weight < 0:
                    self.errors.append(
                        f"边 {edge.from_id} --[{edge.action}]--> {edge.to_id} 的权重必须是非负数"
                    )

        # 检查重复的边
        edge_keys = set()
        for edge in all_edges:
            key = (edge.from_id, edge.to_id, edge.action)
            if key in edge_keys:
                self.warnings.append(
                    f"发现重复的边: {edge.from_id} --[{edge.action}]--> {edge.to_id}"
                )
            edge_keys.add(key)

    def _validate_connectivity(self, graph: Graph) -> None:
        """验证连通性"""
        if not graph.start_node_id:
            return  # 基础验证已经处理

        # 检查从起始节点到所有结束节点的可达性
        for end_node_id in graph.end_node_ids:
            if not graph.has_path(graph.start_node_id, end_node_id):
                self.errors.append(
                    f"从起始节点 '{graph.start_node_id}' 无法到达结束节点 '{end_node_id}'"
                )

        # 检查孤立节点（既没有入边也没有出边）
        for node_id in graph.nodes:
            incoming = graph.get_incoming_edges(node_id)
            outgoing = graph.get_outgoing_edges(node_id)

            if not incoming and not outgoing:
                self.errors.append(f"节点 '{node_id}' 是孤立节点（没有任何连接）")
            elif node_id != graph.start_node_id and not incoming:
                self.warnings.append(f"节点 '{node_id}' 没有入边（除非是起始节点）")
            elif node_id not in graph.end_node_ids and not outgoing:
                self.warnings.append(f"节点 '{node_id}' 没有出边（除非是结束节点）")

        # 检查环
        cycles = graph.detect_cycles()
        if cycles:
            for cycle in cycles:
                self.warnings.append(f"检测到环: {' -> '.join(cycle)}")

    def _validate_execution_paths(self, graph: Graph) -> None:
        """验证执行路径"""
        if not graph.start_node_id:
            return

        # 检查是否有不可达的节点
        visited = set()
        queue = [graph.start_node_id]

        while queue:
            node_id = queue.pop(0)
            if node_id in visited:
                continue

            visited.add(node_id)
            neighbors = graph.get_neighbors(node_id)
            queue.extend(neighbors)

        unreachable = set(graph.nodes.keys()) - visited
        for node_id in unreachable:
            self.errors.append(f"节点 '{node_id}' 从起始节点不可达")

        # 检查死锁路径（没有到达结束节点的路径）
        for node_id in visited:
            if node_id in graph.end_node_ids:
                continue

            # 检查是否有路径到达任何结束节点
            can_reach_end = False
            for end_node_id in graph.end_node_ids:
                if graph.has_path(node_id, end_node_id):
                    can_reach_end = True
                    break

            if not can_reach_end and graph.get_outgoing_edges(node_id):
                self.warnings.append(
                    f"节点 '{node_id}' 无法到达任何结束节点（可能存在死锁）"
                )

    def _validate_special_nodes(self, graph: Graph) -> None:
        """验证特殊节点"""
        # 验证分支节点的出边
        for node_id, node in graph.nodes.items():
            node_type = type(node).__name__

            if node_type in ["BranchControlNode", "BranchNode"]:
                outgoing_edges = graph.get_outgoing_edges(node_id)
                if len(outgoing_edges) < 2:
                    self.errors.append(
                        f"分支节点 '{node_id}' 至少需要2条出边，当前只有 {len(outgoing_edges)} 条"
                    )

                # 检查是否有不同的action
                actions = {edge.action for edge in outgoing_edges}
                if len(actions) < 2:
                    self.warnings.append(
                        f"分支节点 '{node_id}' 的所有出边使用相同的action，可能无法正确分支"
                    )

            elif isinstance(node, ForkControlNode):
                outgoing_edges = graph.get_outgoing_edges(node_id)
                if len(outgoing_edges) != node.fork_count:
                    self.warnings.append(
                        f"分叉节点 '{node_id}' 的出边数量({len(outgoing_edges)})与fork_count({node.fork_count})不匹配"
                    )

            elif node_type in ["JoinControlNode", "JoinNode"]:
                incoming_edges = graph.get_incoming_edges(node_id)
                if len(incoming_edges) < 2:
                    self.warnings.append(
                        f"汇聚节点 '{node_id}' 应该有多条入边，当前只有 {len(incoming_edges)} 条"
                    )

            elif node_type in ["MergeControlNode", "MergeNode"]:
                incoming_edges = graph.get_incoming_edges(node_id)
                if len(incoming_edges) < 2:
                    self.warnings.append(
                        f"合并节点 '{node_id}' 应该有多条入边，当前只有 {len(incoming_edges)} 条"
                    )

    def get_warnings(self) -> list[str]:
        """获取警告信息"""
        return self.warnings

    def validate_node_execution_state(self, graph: Graph) -> tuple[bool, list[str]]:
        """
        验证节点执行状态

        Args:
            graph: 要验证的Graph对象

        Returns:
            (是否有效, 错误信息列表)
        """
        errors = []

        # 检查是否有失败的节点
        failed_nodes = []
        for node_id, node in graph.nodes.items():
            if node.status == NodeStatus.FAILED:
                failed_nodes.append(node_id)
                if node.error:
                    errors.append(f"节点 '{node_id}' 执行失败: {node.error}")
                else:
                    errors.append(f"节点 '{node_id}' 执行失败")

        # 检查执行状态的一致性
        for node_id, node in graph.nodes.items():
            if node.status == NodeStatus.SUCCESS:
                # 成功的节点应该有结果
                if node.result is None:
                    errors.append(f"节点 '{node_id}' 标记为成功但没有结果")

            elif node.status == NodeStatus.RUNNING:
                # 运行中的节点不应该有结果或错误
                if node.result is not None or node.error is not None:
                    errors.append(f"节点 '{node_id}' 正在运行但已有结果或错误")

        return len(errors) == 0, errors
