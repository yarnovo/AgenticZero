"""
复合节点实现

复合节点是基于原子节点构建的高级功能节点，内部包含多个原子节点组合，
对外表现为一个完整的功能单元。

分为两大类：
1. 控制流类：条件分支、循环控制等
2. 并行控制类：并行执行、竞态执行等
"""

import asyncio
from collections.abc import Callable, Iterable
from typing import Any

from .atomic_nodes import BranchNode, ForkNode, JoinNode, MergeNode, SequenceNode
from .core import BaseNode, Graph
from .executor import GraphExecutor


class CompositeNodeBase(BaseNode):
    """复合节点基类

    复合节点内部维护一个子图，执行时运行整个子图
    """

    def __init__(self, node_id: str, name: str | None = None, **kwargs):
        """初始化复合节点"""
        super().__init__(node_id, name, **kwargs)
        self.sub_graph = Graph(f"{node_id}_subgraph")
        self.sub_executor = None
        self._setup_sub_graph()

    def _setup_sub_graph(self):
        """设置子图结构，子类必须实现"""
        raise NotImplementedError("子类必须实现_setup_sub_graph方法")

    async def prep(self) -> None:
        """准备阶段"""
        self.sub_executor = GraphExecutor(self.sub_graph)

    async def exec(self) -> Any:
        """执行子图"""
        if self.sub_executor is None:
            raise RuntimeError("子执行器未初始化，请先调用prep()方法")
        
        context = await self.sub_executor.execute(initial_input=self._input_data)
        # 获取子图最后一个节点（结束节点）的输出
        end_nodes = list(self.sub_graph.end_node_ids)
        if end_nodes:
            return context.node_outputs.get(end_nodes[0])
        # 如果没有结束节点，返回起始节点的输出
        if self.sub_graph.start_node_id:
            return context.node_outputs.get(self.sub_graph.start_node_id)
        return None

    async def post(self) -> str:
        """后处理阶段"""
        return "default"


# ==================== 控制流类复合节点 ====================


class IfElseNode(CompositeNodeBase):
    """If-Else条件分支复合节点

    根据条件执行不同的分支逻辑
    """

    def __init__(
        self,
        node_id: str,
        name: str | None = None,
        condition_func: Callable[[Any], bool] | None = None,
        if_func: Callable[[Any], Any] | None = None,
        else_func: Callable[[Any], Any] | None = None,
        **kwargs,
    ):
        """初始化If-Else节点

        Args:
            node_id: 节点ID
            name: 节点名称
            condition_func: 条件判断函数
            if_func: True分支处理函数
            else_func: False分支处理函数
        """
        self.condition_func = condition_func or (lambda x: True)
        self.if_func = if_func or (lambda x: x)
        self.else_func = else_func or (lambda x: None)
        super().__init__(node_id, name, **kwargs)

    def _setup_sub_graph(self):
        """设置If-Else子图"""
        # 分支节点
        branch = BranchNode(
            "branch",
            "条件判断",
            lambda x: "true" if self.condition_func(x) else "false",
        )

        # 处理节点
        if_node = SequenceNode("if_branch", "True分支", self.if_func)
        else_node = SequenceNode("else_branch", "False分支", self.else_func)

        # 合并节点
        merge = MergeNode("merge", "结果合并")

        # 添加节点
        self.sub_graph.add_node(branch)
        self.sub_graph.add_node(if_node)
        self.sub_graph.add_node(else_node)
        self.sub_graph.add_node(merge)

        # 连接边
        self.sub_graph.add_edge("branch", "if_branch", "true")
        self.sub_graph.add_edge("branch", "else_branch", "false")
        self.sub_graph.add_edge("if_branch", "merge")
        self.sub_graph.add_edge("else_branch", "merge")

        # 设置起始和结束节点
        self.sub_graph.set_start("branch")
        self.sub_graph.add_end("merge")


