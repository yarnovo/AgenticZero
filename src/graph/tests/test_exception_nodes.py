"""
测试异常节点

测试各种异常处理节点的功能
"""

import asyncio
import time

import pytest

from src.graph import CircuitBreakerNode, RetryNode, TimeoutNode, TryCatchNode


@pytest.mark.unit
class TestTryCatchNode:
    """测试Try-Catch节点"""

    def test_try_catch_creation(self):
        """测试Try-Catch节点创建"""

        def try_func(x):
            return x * 2

        def catch_func(x, e):
            return {"error": str(e), "input": x}

        node = TryCatchNode(
            "try1", "异常捕获", try_func=try_func, catch_func=catch_func
        )

        assert node.try_func is try_func
        assert node.catch_func is catch_func
        assert node.exception_types == (Exception,)

    def test_try_catch_with_types(self):
        """测试指定异常类型"""
        node = TryCatchNode("try2", "类型捕获", exception_types=(ValueError, TypeError))

        assert node.exception_types == (ValueError, TypeError)

    @pytest.mark.asyncio
    async def test_try_catch_success(self):
        """测试正常执行"""
        node = TryCatchNode("try3", "成功执行", try_func=lambda x: {"result": x * 2})
        node._input_data = 10

        result = await node.exec()

        assert result["success"] is True
        assert result["result"] == {"result": 20}
        assert result["error"] is None
        assert result["handled"] is True

    @pytest.mark.asyncio
    async def test_try_catch_exception(self):
        """测试异常捕获"""

        def failing_func(x):
            raise ValueError("测试错误")

        def error_handler(x, e):
            return {"caught": True, "message": str(e)}

        node = TryCatchNode(
            "try4", "异常处理", try_func=failing_func, catch_func=error_handler
        )
        node._input_data = "test"

        result = await node.exec()

        assert result["success"] is False
        assert result["error"] == "测试错误"
        assert result["exception_type"] == "ValueError"
        assert result["result"]["caught"] is True

    @pytest.mark.asyncio
    async def test_handle_exception_method(self):
        """测试handle_exception方法"""
        node = TryCatchNode("try5", "处理方法", exception_types=(ValueError,))

        # 处理匹配的异常
        result = await node.handle_exception(ValueError("test"), {"input": "data"})
        assert result["handled"] is True
        assert result["action"] == "continue"

        # 不处理不匹配的异常
        result = await node.handle_exception(TypeError("test"), {"input": "data"})
        assert result["handled"] is False
        assert result["action"] == "propagate"


@pytest.mark.unit
class TestRetryNode:
    """测试重试节点"""

    def test_retry_node_creation(self):
        """测试重试节点创建"""
        node = RetryNode(
            "retry1", "重试节点", max_retries=5, retry_delay=0.5, backoff_factor=1.5
        )

        assert node.max_retries == 5
        assert node.retry_delay == 0.5
        assert node.backoff_factor == 1.5

    @pytest.mark.asyncio
    async def test_retry_success_first_attempt(self):
        """测试第一次就成功"""
        node = RetryNode("retry2", "首次成功", target_func=lambda x: {"success": x})
        node._input_data = "test"

        result = await node.exec()

        assert result["success"] is True
        assert result["result"] == {"success": "test"}
        assert result["attempts"] == 1

    @pytest.mark.asyncio
    async def test_retry_with_failures(self):
        """测试多次失败后成功"""
        attempt_count = 0

        def flaky_func(x):
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise ValueError(f"失败 {attempt_count}")
            return {"finally": "success"}

        node = RetryNode(
            "retry3",
            "多次重试",
            target_func=flaky_func,
            max_retries=3,
            retry_delay=0.01,  # 快速测试
        )
        node._input_data = "test"

        result = await node.exec()

        assert result["success"] is True
        assert result["attempts"] == 3
        assert result["result"] == {"finally": "success"}

    @pytest.mark.asyncio
    async def test_retry_max_exceeded(self):
        """测试超过最大重试次数"""

        def always_fail(x):
            raise ValueError("永远失败")

        node = RetryNode(
            "retry4",
            "超过重试",
            target_func=always_fail,
            max_retries=2,
            retry_delay=0.01,
        )
        node._input_data = "test"

        result = await node.exec()

        assert result["success"] is False
        assert result["attempts"] == 3  # 初始尝试 + 2次重试
        assert result["max_retries_exceeded"] is True
        assert "永远失败" in result["error"]


