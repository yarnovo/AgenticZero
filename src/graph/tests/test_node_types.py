"""
测试节点类型

测试新架构中的各种节点类型
"""

import pytest

from src.graph import ControlNode, ExceptionNode, NodeCategory, NodeStatus, TaskNode


@pytest.mark.unit
class TestTaskNode:
    """测试任务节点"""

    def test_task_node_creation(self):
        """测试任务节点创建"""
        node = TaskNode("task1", "测试任务")
        assert node.node_id == "task1"
        assert node.name == "测试任务"
        assert node.category == NodeCategory.TASK
        assert node.status == NodeStatus.PENDING

    def test_task_node_with_process_func(self):
        """测试带处理函数的任务节点"""

        def process(x):
            return x * 2

        node = TaskNode("task2", "处理任务", process_func=process)
        assert node.process_func is process

    @pytest.mark.asyncio
    async def test_task_node_execution(self):
        """测试任务节点执行"""
        node = TaskNode("task3", "执行任务", process_func=lambda x: x + 10)
        node._input_data = 5

        result = await node.exec()
        assert result == 15

    @pytest.mark.asyncio
    async def test_task_node_default_execution(self):
        """测试任务节点默认执行"""

        class CustomTask(TaskNode):
            async def _execute_task(self, input_data):
                return {"custom": input_data}

        node = CustomTask("custom1", "自定义任务")
        node._input_data = "test"

        result = await node.exec()
        assert result == {"custom": "test"}


@pytest.mark.unit
class TestControlNode:
    """测试控制节点"""

    def test_control_node_creation(self):
        """测试控制节点创建"""

        class TestControl(ControlNode):
            async def exec(self):
                return "control_result"

        node = TestControl("control1", "测试控制")
        assert node.node_id == "control1"
        assert node.category == NodeCategory.CONTROL
        assert node._control_result is None

    @pytest.mark.asyncio
    async def test_control_node_decision(self):
        """测试控制节点决策"""

        class RouterControl(ControlNode):
            async def exec(self):
                return {"route": "path_a"}

            async def _decide_next(self):
                return self.result.get("route")

        node = RouterControl("router1", "路由控制")
        node.result = await node.exec()

        next_node = await node.post()
        assert next_node == "path_a"

    @pytest.mark.asyncio
    async def test_control_node_with_result(self):
        """测试使用_control_result的控制节点"""

        class SmartControl(ControlNode):
            async def exec(self):
                self._control_result = "smart_path"
                return {"processed": True}

        node = SmartControl("smart1", "智能控制")
        await node.exec()

        next_node = await node.post()
        assert next_node == "smart_path"


@pytest.mark.unit
class TestExceptionNode:
    """测试异常节点"""

    def test_exception_node_creation(self):
        """测试异常节点创建"""

        class TestException(ExceptionNode):
            async def exec(self):
                return {"handled": True}

            async def handle_exception(self, exception, context):
                return {"handled": True, "action": "continue"}

        node = TestException("except1", "测试异常")
        assert node.node_id == "except1"
        assert node.category == NodeCategory.EXCEPTION
        assert node.exception_info is None
        assert node.handled_exceptions == []

    @pytest.mark.asyncio
    async def test_exception_node_prep(self):
        """测试异常节点准备阶段"""

        class SafeException(ExceptionNode):
            async def exec(self):
                return {"handled": True}

            async def handle_exception(self, exception, context):
                return {"handled": True}

        node = SafeException("safe1", "安全异常")
        node._input_data = {
            "exception_info": {"type": "ValueError", "message": "测试错误"}
        }

        await node.prep()
        assert node.exception_info == {"type": "ValueError", "message": "测试错误"}

    @pytest.mark.asyncio
    async def test_exception_node_post(self):
        """测试异常节点后处理"""

        class HandlerException(ExceptionNode):
            async def exec(self):
                return {"handled": True, "next_action": "continue_flow"}

            async def handle_exception(self, exception, context):
                return {"handled": True}

        node = HandlerException("handler1", "处理异常")
        node.result = await node.exec()

        next_action = await node.post()
        assert next_action == "continue_flow"

    @pytest.mark.asyncio
    async def test_exception_node_error_action(self):
        """测试异常节点错误动作"""

        class ErrorException(ExceptionNode):
            async def exec(self):
                return {"handled": False, "error_action": "__exit__"}

            async def handle_exception(self, exception, context):
                return {"handled": False}

        node = ErrorException("error1", "错误异常")
        node.result = await node.exec()

        next_action = await node.post()
        assert next_action == "__exit__"


@pytest.mark.unit
class TestNodeHelpers:
    """测试节点辅助方法"""

    def test_get_input_data(self):
        """测试获取输入数据"""
        node = TaskNode("helper1", "辅助测试")

        # 没有输入数据时
        assert node._get_input_data() is None

        # 有输入数据时
        node._input_data = {"test": "data"}
        assert node._get_input_data() == {"test": "data"}

    def test_node_reset(self):
        """测试节点重置"""
        node = TaskNode("reset1", "重置测试")
        node.status = NodeStatus.SUCCESS
        node.result = {"some": "result"}
        node._input_data = {"some": "input"}

        node.reset()

        assert node.status == NodeStatus.PENDING
        assert node.result is None
        # _input_data 会被清除
        assert node._input_data is None

    def test_node_category_enum(self):
        """测试节点类别枚举"""
        assert NodeCategory.TASK.value == "task"
        assert NodeCategory.CONTROL.value == "control"
        assert NodeCategory.EXCEPTION.value == "exception"
