"""
增强图结构

支持序列化和中断恢复的图实现
"""

import asyncio
import json
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any

from .core import BaseNode, Graph, NodeStatus
from .executor import ExecutionContext, GraphExecutor


class GraphSnapshot:
    """图执行快照

    保存图执行的完整状态，支持恢复
    """

    def __init__(self, graph_id: str):
        """初始化快照"""
        self.graph_id = graph_id
        self.timestamp = datetime.now().isoformat()
        self.graph_structure: dict[str, Any] = {}
        self.execution_state: dict[str, Any] = {}
        self.node_states: dict[str, dict[str, Any]] = {}
        self.context_data: dict[str, Any] = {}

    def capture_graph(self, graph: "EnhancedGraph"):
        """捕获图结构"""
        self.graph_structure = {
            "name": graph.name,
            "nodes": {
                node_id: {
                    "type": node.__class__.__name__,
                    "name": node.name,
                    "status": node.status.value,
                }
                for node_id, node in graph.nodes.items()
            },
            "edges": [
                {"from": edge.from_id, "to": edge.to_id, "condition": edge.action}
                for edges_dict in graph.edges.values()
                for edge in edges_dict.values()
            ],
            "start_node": graph.start_node_id,
            "end_nodes": list(graph.end_node_ids),
        }

    def capture_execution(self, executor: GraphExecutor):
        """捕获执行状态"""
        if executor.context:
            self.execution_state = {
                "current_node": executor.context.current_node,
                "visited_nodes": list(executor.context.visited_nodes),
                "node_outputs": dict(executor.context.node_outputs),
                "graph_input": executor.context.graph_input,
                "start_time": executor.context.start_time.isoformat()
                if executor.context.start_time
                else None,
                "status": "running" if not executor.context.end_time else "completed",
            }

    def capture_node_states(self, graph: "EnhancedGraph"):
        """捕获节点状态"""
        for node_id, node in graph.nodes.items():
            self.node_states[node_id] = {
                "status": node.status.value,
                "result": getattr(node, "result", None),
                "_input_data": getattr(node, "_input_data", None),
                # 保存其他重要的节点状态
                "custom_state": self._extract_custom_state(node),
            }

    def _extract_custom_state(self, node: BaseNode) -> dict[str, Any]:
        """提取节点的自定义状态"""
        custom_state = {}

        # 保存特定类型节点的状态
        if hasattr(node, "conversation_history"):
            custom_state["conversation_history"] = getattr(node, "conversation_history")
        if hasattr(node, "retry_count"):
            custom_state["retry_count"] = getattr(node, "retry_count")
        if hasattr(node, "circuit_state"):
            custom_state["circuit_state"] = getattr(node, "circuit_state")

        return custom_state

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "graph_id": self.graph_id,
            "timestamp": self.timestamp,
            "graph_structure": self.graph_structure,
            "execution_state": self.execution_state,
            "node_states": self.node_states,
            "context_data": self.context_data,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GraphSnapshot":
        """从字典创建快照"""
        snapshot = cls(data["graph_id"])
        snapshot.timestamp = data["timestamp"]
        snapshot.graph_structure = data["graph_structure"]
        snapshot.execution_state = data["execution_state"]
        snapshot.node_states = data["node_states"]
        snapshot.context_data = data.get("context_data", {})
        return snapshot


