"""Python 内存管理器测试"""

import pytest

from src.mcp.python_mcp.python_memory_manager import (
    PythonMemoryManager,
    SandboxEnvironment,
)


class TestSandboxEnvironment:
    """沙盒环境测试类"""

    @pytest.mark.unit
    def test_sandbox_creation(self):
        """测试沙盒创建"""
        sandbox = SandboxEnvironment()
        assert sandbox.globals is not None
        assert sandbox.locals == {}
        assert "__builtins__" in sandbox.globals

    @pytest.mark.unit
    def test_safe_builtins(self):
        """测试安全的内置函数"""
        sandbox = SandboxEnvironment()
        builtins = sandbox.globals["__builtins__"]

        # 检查允许的函数（这些在白名单中）
        assert "print" in builtins
        assert "len" in builtins
        assert "range" in builtins
        assert "sum" in builtins

        # 检查禁止的函数（这些不在白名单中）
        assert "open" not in builtins
        assert "eval" not in builtins
        assert "exec" not in builtins
        assert "__import__" not in builtins

    @pytest.mark.unit
    def test_simple_execution(self):
        """测试简单代码执行"""
        sandbox = SandboxEnvironment()
        success, output, error = sandbox.execute("print('Hello, World!')")

        assert success is True
        assert "Hello, World!" in output
        assert error == ""

    @pytest.mark.unit
    def test_variable_persistence(self):
        """测试变量持久化"""
        sandbox = SandboxEnvironment()

        # 执行第一段代码
        sandbox.execute("x = 42")
        assert "x" in sandbox.locals
        assert sandbox.locals["x"] == 42

        # 执行第二段代码，使用之前的变量
        success, output, _ = sandbox.execute("print(x * 2)")
        assert success is True
        assert "84" in output

    @pytest.mark.unit
    def test_syntax_error_handling(self):
        """测试语法错误处理"""
        sandbox = SandboxEnvironment()
        success, output, error = sandbox.execute("def bad syntax")

        assert success is False
        assert "SyntaxError" in error

    @pytest.mark.unit
    def test_runtime_error_handling(self):
        """测试运行时错误处理"""
        sandbox = SandboxEnvironment()
        success, output, error = sandbox.execute("1 / 0")

        assert success is False
        assert "ZeroDivisionError" in error

    @pytest.mark.unit
    def test_forbidden_operations(self):
        """测试禁止的操作"""
        sandbox = SandboxEnvironment()

        # 测试文件操作
        success, _, error = sandbox.execute("open('test.txt', 'w')")
        assert success is False
        assert "NameError" in error

        # 测试导入
        success, _, error = sandbox.execute("import os")
        assert success is False
        assert "ImportError" in error


