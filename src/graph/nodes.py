"""
常用节点类型实现

提供各种预定义的节点类型
"""

import asyncio
import random
from collections.abc import Callable
from typing import Any

from .core import BaseNode


class SimpleNode(BaseNode):
    """
    简单节点

    执行固定的动作，返回固定的结果
    """

    def __init__(
        self,
        node_id: str,
        name: str | None = None,
        action: str = "default",
        **kwargs,
    ):
        """
        初始化简单节点

        Args:
            node_id: 节点ID
            name: 节点名称
            action: 返回的动作
            **kwargs: 其他元数据
        """
        super().__init__(node_id, name, **kwargs)
        self.action = action

    async def prep(self) -> None:
        """准备阶段 - 无需特殊准备"""
        pass

    async def exec(self) -> Any:
        """执行阶段 - 模拟一些工作"""
        await asyncio.sleep(0.1)  # 模拟耗时操作
        return f"执行了 {self.name}"

    async def post(self) -> str:
        """后处理阶段 - 返回固定动作"""
        return self.action


class DataProcessorNode(BaseNode):
    """
    数据处理节点

    使用自定义函数处理输入数据
    """

    def __init__(
        self, node_id: str, name: str | None = None, processor_func=None, **kwargs
    ):
        """
        初始化数据处理节点

        Args:
            node_id: 节点ID
            name: 节点名称
            processor_func: 数据处理函数
            **kwargs: 其他元数据
        """
        super().__init__(node_id, name, **kwargs)
        self.processor_func = processor_func or (lambda x: x)
        self.input_data = None

    async def prep(self) -> None:
        """准备阶段 - 获取输入数据"""
        self.input_data = self.metadata.get("input_data")

    async def exec(self) -> Any:
        """执行阶段 - 处理数据"""
        if asyncio.iscoroutinefunction(self.processor_func):
            return await self.processor_func(self.input_data)
        else:
            return self.processor_func(self.input_data)

    async def post(self) -> str:
        """后处理阶段 - 根据结果决定动作"""
        if self.result:
            return "success"
        else:
            return "failure"


class ConditionalNode(BaseNode):
    """
    条件节点

    根据条件函数的结果决定分支
    """

    def __init__(
        self, node_id: str, name: str | None = None, condition_func=None, **kwargs
    ):
        """
        初始化条件节点

        Args:
            node_id: 节点ID
            name: 节点名称
            condition_func: 条件判断函数
            **kwargs: 其他元数据
        """
        super().__init__(node_id, name, **kwargs)
        self.condition_func = condition_func or (lambda: True)

    async def prep(self) -> None:
        """准备阶段"""
        pass

    async def exec(self) -> Any:
        """执行阶段 - 评估条件"""
        if asyncio.iscoroutinefunction(self.condition_func):
            return await self.condition_func()
        else:
            return self.condition_func()

    async def post(self) -> str:
        """后处理阶段 - 根据条件结果返回动作"""
        if self.result:
            return "true"
        else:
            return "false"


class RandomChoiceNode(BaseNode):
    """
    随机选择节点

    根据权重随机选择下一个动作
    """

    def __init__(
        self,
        node_id: str,
        name: str | None = None,
        choices: dict[str, float] | None = None,
        **kwargs,
    ):
        """
        初始化随机选择节点

        Args:
            node_id: 节点ID
            name: 节点名称
            choices: 选择字典，格式为 {动作: 权重}
            **kwargs: 其他元数据
        """
        super().__init__(node_id, name, **kwargs)
        self.choices = choices or {"default": 1.0}

    async def prep(self) -> None:
        """准备阶段 - 归一化权重"""
        total_weight = sum(self.choices.values())
        self.normalized_choices = {k: v / total_weight for k, v in self.choices.items()}

    async def exec(self) -> Any:
        """执行阶段 - 随机选择"""
        rand = random.random()
        cumulative = 0.0

        for choice, weight in self.normalized_choices.items():
            cumulative += weight
            if rand <= cumulative:
                return choice

        # 理论上不应该到这里
        return list(self.choices.keys())[-1]

    async def post(self) -> str:
        """后处理阶段 - 返回选择的动作"""
        return self.result if self.result else "default"