class EnhancedGraph(Graph):
    """增强图

    支持序列化和中断恢复的图
    """

    def __init__(self, name: str = "enhanced_graph"):
        """初始化增强图"""
        super().__init__(name)
        self.checkpoints: list[GraphSnapshot] = []
        self.is_resumable = True
        self.auto_checkpoint = True
        self.checkpoint_interval = 5  # 每5个节点自动保存

    def create_snapshot(self) -> GraphSnapshot:
        """创建当前状态的快照"""
        snapshot = GraphSnapshot(self.name)
        snapshot.capture_graph(self)
        return snapshot

    def save_snapshot(self, snapshot: GraphSnapshot, filepath: Path | None = None):
        """保存快照到文件"""
        if filepath is None:
            filepath = Path(f"{self.name}_snapshot_{snapshot.timestamp}.json")

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(snapshot.to_dict(), f, indent=2, ensure_ascii=False)

    def load_snapshot(self, filepath: Path) -> GraphSnapshot:
        """从文件加载快照"""
        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)
        return GraphSnapshot.from_dict(data)

    def serialize(self) -> dict[str, Any]:
        """序列化图结构"""
        return {
            "name": self.name,
            "nodes": {
                node_id: self._serialize_node(node)
                for node_id, node in self.nodes.items()
            },
            "edges": [
                {"from": edge.from_id, "to": edge.to_id, "condition": edge.action}
                for edges_dict in self.edges.values()
                for edge in edges_dict.values()
            ],
            "start_node": self.start_node_id,
            "end_nodes": list(self.end_node_ids),
            "metadata": {
                "is_resumable": self.is_resumable,
                "auto_checkpoint": self.auto_checkpoint,
                "checkpoint_interval": self.checkpoint_interval,
            },
        }

    def _serialize_node(self, node: BaseNode) -> dict[str, Any]:
        """序列化节点"""
        node_data = {
            "type": node.__class__.__name__,
            "module": node.__class__.__module__,
            "name": node.name,
            "status": node.status.value,
            "config": {},
        }

        # 保存节点配置
        if hasattr(node, "process_func"):
            node_data["config"]["has_process_func"] = True
        if hasattr(node, "condition_func"):
            node_data["config"]["has_condition_func"] = True
        if hasattr(node, "agent"):
            node_data["config"]["has_agent"] = True

        return node_data

    @classmethod
    def deserialize(
        cls, data: dict[str, Any], node_factory: dict[str, type] | None = None
    ) -> "EnhancedGraph":
        """反序列化图结构

        Args:
            data: 序列化的图数据
            node_factory: 节点类型映射字典

        Returns:
            重建的图
        """
        graph = cls(data["name"])

        # 恢复元数据
        metadata = data.get("metadata", {})
        graph.is_resumable = metadata.get("is_resumable", True)
        graph.auto_checkpoint = metadata.get("auto_checkpoint", True)
        graph.checkpoint_interval = metadata.get("checkpoint_interval", 5)

        # 恢复节点（需要节点工厂）
        if node_factory:
            for node_id, node_data in data["nodes"].items():
                node_type = node_data["type"]
                if node_type in node_factory:
                    # 创建节点实例
                    node_class = node_factory[node_type]
                    node = node_class(node_id, node_data["name"])
                    graph.add_node(node)

        # 恢复边
        for edge_data in data["edges"]:
            graph.add_edge(
                edge_data["from"], edge_data["to"], edge_data.get("condition")
            )

        # 恢复起始和结束节点
        if data.get("start_node"):
            graph.set_start(data["start_node"])
        for end_node in data.get("end_nodes", []):
            graph.add_end(end_node)

        return graph


