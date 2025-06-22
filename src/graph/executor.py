"""
图执行器实现

负责图的遍历和节点的执行
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
        self.data: dict[str, Any] = {}  # 共享数据存储
        self.execution_history: list[dict[str, Any]] = []  # 执行历史
        self.start_time = datetime.now()
        self.end_time = None

    def set(self, key: str, value: Any):
        """设置共享数据"""
        self.data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """获取共享数据"""
        return self.data.get(key, default)

    def add_execution(
        self, node_id: str, result: Any, action: str, error: str | None = None
    ):
        """记录节点执行信息"""
        self.execution_history.append(
            {
                "node_id": node_id,
                "timestamp": datetime.now(),
                "result": result,
                "action": action,
                "error": error,
            }
        )

    def finish(self):
        """标记执行结束"""
        self.end_time = datetime.now()

    @property
    def duration(self):
        """获取执行时长（秒）"""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return (datetime.now() - self.start_time).total_seconds()


class GraphExecutor:
    """
    图执行器

    负责遍历图并执行节点
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

    async def execute(self, start_node_id: str | None = None) -> ExecutionContext:
        """
        执行图

        Args:
            start_node_id: 起始节点ID，如果不指定则使用图的默认起始节点

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

        self.current_node_id = start_id
        iterations = 0

        try:
            while self.current_node_id and iterations < self.max_iterations:
                node = self.graph.get_node(self.current_node_id)
                if not node:
                    raise ValueError(f"节点 {self.current_node_id} 不存在")

                # 执行前钩子
                await self._run_hooks("before_node", node=node, context=self.context)

                try:
                    logger.info(f"执行节点: {self.current_node_id}")
                    action = await node.run()

                    # 记录执行结果
                    self.context.add_execution(
                        node_id=self.current_node_id, result=node.result, action=action
                    )

                    # 执行后钩子
                    await self._run_hooks(
                        "after_node", node=node, action=action, context=self.context
                    )

                    # 获取下一个节点
                    next_node_id = self.graph.get_next_node_id(
                        self.current_node_id, action
                    )

                    if next_node_id:
                        logger.info(
                            f"从 {self.current_node_id} 转移到 {next_node_id}，动作: '{action}'"
                        )
                        self.current_node_id = next_node_id
                    else:
                        logger.info(
                            f"没有找到动作 '{action}' 对应的下一个节点，执行结束"
                        )
                        self.current_node_id = None

                except Exception as e:
                    logger.error(f"执行节点 {self.current_node_id} 时出错: {str(e)}")
                    if self.current_node_id:
                        self.context.add_execution(
                            node_id=self.current_node_id,
                            result=None,
                            action="error",
                            error=str(e),
                        )

                    # 错误钩子
                    await self._run_hooks(
                        "on_error", node=node, error=e, context=self.context
                    )
                    raise

                iterations += 1

            if iterations >= self.max_iterations:
                logger.warning(f"达到最大迭代次数 ({self.max_iterations})")

            self.context.finish()

            # 完成钩子
            await self._run_hooks("on_complete", context=self.context)

        except Exception:
            self.context.finish()
            raise

        return self.context

    async def execute_parallel_branches(
        self, start_node_ids: list[str]
    ) -> dict[str, ExecutionContext | None]:
        """
        并行执行多个分支

        Args:
            start_node_ids: 起始节点ID列表

        Returns:
            节点ID到执行上下文的映射
        """
        tasks = []
        for node_id in start_node_ids:
            executor = GraphExecutor(self.graph, self.max_iterations)
            tasks.append(executor.execute(node_id))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        return {
            node_id: result if not isinstance(result, Exception) else None
            for node_id, result in zip(start_node_ids, results)
        }

    def reset(self):
        """重置执行器状态"""
        # 重置所有节点状态
        for node in self.graph.nodes.values():
            node.reset()

        # 重置执行上下文
        self.context = ExecutionContext()
        self.current_node_id = None


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

    async def execute(self, start_node_id: str | None = None) -> ExecutionContext:
        """执行图，支持条件跳过"""
        start_id = start_node_id or self.graph.start_node_id
        if not start_id:
            raise ValueError("未指定起始节点")

        self.current_node_id = start_id
        iterations = 0

        try:
            while self.current_node_id and iterations < self.max_iterations:
                node = self.graph.get_node(self.current_node_id)
                if not node:
                    raise ValueError(f"节点 {self.current_node_id} 不存在")

                # 检查节点条件
                condition_name = node.metadata.get("condition")
                if condition_name:
                    should_execute = await self.evaluate_condition(condition_name, node)
                    if not should_execute:
                        logger.info(
                            f"由于条件 {condition_name} 不满足，跳过节点 {self.current_node_id}"
                        )
                        node.status = NodeStatus.SKIPPED

                        # 寻找跳过时的下一个节点
                        skip_next = self.graph.get_next_node_id(
                            self.current_node_id, "skip"
                        )
                        if not skip_next:
                            skip_next = self.graph.get_next_node_id(
                                self.current_node_id, "default"
                            )

                        self.current_node_id = skip_next
                        iterations += 1
                        continue

                # 正常执行节点
                await self._run_hooks("before_node", node=node, context=self.context)

                try:
                    action = await node.run()
                    self.context.add_execution(
                        node_id=self.current_node_id, result=node.result, action=action
                    )
                    await self._run_hooks(
                        "after_node", node=node, action=action, context=self.context
                    )

                    next_node_id = self.graph.get_next_node_id(
                        self.current_node_id, action
                    )
                    self.current_node_id = next_node_id

                except Exception as e:
                    logger.error(f"执行节点 {self.current_node_id} 时出错: {str(e)}")
                    if self.current_node_id:
                        self.context.add_execution(
                            node_id=self.current_node_id,
                            result=None,
                            action="error",
                            error=str(e),
                        )
                    await self._run_hooks(
                        "on_error", node=node, error=e, context=self.context
                    )

                    # 尝试错误处理路径
                    error_next = None
                    if self.current_node_id:
                        error_next = self.graph.get_next_node_id(
                            self.current_node_id, "error"
                        )
                    if error_next:
                        self.current_node_id = error_next
                    else:
                        raise

                iterations += 1

            self.context.finish()
            await self._run_hooks("on_complete", context=self.context)

        except Exception:
            self.context.finish()
            raise

        return self.context