@pytest.mark.unit
class TestTimeoutNode:
    """测试超时节点"""

    def test_timeout_node_creation(self):
        """测试超时节点创建"""
        node = TimeoutNode("timeout1", "超时节点", timeout_seconds=5.0)

        assert node.timeout_seconds == 5.0

    @pytest.mark.asyncio
    async def test_timeout_success(self):
        """测试正常完成"""

        async def quick_task(x):
            await asyncio.sleep(0.01)
            return {"quick": x}

        node = TimeoutNode(
            "timeout2", "快速任务", target_func=quick_task, timeout_seconds=1.0
        )
        node._input_data = "test"

        result = await node.exec()

        assert result["success"] is True
        assert result["timeout"] is False
        assert result["result"] == {"quick": "test"}

    @pytest.mark.asyncio
    async def test_timeout_exceeded(self):
        """测试超时"""

        async def slow_task(x):
            await asyncio.sleep(2.0)
            return {"slow": x}

        node = TimeoutNode(
            "timeout3", "慢任务", target_func=slow_task, timeout_seconds=0.1
        )
        node._input_data = "test"

        result = await node.exec()

        assert result["success"] is False
        assert result["timeout"] is True
        assert result["result"] is None
        assert "timed out" in result["error"]

    @pytest.mark.asyncio
    async def test_timeout_handle_exception(self):
        """测试超时异常处理"""
        node = TimeoutNode("timeout4", "异常处理")

        result = await node.handle_exception(TimeoutError(), {"test": "context"})

        assert result["handled"] is True
        assert result["action"] == "timeout"
        assert result["result"]["timeout"] is True


@pytest.mark.unit
class TestCircuitBreakerNode:
    """测试熔断器节点"""

    def test_circuit_breaker_creation(self):
        """测试熔断器创建"""
        node = CircuitBreakerNode(
            "circuit1",
            "熔断器",
            failure_threshold=5,
            success_threshold=3,
            timeout_seconds=60.0,
        )

        assert node.failure_threshold == 5
        assert node.success_threshold == 3
        assert node.timeout_seconds == 60.0
        assert node.state == "CLOSED"

    @pytest.mark.asyncio
    async def test_circuit_breaker_closed_success(self):
        """测试关闭状态成功"""
        node = CircuitBreakerNode(
            "circuit2", "正常工作", target_func=lambda x: {"ok": x}
        )
        node._input_data = "test"

        result = await node.exec()

        assert result["success"] is True
        assert result["circuit_breaker_state"] == "CLOSED"
        assert node.failure_count == 0

    @pytest.mark.asyncio
    async def test_circuit_breaker_trip(self):
        """测试熔断器触发"""

        def failing_func(x):
            raise Exception("失败")

        node = CircuitBreakerNode(
            "circuit3", "触发熔断", target_func=failing_func, failure_threshold=2
        )

        # 第一次失败
        node._input_data = "test1"
        result1 = await node.exec()
        assert result1["success"] is False
        assert node.state == "CLOSED"

        # 第二次失败，触发熔断
        node._input_data = "test2"
        result2 = await node.exec()
        assert result2["success"] is False
        assert node.state == "OPEN"
        assert result2["next_action"] == "circuit_trip"

        # 熔断器开启，直接返回失败
        node._input_data = "test3"
        result3 = await node.exec()
        assert result3["success"] is False
        assert result3["error"] == "Circuit breaker is OPEN"
        assert result3["next_action"] == "circuit_open"

    @pytest.mark.asyncio
    async def test_circuit_breaker_recovery(self):
        """测试熔断器恢复"""
        node = CircuitBreakerNode(
            "circuit4",
            "恢复测试",
            target_func=lambda x: {"ok": x},
            failure_threshold=1,
            success_threshold=2,
            timeout_seconds=0.1,  # 快速恢复
        )

        # 触发熔断
        def fail_once(x):
            raise Exception("失败")

        node.target_func = fail_once
        node._input_data = "fail"
        await node.exec()
        assert node.state == "OPEN"

        # 等待超时
        await asyncio.sleep(0.15)

        # 恢复为成功函数
        node.target_func = lambda x: {"ok": x}

        # 进入半开状态
        node._input_data = "test1"
        result1 = await node.exec()
        assert node.state == "HALF_OPEN"
        assert result1["success"] is True

        # 再次成功，完全恢复
        node._input_data = "test2"
        result2 = await node.exec()
        assert node.state == "CLOSED"
        assert result2["success"] is True

    def test_circuit_breaker_reset(self):
        """测试熔断器重置"""
        node = CircuitBreakerNode("circuit5", "重置测试")
        node.state = "OPEN"
        node.failure_count = 10
        node.success_count = 5
        node.last_failure_time = time.time()

        node.reset()

        assert node.state == "CLOSED"
        assert node.failure_count == 0
        assert node.success_count == 0
        assert node.last_failure_time == 0
