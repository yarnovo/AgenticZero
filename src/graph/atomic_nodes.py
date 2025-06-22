"""原子化控制流节点实现

这个模块实现了5种基本的控制流节点，用于构建复杂的图执行流程：
- SequenceNode: 顺序节点，一个输入一个输出
- BranchNode: 分支节点，一个输入多个输出，根据条件选择
- MergeNode: 合并节点，多个输入一个输出，任意输入到达即继续
- ForkNode: 分叉节点，一个输入多个输出，同时激活所有输出
- JoinNode: 汇聚节点，多个输入一个输出，所有输入到达才继续
"""

from collections.abc import Callable
from typing import Any

from .core import BaseNode


class AtomicNodeBase(BaseNode):
    """原子节点基类，提供默认的prep和post实现"""

    async def prep(self) -> None:
        """准备阶段 - 默认实现"""
        pass

    async def post(self) -> str:
        """后处理阶段 - 默认返回default动作"""
        return "default"

    async def exec(self) -> Any:
        """执行阶段 - 调用同步的exec_sync方法"""
        return self.exec_sync(self._get_input_data())

    def exec_sync(self, input_data: Any) -> Any:
        """同步执行方法，子类应该重写这个方法"""
        return input_data

    def _get_input_data(self) -> Any:
        """获取输入数据（从执行器传递）"""
        # 这个方法会被执行器调用时设置
        return getattr(self, "_input_data", None)


class SequenceNode(AtomicNodeBase):
    """顺序节点

    最基本的节点类型，接收一个输入，执行处理，产生一个输出。
    """

    def __init__(
        self,
        node_id: str,
        name: str | None = None,
        process_func: Callable[[Any], Any] | None = None,
    ):
        """初始化顺序节点

        Args:
            node_id: 节点唯一标识
            name: 节点名称
            process_func: 处理函数，接收输入返回输出
        """
        super().__init__(node_id, name)
        self.process_func = process_func or (lambda x: x)

    def exec_sync(self, input_data: Any) -> Any:
        """执行节点处理

        Args:
            input_data: 输入数据

        Returns:
            处理后的输出数据
        """
        return self.process_func(input_data)


class BranchNode(AtomicNodeBase):
    """分支节点

    根据条件选择一个输出路径。返回的动作决定了激活哪条边。
    """

    def __init__(
        self,
        node_id: str,
        name: str | None = None,
        condition_func: Callable[[Any], str] | None = None,
    ):
        """初始化分支节点

        Args:
            node_id: 节点唯一标识
            name: 节点名称
            condition_func: 条件函数，接收输入返回动作字符串
        """
        super().__init__(node_id, name)
        self.condition_func = condition_func or (lambda x: "default")

    def exec_sync(self, input_data: Any) -> dict[str, Any]:
        """执行分支判断

        Args:
            input_data: 输入数据

        Returns:
            包含动作的字典，格式: {"action": <branch_name>, "data": <output_data>}
        """
        action = self.condition_func(input_data)
        return {"action": action, "data": input_data}

    async def post(self) -> str:
        """后处理阶段 - 返回分支动作"""
        if isinstance(self.result, dict) and "action" in self.result:
            return self.result["action"]
        return "default"


class MergeNode(AtomicNodeBase):
    """合并节点

    多个输入路径汇聚到一个输出。任意一个输入到达即可继续执行。
    可选地对输入进行处理后输出。
    """

    def __init__(
        self,
        node_id: str,
        name: str | None = None,
        merge_func: Callable[[Any], Any] | None = None,
    ):
        """初始化合并节点

        Args:
            node_id: 节点唯一标识
            name: 节点名称
            merge_func: 合并函数，处理输入数据
        """
        super().__init__(node_id, name)
        self.merge_func = merge_func or (lambda x: x)

    def exec_sync(self, input_data: Any) -> Any:
        """执行合并处理

        Args:
            input_data: 输入数据（来自任意一个上游节点）

        Returns:
            处理后的输出数据
        """
        return self.merge_func(input_data)


class ForkNode(AtomicNodeBase):
    """分叉节点

    将一个输入同时发送到多个输出路径，实现并行执行的开始。
    所有下游节点将同时收到相同的数据。
    """

    def __init__(
        self,
        node_id: str,
        name: str | None = None,
        transform_func: Callable[[Any], Any] | None = None,
    ):
        """初始化分叉节点

        Args:
            node_id: 节点唯一标识
            name: 节点名称
            transform_func: 转换函数，在分叉前对数据进行处理
        """
        super().__init__(node_id, name)
        self.transform_func = transform_func or (lambda x: x)

    def exec_sync(self, input_data: Any) -> dict[str, Any]:
        """执行分叉

        Args:
            input_data: 输入数据

        Returns:
            包含特殊标记的字典，告诉执行器激活所有下游节点
        """
        output_data = self.transform_func(input_data)
        # 返回特殊格式，执行器会识别并激活所有下游节点
        return {"__fork__": True, "data": output_data}


class JoinNode(AtomicNodeBase):
    """汇聚节点

    等待所有输入路径都到达后才继续执行，实现并行执行的结束。
    可以对所有输入进行聚合处理。
    """

    def __init__(
        self,
        node_id: str,
        name: str | None = None,
        join_func: Callable[[list[Any]], Any] | None = None,
        expected_inputs: int | None = None,
    ):
        """初始化汇聚节点

        Args:
            node_id: 节点唯一标识
            name: 节点名称
            join_func: 汇聚函数，接收所有输入的列表，返回聚合结果
            expected_inputs: 期望的输入数量，如果为None则自动计算
        """
        super().__init__(node_id, name)
        self.join_func = join_func or (lambda x: x)
        self.expected_inputs = expected_inputs

    def exec_sync(self, input_data: Any) -> Any:
        """执行汇聚

        Args:
            input_data: 输入数据（列表形式，由执行器收集）

        Returns:
            聚合结果
        """
        # 执行器负责收集所有输入并作为列表传递
        if not isinstance(input_data, list):
            # 为了兼容性，将单个输入转换为列表
            input_data = [input_data]

        # 执行汇聚函数
        return self.join_func(input_data)