class ResumableExecutor(GraphExecutor):
    """可恢复的图执行器

    支持中断和恢复执行，并添加钩子机制
    """

    def __init__(self, graph: EnhancedGraph):
        """初始化可恢复执行器"""
        super().__init__(graph)
        self.graph: EnhancedGraph = graph
        self.snapshots: list[GraphSnapshot] = []
        self.is_paused = False
        self.checkpoint_counter = 0

        # 钩子机制
        self._on_node_start_hooks: list[Callable] = []
        self._on_node_complete_hooks: list[Callable] = []
        self._on_node_error_hooks: list[Callable] = []
        self._on_graph_complete_hooks: list[Callable] = []

    async def execute_with_checkpoints(
        self,
        initial_input: Any | None = None,
        start_node_id: str | None = None,
        checkpoint_callback: Callable | None = None,
    ) -> ExecutionContext:
        """带检查点的执行

        Args:
            initial_input: 初始输入
            start_node_id: 起始节点ID
            checkpoint_callback: 检查点回调函数

        Returns:
            执行上下文
        """
        # 初始化执行
        self.context = ExecutionContext()
        self.context.graph_input = initial_input

        # 创建初始快照
        if self.graph.auto_checkpoint:
            snapshot = self._create_checkpoint("initial")
            if checkpoint_callback:
                checkpoint_callback(snapshot)

        # 执行图
        try:
            result = await self.execute(initial_input, start_node_id)

            # 创建最终快照
            if self.graph.auto_checkpoint:
                snapshot = self._create_checkpoint("final")
                if checkpoint_callback:
                    checkpoint_callback(snapshot)

            return result

        except Exception as e:
            # 发生异常时保存快照
            snapshot = self._create_checkpoint("error")
            snapshot.context_data["error"] = str(e)
            if checkpoint_callback:
                checkpoint_callback(snapshot)
            raise

    def _create_checkpoint(self, checkpoint_type: str = "auto") -> GraphSnapshot:
        """创建检查点"""
        snapshot = self.graph.create_snapshot()
        snapshot.capture_execution(self)
        snapshot.capture_node_states(self.graph)
        snapshot.context_data["checkpoint_type"] = checkpoint_type
        snapshot.context_data["checkpoint_number"] = self.checkpoint_counter

        self.snapshots.append(snapshot)
        self.checkpoint_counter += 1

        return snapshot

    async def resume_from_snapshot(self, snapshot: GraphSnapshot) -> ExecutionContext:
        """从快照恢复执行

        Args:
            snapshot: 要恢复的快照

        Returns:
            执行上下文
        """
        # 恢复执行上下文
        self.context = ExecutionContext()
        exec_state = snapshot.execution_state

        self.context.current_node = exec_state.get("current_node")
        self.context.visited_nodes = set(exec_state.get("visited_nodes", []))
        self.context.node_outputs = exec_state.get("node_outputs", {})
        self.context.graph_input = exec_state.get("graph_input")

        # 恢复节点状态
        for node_id, node_state in snapshot.node_states.items():
            if node_id in self.graph.nodes:
                node = self.graph.nodes[node_id]
                node.status = NodeStatus(node_state["status"])
                if node_state.get("result") is not None:
                    node.result = node_state["result"]
                if node_state.get("_input_data") is not None:
                    node._input_data = node_state["_input_data"]

                # 恢复自定义状态
                custom_state = node_state.get("custom_state", {})
                for key, value in custom_state.items():
                    if hasattr(node, key):
                        setattr(node, key, value)

        # 继续执行
        if self.context.current_node:
            # 从当前节点继续
            return await self._continue_execution_from(self.context.current_node)
        else:
            # 从头开始
            return await self.execute(self.context.graph_input)

    async def _continue_execution_from(self, node_id: str) -> ExecutionContext:
        """从指定节点继续执行"""
        # 获取当前节点
        current_node = self.graph.nodes.get(node_id)
        if not current_node:
            raise ValueError(f"Node {node_id} not found in graph")

        # 如果节点未完成，先执行它
        if current_node.status != NodeStatus.SUCCESS:
            await self._execute_node(current_node)

        # 继续执行后续节点
        # 使用执行队列机制
        execution_queue = [node_id]

        while execution_queue and not self.is_paused:
            current_id = execution_queue.pop(0)
            current = self.graph.nodes.get(current_id)

            if not current or current.status == NodeStatus.SUCCESS:
                continue

            # 执行节点
            await self._execute_node(current)

            # 获取下一个节点
            next_node_id = await current.post()

            # 处理特殊控制标记
            if next_node_id == "__fork__":
                # 处理分叉
                edges = self.graph.get_outgoing_edges(current_id)
                execution_queue.extend([e.to_node for e in edges])
            elif next_node_id == "__waiting__":
                # 节点正在等待，重新加入队列
                execution_queue.append(current_id)
            elif next_node_id == "__exit__":
                # 退出执行
                break
            elif next_node_id:
                # 普通节点
                execution_queue.append(next_node_id)
            else:
                # 默认继续执行下一个
                edges = self.graph.get_outgoing_edges(current_id)
                if edges:
                    execution_queue.append(edges[0].to_node)

            # 创建检查点
            if (
                self.graph.auto_checkpoint
                and len(self.context.visited_nodes) % self.graph.checkpoint_interval
                == 0
            ):
                self._create_checkpoint("auto")

        return self.context

    def pause(self):
        """暂停执行"""
        self.is_paused = True

    def resume(self):
        """恢复执行"""
        self.is_paused = False

    def register_hook(self, event: str, callback: Callable):
        """注册钩子函数

        Args:
            event: 事件类型 (node_start, node_complete, node_error, graph_complete)
            callback: 回调函数
        """
        if event == "node_start":
            self._on_node_start_hooks.append(callback)
        elif event == "node_complete":
            self._on_node_complete_hooks.append(callback)
        elif event == "node_error":
            self._on_node_error_hooks.append(callback)
        elif event == "graph_complete":
            self._on_graph_complete_hooks.append(callback)

    async def _execute_node(self, node_id: str, input_data: Any) -> None:
        """执行单个节点（增强版）"""
        # 获取节点
        node = self.graph.nodes.get(node_id)
        if not node:
            raise ValueError(f"Node {node_id} not found")

        # 节点开始执行钩子
        for hook in self._on_node_start_hooks:
            await self._call_hook(hook, node)

        try:
            # 调用父类的执行方法
            await super()._execute_node(node_id, input_data)

            # 节点完成钩子
            for hook in self._on_node_complete_hooks:
                await self._call_hook(hook, node)

        except Exception as e:
            # 节点错误钩子
            for hook in self._on_node_error_hooks:
                await self._call_hook(hook, node, e)
            raise

    async def _call_hook(self, hook: Callable, *args, **kwargs):
        """调用钩子函数"""
        if asyncio.iscoroutinefunction(hook):
            await hook(*args, **kwargs)
        else:
            hook(*args, **kwargs)

