"""
图执行器实现

负责图的遍历和节点的执行，确保上一个节点的输出作为下一个节点的输入
"""

import asyncio
import logging
from collections.abc import Callable
from datetime import datetime
from typing import Any

from .core import BaseNode, Graph, NodeStatus

logger = logging.getLogger(__name__)


class ExecutionContext:
    """
    执行上下文

    在图执行过程中维护状态和数据
    """

    def __init__(self):
        """初始化执行上下文"""
        # 共享数据存储
        self.data: dict[str, Any] = {}

        # 执行历史
        self.execution_history: list[dict[str, Any]] = []
        self.current_path: list[str] = []  # 当前执行路径

        # 时间信息
        self.start_time = datetime.now()
        self.end_time = None

        # 节点输入输出记录
        self.node_inputs: dict[str, Any] = {}  # 记录每个节点的输入
        self.node_outputs: dict[str, Any] = {}  # 记录每个节点的输出

    def set(self, key: str, value: Any):
        """设置共享数据"""
        self.data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """获取共享数据"""
        return self.data.get(key, default)

    def add_execution(
        self,
        node_id: str,
        input_data: Any = None,
        result: Any = None,
        action: str = "default",
        error: str | None = None,
    ):
        """记录节点执行信息"""
        self.execution_history.append(
            {
                "node_id": node_id,
                "timestamp": datetime.now(),
                "input": input_data,
                "result": result,
                "action": action,
                "error": error,
            }
        )

        # 记录输入输出
        if input_data is not None:
            self.node_inputs[node_id] = input_data
        if result is not None:
            self.node_outputs[node_id] = result

    def get_node_output(self, node_id: str) -> Any:
        """获取指定节点的输出"""
        return self.node_outputs.get(node_id)

    def finish(self):
        """标记执行结束"""
        self.end_time = datetime.now()

    @property
    def duration(self):
        """获取执行时长（秒）"""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return (datetime.now() - self.start_time).total_seconds()
    
    @property
    def graph_output(self):
        """获取图的最终输出
        
        返回最后执行的节点的输出
        """
        if not self.execution_history:
            return None
            
        # 找到最后一个成功执行的节点
        for exec_record in reversed(self.execution_history):
            if exec_record.get("result") is not None and exec_record.get("error") is None:
                return exec_record["result"]
                
        return None