class SwitchNode(CompositeNodeBase):
    """Switch多路分支复合节点

    根据选择器值执行对应的分支
    """

    def __init__(
        self,
        node_id: str,
        name: str | None = None,
        selector_func: Callable[[Any], str] | None = None,
        cases: dict[str, Callable[[Any], Any]] | None = None,
        default_func: Callable[[Any], Any] | None = None,
        **kwargs,
    ):
        """初始化Switch节点

        Args:
            node_id: 节点ID
            name: 节点名称
            selector_func: 选择器函数，返回case名称
            cases: case分支字典 {case_name: handler_func}
            default_func: 默认分支处理函数
        """
        self.selector_func = selector_func or (lambda x: "default")
        self.cases = cases or {}
        self.default_func = default_func or (lambda x: x)
        super().__init__(node_id, name, **kwargs)

    def _setup_sub_graph(self):
        """设置Switch子图"""

        # 包装选择器函数，确保返回有效的分支名称
        def wrapped_selector(x):
            result = self.selector_func(x)
            return result if result in self.cases else "default"

        # 分支节点
        branch = BranchNode("branch", "选择器", wrapped_selector)

        # 合并节点
        merge = MergeNode("merge", "结果合并")

        # 添加分支和合并节点
        self.sub_graph.add_node(branch)
        self.sub_graph.add_node(merge)

        # 为每个case创建处理节点
        for case_name, case_func in self.cases.items():
            case_node = SequenceNode(
                f"case_{case_name}", f"Case {case_name}", case_func
            )
            self.sub_graph.add_node(case_node)
            self.sub_graph.add_edge("branch", f"case_{case_name}", case_name)
            self.sub_graph.add_edge(f"case_{case_name}", "merge")

        # 默认分支
        default_node = SequenceNode("default_case", "默认分支", self.default_func)
        self.sub_graph.add_node(default_node)
        self.sub_graph.add_edge("branch", "default_case", "default")
        self.sub_graph.add_edge("default_case", "merge")

        # 设置起始和结束节点
        self.sub_graph.set_start("branch")
        self.sub_graph.add_end("merge")


class WhileNode(CompositeNodeBase):
    """While循环复合节点

    前置条件循环，先检查条件，满足则执行循环体
    """

    def __init__(
        self,
        node_id: str,
        name: str | None = None,
        condition_func: Callable[[Any], bool] | None = None,
        body_func: Callable[[Any], Any] | None = None,
        max_iterations: int = 100,
        **kwargs,
    ):
        """初始化While节点

        Args:
            node_id: 节点ID
            name: 节点名称
            condition_func: 循环条件函数
            body_func: 循环体函数
            max_iterations: 最大迭代次数，防止无限循环
        """
        self.condition_func = condition_func or (lambda x: False)
        self.body_func = body_func or (lambda x: x)
        self.max_iterations = max_iterations
        super().__init__(node_id, name, **kwargs)

    async def exec(self) -> Any:
        """执行While循环"""
        current_data = self._input_data
        iterations = 0

        while iterations < self.max_iterations and self.condition_func(current_data):
            current_data = self.body_func(current_data)
            iterations += 1

        return {
            "result": current_data,
            "iterations": iterations,
            "max_reached": iterations >= self.max_iterations,
        }

    def _setup_sub_graph(self):
        """While节点不使用子图，直接在exec中实现"""
        pass


class DoWhileNode(CompositeNodeBase):
    """Do-While循环复合节点

    后置条件循环，先执行循环体，再检查条件
    """

    def __init__(
        self,
        node_id: str,
        name: str | None = None,
        condition_func: Callable[[Any], bool] | None = None,
        body_func: Callable[[Any], Any] | None = None,
        max_iterations: int = 100,
        **kwargs,
    ):
        """初始化Do-While节点"""
        self.condition_func = condition_func or (lambda x: False)
        self.body_func = body_func or (lambda x: x)
        self.max_iterations = max_iterations
        super().__init__(node_id, name, **kwargs)

    async def exec(self) -> Any:
        """执行Do-While循环"""
        current_data = self._input_data
        iterations = 0

        # 至少执行一次
        current_data = self.body_func(current_data)
        iterations += 1

        # 继续循环直到条件不满足
        while iterations < self.max_iterations and self.condition_func(current_data):
            current_data = self.body_func(current_data)
            iterations += 1

        return {
            "result": current_data,
            "iterations": iterations,
            "max_reached": iterations >= self.max_iterations,
        }

    def _setup_sub_graph(self):
        """Do-While节点不使用子图，直接在exec中实现"""
        pass