class TestPythonMemoryManager:
    """Python 内存管理器测试类"""

    @pytest.fixture
    def memory_manager(self):
        """创建内存管理器实例"""
        return PythonMemoryManager()

    @pytest.mark.unit
    def test_create_sandbox(self, memory_manager):
        """测试创建沙盒"""
        memory_manager.create_sandbox("test_sandbox")
        assert "test_sandbox" in memory_manager.sandboxes

    @pytest.mark.unit
    def test_create_duplicate_sandbox(self, memory_manager):
        """测试创建重复沙盒"""
        memory_manager.create_sandbox("duplicate")
        with pytest.raises(ValueError, match="沙盒已存在"):
            memory_manager.create_sandbox("duplicate")

    @pytest.mark.unit
    def test_delete_sandbox(self, memory_manager):
        """测试删除沙盒"""
        memory_manager.create_sandbox("to_delete")
        memory_manager.delete_sandbox("to_delete")
        assert "to_delete" not in memory_manager.sandboxes

    @pytest.mark.unit
    def test_delete_nonexistent_sandbox(self, memory_manager):
        """测试删除不存在的沙盒"""
        with pytest.raises(ValueError, match="沙盒不存在"):
            memory_manager.delete_sandbox("nonexistent")

    @pytest.mark.unit
    def test_execute_in_temporary_sandbox(self, memory_manager):
        """测试在临时沙盒中执行代码"""
        result = memory_manager.execute_code(
            "print('临时沙盒')",
            use_process=False,  # 测试时不使用进程隔离
        )

        assert result["success"] is True
        assert "临时沙盒" in result["output"]
        assert result["sandbox_id"] is None

    @pytest.mark.unit
    def test_execute_in_persistent_sandbox(self, memory_manager):
        """测试在持久沙盒中执行代码"""
        memory_manager.create_sandbox("persistent")

        # 第一次执行
        result1 = memory_manager.execute_code(
            "x = 100", sandbox_id="persistent", use_process=False
        )
        assert result1["success"] is True

        # 第二次执行，使用之前的变量
        result2 = memory_manager.execute_code(
            "print(f'x = {x}')", sandbox_id="persistent", use_process=False
        )
        assert result2["success"] is True
        assert "x = 100" in result2["output"]

    @pytest.mark.unit
    def test_sandbox_isolation(self, memory_manager):
        """测试沙盒隔离性"""
        memory_manager.create_sandbox("sandbox1")
        memory_manager.create_sandbox("sandbox2")

        # 在 sandbox1 中设置变量
        memory_manager.execute_code("x = 1", sandbox_id="sandbox1", use_process=False)

        # 在 sandbox2 中设置不同的变量
        memory_manager.execute_code("x = 2", sandbox_id="sandbox2", use_process=False)

        # 验证变量隔离
        result1 = memory_manager.execute_code(
            "print(x)", sandbox_id="sandbox1", use_process=False
        )
        assert "1" in result1["output"]

        result2 = memory_manager.execute_code(
            "print(x)", sandbox_id="sandbox2", use_process=False
        )
        assert "2" in result2["output"]

    @pytest.mark.unit
    def test_get_sandbox_status(self, memory_manager):
        """测试获取沙盒状态"""
        memory_manager.create_sandbox("status_test")

        # 执行一些代码
        memory_manager.execute_code(
            "x = 42\ny = 'hello'\nz = [1, 2, 3]",
            sandbox_id="status_test",
            use_process=False,
        )

        # 获取状态
        status = memory_manager.get_sandbox_status("status_test")
        assert status["sandbox_id"] == "status_test"
        assert status["variable_count"] == 3
        assert "x" in status["variables"]
        assert status["variables"]["x"]["type"] == "int"
        assert "42" in status["variables"]["x"]["value"]

    @pytest.mark.unit
    def test_list_sandboxes(self, memory_manager):
        """测试列出所有沙盒"""
        # 创建多个沙盒
        memory_manager.create_sandbox("box1")
        memory_manager.create_sandbox("box2")
        memory_manager.create_sandbox("box3")

        sandboxes = memory_manager.list_sandboxes()
        assert len(sandboxes) == 3
        assert "box1" in sandboxes
        assert "box2" in sandboxes
        assert "box3" in sandboxes

    @pytest.mark.unit
    def test_execution_history(self, memory_manager):
        """测试执行历史"""
        # 执行多个代码
        memory_manager.execute_code("x = 1", use_process=False)
        memory_manager.execute_code("y = 2", use_process=False)
        memory_manager.execute_code("z = 3", use_process=False)

        history = memory_manager.get_execution_history(limit=2)
        assert len(history) == 2
        assert history[-1]["code"] == "z = 3"
        assert history[-2]["code"] == "y = 2"

    @pytest.mark.unit
    def test_clear_history(self, memory_manager):
        """测试清空历史"""
        memory_manager.execute_code("x = 1", use_process=False)
        memory_manager.clear_history()

        history = memory_manager.get_execution_history()
        assert len(history) == 0

    @pytest.mark.unit
    def test_execution_timeout(self, memory_manager):
        """测试执行超时"""
        # 无限循环代码
        code = "while True: pass"
        result = memory_manager.execute_code(
            code,
            timeout=1,
            use_process=True,  # 必须使用进程才能超时
        )

        assert result["success"] is False
        assert "超时" in result["error"]

    @pytest.mark.unit
    def test_complex_data_types(self, memory_manager):
        """测试复杂数据类型"""
        code = """
data = {
    'list': [1, 2, 3],
    'dict': {'a': 1, 'b': 2},
    'set': {1, 2, 3},
    'tuple': (1, 2, 3)
}
print(data)
"""
        result = memory_manager.execute_code(code, use_process=False)
        assert result["success"] is True
        assert "list" in result["output"]
        assert "dict" in result["output"]

    @pytest.mark.unit
    def test_mathematical_operations(self, memory_manager):
        """测试数学运算"""
        code = """
import math
result = sum(range(10))
squared = [x**2 for x in range(5)]
print(f"Sum: {result}")
print(f"Squares: {squared}")
"""
        result = memory_manager.execute_code(code, use_process=False)
        assert result["success"] is False  # import math 应该失败
        assert "ImportError" in result["error"]

        # 使用允许的数学函数
        code2 = """
result = sum(range(10))
squared = [x**2 for x in range(5)]
print(f"Sum: {result}")
print(f"Squares: {squared}")
"""
        result2 = memory_manager.execute_code(code2, use_process=False)
        assert result2["success"] is True
        assert "Sum: 45" in result2["output"]
        assert "[0, 1, 4, 9, 16]" in result2["output"]