class GraphExecutor:
    """
    图执行器

    负责遍历图并执行节点，支持原子化控制流节点
    """

    def __init__(self, graph: Graph, max_iterations: int = 100):
        """
        初始化执行器

        Args:
            graph: 要执行的图
            max_iterations: 最大迭代次数，防止无限循环
        """
        self.graph = graph
        self.max_iterations = max_iterations
        self.current_node_id: str | None = None
        self.context = ExecutionContext()
        self.hooks: dict[str, list[Callable]] = {
            "before_node": [],  # 节点执行前
            "after_node": [],  # 节点执行后
            "on_error": [],  # 出错时
            "on_complete": [],  # 执行完成时
        }
        # 用于跟踪并行执行和汇聚节点
        self.active_nodes: set[str] = set()  # 当前活跃的节点
        self.execution_queue: list[
            tuple[str, Any]
        ] = []  # 执行队列：(node_id, input_data)
        self.join_node_states: dict[str, dict[str, Any]] = {}  # 汇聚节点状态

    def add_hook(self, event: str, callback: Callable):
        """
        添加钩子函数

        Args:
            event: 事件名称
            callback: 回调函数
        """
        if event in self.hooks:
            self.hooks[event].append(callback)

    async def _run_hooks(self, event: str, **kwargs):
        """运行指定事件的所有钩子"""
        for callback in self.hooks.get(event, []):
            if asyncio.iscoroutinefunction(callback):
                await callback(**kwargs)
            else:
                callback(**kwargs)

    async def execute(
        self, start_node_id: str | None = None, initial_input: Any = None
    ) -> ExecutionContext:
        """
        执行图，支持原子化控制流节点

        Args:
            start_node_id: 起始节点ID，如果不指定则使用图的默认起始节点
            initial_input: 初始输入数据

        Returns:
            执行上下文
        """
        # 确定起始节点
        start_id = start_node_id or self.graph.start_node_id
        if not start_id:
            raise ValueError("未指定起始节点")

        if start_id not in self.graph.nodes:
            raise ValueError(f"起始节点 {start_id} 不存在")

        # 验证图结构
        valid, errors = self.graph.validate()
        if not valid:
            logger.warning(f"图验证失败: {errors}")

        # 初始化执行队列
        self.execution_queue = [(start_id, initial_input)]
        iterations = 0

        try:
            while self.execution_queue and iterations < self.max_iterations:
                # 获取下一个要执行的节点
                node_id, input_data = self.execution_queue.pop(0)

                # 执行节点
                await self._execute_node(node_id, input_data)

                iterations += 1

            if iterations >= self.max_iterations:
                logger.warning(f"达到最大迭代次数 ({self.max_iterations})")

            self.context.finish()
            await self._run_hooks("on_complete", context=self.context)

        except Exception:
            self.context.finish()
            raise

        return self.context

    async def _execute_node(self, node_id: str, input_data: Any) -> None:
        """
        执行单个节点

        Args:
            node_id: 节点ID
            input_data: 输入数据（来自上一个节点的输出）
        """
        node = self.graph.get_node(node_id)
        if not node:
            raise ValueError(f"节点 {node_id} 不存在")

        # 记录当前执行路径
        self.context.current_path.append(node_id)

        # 执行前钩子
        await self._run_hooks("before_node", node=node, context=self.context)

        try:
            logger.info(f"执行节点: {node_id}，输入: {input_data}")

            # 执行节点
            output_data = await self._call_node_with_input(node, input_data)

            # 提取动作
            action = self._extract_action(output_data)

            # 记录执行结果
            self.context.add_execution(
                node_id=node_id,
                input_data=input_data,
                result=output_data,
                action=action,
            )

            # 执行后钩子
            await self._run_hooks(
                "after_node", node=node, action=action, context=self.context
            )

            # 处理节点输出
            await self._process_node_output(node_id, output_data, action)

        except Exception as e:
            logger.error(f"执行节点 {node_id} 时出错: {str(e)}")
            self.context.add_execution(
                node_id=node_id,
                input_data=input_data,
                result=None,
                action="error",
                error=str(e),
            )
            await self._run_hooks("on_error", node=node, error=e, context=self.context)

            # 尝试错误处理路径
            error_next = self.graph.get_next_node_id(node_id, "error")
            if error_next:
                self.execution_queue.append(
                    (error_next, {"error": str(e), "from_node": node_id})
                )
            else:
                raise

        finally:
            # 从当前路径中移除
            if self.context.current_path and self.context.current_path[-1] == node_id:
                self.context.current_path.pop()

    async def _call_node_with_input(self, node: BaseNode, input_data: Any) -> Any:
        """调用节点并传递输入数据"""
        # 设置输入数据并运行
        node._input_data = input_data
        await node.run()
        return node.result

    def _extract_action(self, result: Any) -> str:
        """从结果中提取动作"""
        if isinstance(result, dict):
            if "action" in result:
                return result["action"]
            elif "__fork__" in result:
                return "fork"
            elif "__waiting__" in result:
                return "waiting"
        return "default"

    async def _process_node_output(self, node_id: str, output_data: Any, action: str):
        """
        处理节点输出，确保输出作为下一个节点的输入
        """
        # 处理分叉节点
        if isinstance(output_data, dict) and output_data.get("__fork__"):
            # 获取实际数据
            actual_data = output_data.get("data", output_data)

            # 获取所有下游节点
            outgoing_edges = self.graph.get_outgoing_edges(node_id)
            for edge in outgoing_edges:
                # 将当前节点的输出作为下游节点的输入
                self.execution_queue.append((edge.to_id, actual_data))

            logger.info(f"分叉节点 {node_id} 激活了 {len(outgoing_edges)} 个下游节点")
            return

        # 处理汇聚节点的等待状态
        if isinstance(output_data, dict) and output_data.get("__waiting__"):
            # 节点还在等待更多输入，暂时不激活下游节点
            logger.info(f"节点 {node_id} 正在等待更多输入")
            return

        # 提取实际数据（处理BranchNode的输出格式）
        if (
            isinstance(output_data, dict)
            and "data" in output_data
            and "action" in output_data
        ):
            actual_data = output_data["data"]
        else:
            actual_data = output_data

        # 普通节点，根据动作获取下一个节点
        next_node_id = self.graph.get_next_node_id(node_id, action)
        if next_node_id:
            logger.info(f"从 {node_id} 转移到 {next_node_id}，动作: '{action}'")

            # 检查是否是汇聚节点
            next_node = self.graph.get_node(next_node_id)
            if hasattr(next_node, "join_inputs"):  # JoinControlNode
                # 处理汇聚节点
                await self._handle_join_node(next_node_id, node_id, actual_data)
            else:
                # 将当前节点的输出作为下一个节点的输入
                self.execution_queue.append((next_node_id, actual_data))

    async def _handle_join_node(self, join_node_id: str, from_node_id: str, data: Any):
        """处理汇聚节点的输入"""
        # 初始化汇聚节点状态
        if join_node_id not in self.join_node_states:
            self.join_node_states[join_node_id] = {"inputs": {}, "received_from": set()}

        state = self.join_node_states[join_node_id]

        # 记录输入
        state["inputs"][from_node_id] = data
        state["received_from"].add(from_node_id)

        # 获取所有上游节点
        incoming_edges = self.graph.get_incoming_edges(join_node_id)
        expected_count = len(incoming_edges)

        # 检查是否收到所有输入
        if len(state["received_from"]) >= expected_count:
            # 准备汇聚的输入数据
            join_input_data = list(state["inputs"].values())

            # 将汇聚的数据作为输入
            self.execution_queue.append((join_node_id, join_input_data))

            # 清理状态
            del self.join_node_states[join_node_id]

            logger.info(f"汇聚节点 {join_node_id} 收到所有 {expected_count} 个输入")

    def reset(self):
        """重置执行器状态"""
        # 重置所有节点状态
        for node in self.graph.nodes.values():
            node.reset()

        # 重置执行上下文
        self.context = ExecutionContext()
        self.current_node_id = None
        self.active_nodes.clear()
        self.execution_queue.clear()
        self.join_node_states.clear()


