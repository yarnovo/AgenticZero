"""
异常节点

独立的异常处理节点实现
"""

import asyncio
import time
from collections.abc import Callable
from typing import Any

from .node_types import ExceptionNode


class TryCatchNode(ExceptionNode):
    """Try-Catch异常捕获节点

    捕获并处理异常
    """

    def __init__(
        self,
        node_id: str,
        name: str | None = None,
        try_func: Callable[[Any], Any] | None = None,
        catch_func: Callable[[Any, Exception], Any] | None = None,
        exception_types: tuple[type[Exception], ...] = (Exception,),
        **kwargs,
    ):
        """初始化Try-Catch节点

        Args:
            node_id: 节点ID
            name: 节点名称
            try_func: 主要执行函数
            catch_func: 异常处理函数
            exception_types: 要捕获的异常类型
        """
        super().__init__(node_id, name, **kwargs)
        self.try_func = try_func or (lambda x: x)
        self.catch_func = catch_func or (lambda x, e: {"error": str(e), "input": x})
        self.exception_types = exception_types

    async def exec(self) -> Any:
        """执行异常捕获逻辑"""
        input_data = self._input_data if hasattr(self, "_input_data") else None

        try:
            # 尝试执行主函数
            result = self.try_func(input_data)
            return {"success": True, "result": result, "error": None, "handled": True}
        except self.exception_types as e:
            # 捕获并处理异常
            error_result = self.catch_func(input_data, e)
            return {
                "success": False,
                "result": error_result,
                "error": str(e),
                "handled": True,
                "exception_type": type(e).__name__,
            }

    async def handle_exception(
        self, exception: Exception, context: dict[str, Any]
    ) -> dict[str, Any]:
        """处理异常"""
        if isinstance(exception, self.exception_types):
            return {
                "handled": True,
                "action": "continue",
                "result": self.catch_func(context.get("input"), exception),
            }
        else:
            return {"handled": False, "action": "propagate", "result": None}


class RetryNode(ExceptionNode):
    """重试节点

    失败时自动重试
    """

    def __init__(
        self,
        node_id: str,
        name: str | None = None,
        target_func: Callable[[Any], Any] | None = None,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        backoff_factor: float = 2.0,
        exception_types: tuple[type[Exception], ...] = (Exception,),
        **kwargs,
    ):
        """初始化重试节点

        Args:
            node_id: 节点ID
            name: 节点名称
            target_func: 目标执行函数
            max_retries: 最大重试次数
            retry_delay: 重试延迟（秒）
            backoff_factor: 延迟递增因子
            exception_types: 需要重试的异常类型
        """
        super().__init__(node_id, name, **kwargs)
        self.target_func = target_func or (lambda x: x)
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.backoff_factor = backoff_factor
        self.exception_types = exception_types

    async def exec(self) -> Any:
        """执行重试逻辑"""
        input_data = self._input_data if hasattr(self, "_input_data") else None
        last_exception = None
        delay = self.retry_delay

        for attempt in range(self.max_retries + 1):
            try:
                result = self.target_func(input_data)
                return {
                    "success": True,
                    "result": result,
                    "attempts": attempt + 1,
                    "error": None,
                    "handled": True,
                }
            except self.exception_types as e:
                last_exception = e
                if attempt < self.max_retries:
                    await asyncio.sleep(delay)
                    delay *= self.backoff_factor

        return {
            "success": False,
            "result": None,
            "attempts": self.max_retries + 1,
            "error": str(last_exception),
            "handled": True,
            "max_retries_exceeded": True,
        }

    async def handle_exception(
        self, exception: Exception, context: dict[str, Any]
    ) -> dict[str, Any]:
        """处理异常 - 通过重试"""
        if isinstance(exception, self.exception_types):
            # 执行重试逻辑
            self._input_data = context.get("input")
            result = await self.exec()
            return {
                "handled": result["handled"],
                "action": "continue" if result["success"] else "error",
                "result": result,
            }
        else:
            return {"handled": False, "action": "propagate", "result": None}