class LoggingNode(BaseNode):
    """
    日志节点

    用于输出调试信息
    """

    def __init__(
        self, node_id: str, name: str | None = None, log_message: str = "", **kwargs
    ):
        """
        初始化日志节点

        Args:
            node_id: 节点ID
            name: 节点名称
            log_message: 要输出的日志信息
            **kwargs: 其他元数据
        """
        super().__init__(node_id, name, **kwargs)
        self.log_message = log_message

    async def prep(self) -> None:
        """准备阶段"""
        pass

    async def exec(self) -> Any:
        """执行阶段 - 输出日志"""
        print(f"[{self.name}] {self.log_message}")
        return self.log_message

    async def post(self) -> str:
        """后处理阶段"""
        return "default"


class AccumulatorNode(BaseNode):
    """
    累加器节点

    累积数据直到达到阈值
    """

    def __init__(self, node_id: str, name: str | None = None, **kwargs):
        """
        初始化累加器节点

        Args:
            node_id: 节点ID
            name: 节点名称
            **kwargs: 其他元数据（可包含 threshold 阈值）
        """
        super().__init__(node_id, name, **kwargs)
        self.accumulated_data = []

    async def prep(self) -> None:
        """准备阶段 - 收集新数据"""
        new_data = self.metadata.get("data")
        if new_data is not None:
            self.accumulated_data.append(new_data)

    async def exec(self) -> Any:
        """执行阶段 - 返回累积的数据"""
        return self.accumulated_data.copy()

    async def post(self) -> str:
        """后处理阶段 - 检查是否达到阈值"""
        threshold = self.metadata.get("threshold", 5)
        if len(self.accumulated_data) >= threshold:
            return "threshold_reached"
        else:
            return "continue"


class DelayNode(BaseNode):
    """
    延迟节点

    暂停执行一段时间
    """

    def __init__(
        self,
        node_id: str,
        name: str | None = None,
        delay_seconds: float = 1.0,
        **kwargs,
    ):
        """
        初始化延迟节点

        Args:
            node_id: 节点ID
            name: 节点名称
            delay_seconds: 延迟秒数
            **kwargs: 其他元数据
        """
        super().__init__(node_id, name, **kwargs)
        self.delay_seconds = delay_seconds

    async def prep(self) -> None:
        """准备阶段"""
        pass

    async def exec(self) -> Any:
        """执行阶段 - 延迟"""
        await asyncio.sleep(self.delay_seconds)
        return f"延迟了 {self.delay_seconds} 秒"

    async def post(self) -> str:
        """后处理阶段"""
        return "default"


class ErrorNode(BaseNode):
    """
    错误节点

    用于测试错误处理
    """

    def __init__(
        self,
        node_id: str,
        name: str | None = None,
        error_message: str = "模拟错误",
        **kwargs,
    ):
        """
        初始化错误节点

        Args:
            node_id: 节点ID
            name: 节点名称
            error_message: 错误信息
            **kwargs: 其他元数据
        """
        super().__init__(node_id, name, **kwargs)
        self.error_message = error_message

    async def prep(self) -> None:
        """准备阶段"""
        pass

    async def exec(self) -> Any:
        """执行阶段 - 抛出错误"""
        raise RuntimeError(self.error_message)

    async def post(self) -> str:
        """后处理阶段 - 不会执行到这里"""
        return "default"


class FunctionNode(BaseNode):
    """
    函数节点

    包装任意函数为节点
    """

    def __init__(
        self,
        node_id: str,
        name: str | None = None,
        prep_func: Callable | None = None,
        exec_func: Callable | None = None,
        post_func: Callable | None = None,
        **kwargs,
    ):
        """
        初始化函数节点

        Args:
            node_id: 节点ID
            name: 节点名称
            prep_func: 准备函数
            exec_func: 执行函数
            post_func: 后处理函数
            **kwargs: 其他元数据
        """
        super().__init__(node_id, name, **kwargs)
        self._prep_func = prep_func
        self._exec_func = exec_func
        self._post_func = post_func

    async def prep(self) -> None:
        """准备阶段"""
        if self._prep_func:
            if asyncio.iscoroutinefunction(self._prep_func):
                await self._prep_func(self)
            else:
                self._prep_func(self)

    async def exec(self) -> Any:
        """执行阶段"""
        if self._exec_func:
            if asyncio.iscoroutinefunction(self._exec_func):
                return await self._exec_func(self)
            else:
                return self._exec_func(self)
        return None

    async def post(self) -> str:
        """后处理阶段"""
        if self._post_func:
            if asyncio.iscoroutinefunction(self._post_func):
                return await self._post_func(self)
            else:
                return self._post_func(self)
        return "default"