class ConditionalExecutor(GraphExecutor):
    """
    条件执行器

    支持基于条件跳过节点的执行
    """

    def __init__(
        self, graph: Graph, conditions: dict[str, Callable], max_iterations: int = 100
    ):
        """
        初始化条件执行器

        Args:
            graph: 要执行的图
            conditions: 条件函数字典
            max_iterations: 最大迭代次数
        """
        super().__init__(graph, max_iterations)
        self.conditions = conditions

    async def evaluate_condition(self, condition_name: str, node: BaseNode) -> bool:
        """
        评估条件

        Args:
            condition_name: 条件名称
            node: 当前节点

        Returns:
            条件是否满足
        """
        condition_func = self.conditions.get(condition_name)
        if not condition_func:
            return True

        if asyncio.iscoroutinefunction(condition_func):
            return await condition_func(node, self.context)
        else:
            return condition_func(node, self.context)

    async def _execute_node(self, node_id: str, input_data: Any) -> None:
        """执行节点，支持条件跳过"""
        node = self.graph.get_node(node_id)
        if not node:
            raise ValueError(f"节点 {node_id} 不存在")

        # 检查节点条件
        condition_name = node.metadata.get("condition")
        if condition_name:
            should_execute = await self.evaluate_condition(condition_name, node)
            if not should_execute:
                logger.info(f"由于条件 {condition_name} 不满足，跳过节点 {node_id}")
                node.status = NodeStatus.SKIPPED

                # 寻找跳过时的下一个节点
                skip_next = self.graph.get_next_node_id(node_id, "skip")
                if not skip_next:
                    skip_next = self.graph.get_next_node_id(node_id, "default")

                if skip_next:
                    self.execution_queue.append((skip_next, input_data))
                return

        # 正常执行节点
        await super()._execute_node(node_id, input_data)