class ForNode(CompositeNodeBase):
    """For计数循环复合节点

    指定次数的循环执行
    """

    def __init__(
        self,
        node_id: str,
        name: str | None = None,
        count: int = 1,
        body_func: Callable[[Any, int], Any] | None = None,
        **kwargs,
    ):
        """初始化For节点

        Args:
            node_id: 节点ID
            name: 节点名称
            count: 循环次数
            body_func: 循环体函数，接收(data, index)参数
        """
        self.count = count
        self.body_func = body_func or (lambda data, i: data)
        super().__init__(node_id, name, **kwargs)

    async def exec(self) -> Any:
        """执行For循环"""
        current_data = self._input_data
        results = []

        for i in range(self.count):
            current_data = self.body_func(current_data, i)
            results.append(current_data)

        return {
            "result": current_data,
            "all_results": results,
            "iterations": self.count,
        }

    def _setup_sub_graph(self):
        """For节点不使用子图，直接在exec中实现"""
        pass


class ForEachNode(CompositeNodeBase):
    """ForEach遍历循环复合节点

    遍历集合中的每个元素
    """

    def __init__(
        self,
        node_id: str,
        name: str | None = None,
        items_func: Callable[[Any], Iterable] | None = None,
        body_func: Callable[[Any, Any], Any] | None = None,
        **kwargs,
    ):
        """初始化ForEach节点

        Args:
            node_id: 节点ID
            name: 节点名称
            items_func: 获取可迭代对象的函数
            body_func: 循环体函数，接收(accumulated_data, current_item)参数
        """
        self.items_func = items_func or (lambda x: [])
        self.body_func = body_func or (lambda acc, item: acc)
        super().__init__(node_id, name, **kwargs)

    async def exec(self) -> Any:
        """执行ForEach循环"""
        items = self.items_func(self._input_data)
        current_data = self._input_data
        results = []

        for item in items:
            current_data = self.body_func(current_data, item)
            results.append(current_data)

        return {
            "result": current_data,
            "all_results": results,
            "iterations": len(results),
        }

    def _setup_sub_graph(self):
        """ForEach节点不使用子图，直接在exec中实现"""
        pass


class BreakNode(SequenceNode):
    """Break中断节点

    在循环中使用，设置中断标志
    """

    def __init__(self, node_id: str, name: str | None = None, **kwargs):
        """初始化Break节点"""
        super().__init__(
            node_id, name, lambda x: {"__break__": True, "data": x}, **kwargs
        )


class ContinueNode(SequenceNode):
    """Continue继续节点

    在循环中使用，跳过当前迭代
    """

    def __init__(self, node_id: str, name: str | None = None, **kwargs):
        """初始化Continue节点"""
        super().__init__(
            node_id, name, lambda x: {"__continue__": True, "data": x}, **kwargs
        )


# ==================== 并行控制类复合节点 ====================


class ParallelNode(CompositeNodeBase):
    """并行执行复合节点

    同时执行多个任务，等待所有任务完成
    """

    def __init__(
        self,
        node_id: str,
        name: str | None = None,
        tasks: list[Callable[[Any], Any]] | None = None,
        **kwargs,
    ):
        """初始化Parallel节点

        Args:
            node_id: 节点ID
            name: 节点名称
            tasks: 并行执行的任务列表
        """
        self.tasks = tasks or []
        super().__init__(node_id, name, **kwargs)

    def _setup_sub_graph(self):
        """设置并行执行子图"""
        # 输入节点
        input_node = SequenceNode("input", "输入", lambda x: x)

        # 分叉节点
        fork = ForkNode("fork", "分叉")

        # 汇聚节点
        join = JoinNode(
            "join", "汇聚", lambda results: {"results": results, "count": len(results)}
        )

        # 添加基础节点
        self.sub_graph.add_node(input_node)
        self.sub_graph.add_node(fork)
        self.sub_graph.add_node(join)

        # 连接主要流程
        self.sub_graph.add_edge("input", "fork")

        # 为每个任务创建处理节点
        for i, task in enumerate(self.tasks):
            task_node = SequenceNode(f"task_{i}", f"任务{i}", task)
            self.sub_graph.add_node(task_node)
            self.sub_graph.add_edge("fork", f"task_{i}")
            self.sub_graph.add_edge(f"task_{i}", "join")

        # 如果没有任务，直接连接fork到join
        if not self.tasks:
            self.sub_graph.add_edge("fork", "join")

        # 设置起始和结束节点
        self.sub_graph.set_start("input")
        self.sub_graph.add_end("join")


