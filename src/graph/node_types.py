"""
节点类型定义

定义整个图系统的节点层次结构
"""

from abc import abstractmethod
from collections.abc import Callable
from enum import Enum
from typing import Any

from .core import BaseNode


class NodeCategory(Enum):
    """节点类别枚举"""

    TASK = "task"  # 任务节点
    CONTROL = "control"  # 控制节点
    EXCEPTION = "exception"  # 异常节点


class TaskNode(BaseNode):
    """任务节点基类

    任务节点用于执行具体的业务逻辑，是图中的工作单元
    """

    def __init__(
        self,
        node_id: str,
        name: str | None = None,
        process_func: Callable[[Any], Any] | None = None,
        **kwargs,
    ):
        """初始化任务节点

        Args:
            node_id: 节点ID
            name: 节点名称
            process_func: 处理函数，如果提供则使用它代替exec方法
        """
        super().__init__(node_id, name, **kwargs)
        self.category = NodeCategory.TASK
        self.process_func = process_func

    async def prep(self) -> None:
        """准备阶段 - 任务节点默认实现"""
        pass

    async def post(self) -> str | None:
        """后处理阶段 - 任务节点默认返回None（继续执行）"""
        return None

    def _get_input_data(self) -> Any:
        """获取输入数据的辅助方法"""
        return self._input_data if hasattr(self, "_input_data") else None

    async def exec(self) -> Any:
        """执行任务"""
        input_data = self._get_input_data()

        # 如果提供了处理函数，使用它
        if self.process_func:
            return self.process_func(input_data)
        else:
            # 否则调用子类的实现
            return await self._execute_task(input_data)

    async def _execute_task(self, input_data: Any) -> Any:
        """执行任务的具体逻辑 - 子类可以覆盖"""
        # 默认实现：直接返回输入
        return input_data


class ControlNode(BaseNode):
    """控制节点基类

    控制节点用于控制执行流程，如分支、循环、并行等
    """

    def __init__(self, node_id: str, name: str | None = None, **kwargs):
        """初始化控制节点"""
        super().__init__(node_id, name, **kwargs)
        self.category = NodeCategory.CONTROL
        self._control_result = None  # 存储控制决策结果

    async def prep(self) -> None:
        """准备阶段 - 控制节点默认实现"""
        pass

    def _get_input_data(self) -> Any:
        """获取输入数据的辅助方法"""
        return self._input_data if hasattr(self, "_input_data") else None

    async def post(self) -> str | None:
        """后处理阶段 - 返回控制决策"""
        # 如果在exec中设置了控制结果，使用它
        if self._control_result is not None:
            return self._control_result
        # 否则调用子类的决策方法
        return await self._decide_next()

    async def _decide_next(self) -> str | None:
        """决定下一个节点的逻辑 - 子类应该实现"""
        # 默认实现：返回第一个出边
        if hasattr(self, "graph") and self.graph:
            edges = self.graph.get_outgoing_edges(self.node_id)
            return edges[0].to_node if edges else None
        return None

    @abstractmethod
    async def exec(self) -> Any:
        """执行控制逻辑 - 子类必须实现"""
        pass


class ExceptionNode(BaseNode):
    """异常节点基类

    异常节点专门用于处理异常情况，是独立的节点类型
    """

    def __init__(self, node_id: str, name: str | None = None, **kwargs):
        """初始化异常节点"""
        super().__init__(node_id, name, **kwargs)
        self.category = NodeCategory.EXCEPTION
        self.exception_info: dict[str, Any] | None = None
        self.handled_exceptions: list[Exception] = []  # 记录处理过的异常

    def _get_input_data(self) -> Any:
        """获取输入数据的辅助方法"""
        return self._input_data if hasattr(self, "_input_data") else None

    async def prep(self) -> None:
        """准备阶段 - 记录异常信息"""
        input_data = self._get_input_data()
        if isinstance(input_data, dict):
            self.exception_info = input_data.get("exception_info", {})

    async def post(self) -> str | None:
        """后处理阶段 - 根据异常处理结果决定下一步"""
        if self.result and isinstance(self.result, dict):
            # 如果处理成功，继续执行
            if self.result.get("handled", False):
                return self.result.get("next_action", None)
            # 如果处理失败，可能需要特殊的错误路径
            # 支持特殊动作
            error_action = self.result.get("error_action", "error")
            # 如果是"__exit__"，表示要退出整个流程
            if error_action == "__exit__":
                return "__exit__"
            return error_action
        return None

    @abstractmethod
    async def exec(self) -> Any:
        """执行异常处理逻辑 - 子类必须实现"""
        pass

    @abstractmethod
    async def handle_exception(
        self, exception: Exception, context: dict[str, Any]
    ) -> dict[str, Any]:
        """处理异常的核心方法

        Args:
            exception: 捕获的异常
            context: 异常上下文信息

        Returns:
            处理结果字典，包含:
            - handled: 是否成功处理
            - action: 下一步动作
            - result: 处理结果
        """
        pass