class TimeoutNode(ExceptionNode):
    """超时控制节点

    控制执行时间，超时则中断
    """

    def __init__(
        self,
        node_id: str,
        name: str | None = None,
        target_func: Callable[[Any], Any] | None = None,
        timeout_seconds: float = 30.0,
        **kwargs,
    ):
        """初始化超时节点

        Args:
            node_id: 节点ID
            name: 节点名称
            target_func: 目标执行函数
            timeout_seconds: 超时时间（秒）
        """
        super().__init__(node_id, name, **kwargs)
        self.target_func = target_func or (lambda x: x)
        self.timeout_seconds = timeout_seconds

    async def exec(self) -> Any:
        """执行超时控制"""
        input_data = self._input_data if hasattr(self, "_input_data") else None

        async def run_target():
            # 检查target_func是否是异步函数
            if asyncio.iscoroutinefunction(self.target_func):
                return await self.target_func(input_data)
            else:
                return self.target_func(input_data)

        try:
            result = await asyncio.wait_for(run_target(), timeout=self.timeout_seconds)
            return {
                "success": True,
                "result": result,
                "timeout": False,
                "timeout_seconds": self.timeout_seconds,
                "handled": True,
            }
        except TimeoutError:
            return {
                "success": False,
                "result": None,
                "timeout": True,
                "timeout_seconds": self.timeout_seconds,
                "handled": True,
                "error": f"Operation timed out after {self.timeout_seconds} seconds",
            }

    async def handle_exception(
        self, exception: Exception, context: dict[str, Any]
    ) -> dict[str, Any]:
        """处理超时异常"""
        if isinstance(exception, asyncio.TimeoutError):
            return {
                "handled": True,
                "action": "timeout",
                "result": {
                    "timeout": True,
                    "duration": self.timeout_seconds,
                    "context": context,
                },
            }
        else:
            return {"handled": False, "action": "propagate", "result": None}


class CircuitBreakerNode(ExceptionNode):
    """熔断器节点

    保护系统免受连续失败的影响
    """

    def __init__(
        self,
        node_id: str,
        name: str | None = None,
        target_func: Callable[[Any], Any] | None = None,
        failure_threshold: int = 5,
        success_threshold: int = 3,
        timeout_seconds: float = 60.0,
        **kwargs,
    ):
        """初始化熔断器节点

        Args:
            node_id: 节点ID
            name: 节点名称
            target_func: 目标执行函数
            failure_threshold: 失败阈值
            success_threshold: 成功阈值（半开状态）
            timeout_seconds: 熔断恢复时间
        """
        super().__init__(node_id, name, **kwargs)
        self.target_func = target_func or (lambda x: x)
        self.failure_threshold = failure_threshold
        self.success_threshold = success_threshold
        self.timeout_seconds = timeout_seconds

        # 熔断器状态
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = 0

    async def exec(self) -> Any:
        """执行熔断器逻辑"""
        input_data = self._input_data if hasattr(self, "_input_data") else None
        current_time = time.time()

        # 检查是否需要从OPEN转换到HALF_OPEN
        if (
            self.state == "OPEN"
            and current_time - self.last_failure_time > self.timeout_seconds
        ):
            self.state = "HALF_OPEN"
            self.success_count = 0

        # 如果熔断器开启，直接返回失败
        if self.state == "OPEN":
            return {
                "success": False,
                "result": None,
                "circuit_breaker_state": self.state,
                "error": "Circuit breaker is OPEN",
                "handled": True,
                "next_action": "circuit_open",
            }

        # 尝试执行目标函数
        try:
            result = self.target_func(input_data)

            # 执行成功
            if self.state == "HALF_OPEN":
                self.success_count += 1
                if self.success_count >= self.success_threshold:
                    self.state = "CLOSED"
                    self.failure_count = 0
            elif self.state == "CLOSED":
                self.failure_count = 0

            return {
                "success": True,
                "result": result,
                "circuit_breaker_state": self.state,
                "error": None,
                "handled": True,
            }

        except Exception as e:
            # 执行失败
            self.failure_count += 1
            self.last_failure_time = current_time

            if self.state == "HALF_OPEN":
                self.state = "OPEN"
            elif (
                self.state == "CLOSED" and self.failure_count >= self.failure_threshold
            ):
                self.state = "OPEN"

            return {
                "success": False,
                "result": None,
                "circuit_breaker_state": self.state,
                "error": str(e),
                "handled": True,
                "next_action": "circuit_trip" if self.state == "OPEN" else "error",
            }

    async def handle_exception(
        self, exception: Exception, context: dict[str, Any]
    ) -> dict[str, Any]:
        """处理异常 - 更新熔断器状态"""
        # 记录失败
        self.failure_count += 1
        self.last_failure_time = time.time()

        # 检查是否需要熔断
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            return {
                "handled": True,
                "action": "circuit_open",
                "result": {
                    "state": self.state,
                    "message": "Circuit breaker tripped",
                    "will_retry_after": self.timeout_seconds,
                },
            }
        else:
            return {
                "handled": True,
                "action": "error",
                "result": {
                    "state": self.state,
                    "failure_count": self.failure_count,
                    "threshold": self.failure_threshold,
                },
            }

    def reset(self):
        """重置熔断器状态"""
        self.state = "CLOSED"
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = 0