class RaceNode(CompositeNodeBase):
    """竞态执行复合节点

    并行执行多个任务，第一个完成的任务结果被返回
    """

    def __init__(
        self,
        node_id: str,
        name: str | None = None,
        tasks: list[Callable[[Any], Any]] | None = None,
        **kwargs,
    ):
        """初始化Race节点"""
        self.tasks = tasks or []
        super().__init__(node_id, name, **kwargs)

    async def exec(self) -> Any:
        """执行竞态任务"""
        if not self.tasks:
            return {"result": None, "winner": None}

        # 创建所有任务的协程
        async def run_task(task, index):
            return {"result": task(self._input_data), "winner": index}

        # 创建Task对象而不是裸协程
        tasks_coroutines = [
            asyncio.create_task(run_task(task, i)) for i, task in enumerate(self.tasks)
        ]

        # 等待第一个完成的任务
        done, pending = await asyncio.wait(
            tasks_coroutines, return_when=asyncio.FIRST_COMPLETED
        )

        # 取消其他任务
        for task in pending:
            task.cancel()

        # 返回第一个完成的结果
        winner_result = done.pop().result()
        return winner_result

    def _setup_sub_graph(self):
        """Race节点不使用子图，直接在exec中实现"""
        pass


class ThrottleNode(CompositeNodeBase):
    """限流执行复合节点

    控制任务执行的频率
    """

    def __init__(
        self,
        node_id: str,
        name: str | None = None,
        max_concurrent: int = 1,
        tasks: list[Callable[[Any], Any]] | None = None,
        **kwargs,
    ):
        """初始化Throttle节点

        Args:
            node_id: 节点ID
            name: 节点名称
            max_concurrent: 最大并发数
            tasks: 任务列表
        """
        self.max_concurrent = max_concurrent
        self.tasks = tasks or []
        super().__init__(node_id, name, **kwargs)

    async def exec(self) -> Any:
        """执行限流任务"""
        if not self.tasks:
            return {"results": [], "count": 0}

        semaphore = asyncio.Semaphore(self.max_concurrent)
        results = []

        async def run_task(task):
            async with semaphore:
                return task(self._input_data)

        # 创建所有任务的协程
        tasks_coroutines = [run_task(task) for task in self.tasks]

        # 等待所有任务完成
        results = await asyncio.gather(*tasks_coroutines)

        return {
            "results": results,
            "count": len(results),
            "max_concurrent": self.max_concurrent,
        }

    def _setup_sub_graph(self):
        """Throttle节点不使用子图，直接在exec中实现"""
        pass


class BatchNode(CompositeNodeBase):
    """批量执行复合节点

    将数据分批处理
    """

    def __init__(
        self,
        node_id: str,
        name: str | None = None,
        batch_size: int = 10,
        batch_func: Callable[[list], Any] | None = None,
        **kwargs,
    ):
        """初始化Batch节点

        Args:
            node_id: 节点ID
            name: 节点名称
            batch_size: 批量大小
            batch_func: 批处理函数，接收数据列表
        """
        self.batch_size = batch_size
        self.batch_func = batch_func or (lambda batch: batch)
        super().__init__(node_id, name, **kwargs)

    async def exec(self) -> Any:
        """执行批量处理"""
        data = self._input_data

        # 如果输入不是列表，转换为列表
        if not isinstance(data, list):
            data = [data]

        # 分批处理
        results = []
        for i in range(0, len(data), self.batch_size):
            batch = data[i : i + self.batch_size]
            batch_result = self.batch_func(batch)
            results.append(batch_result)

        return {
            "results": results,
            "batch_count": len(results),
            "batch_size": self.batch_size,
            "total_items": len(data),
        }

    def _setup_sub_graph(self):
        """Batch节点不使用子图，直接在exec中实现"""
        pass
