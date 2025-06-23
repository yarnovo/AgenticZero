"""Python MCP 服务器测试"""

import tempfile

import pytest

from src.mcp.python_mcp.python_mcp_server import PythonMCPServer


@pytest.fixture
def temp_dir():
    """创建临时目录"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
async def python_server(temp_dir):
    """创建 Python MCP 服务器实例"""
    server = PythonMCPServer(base_dir=temp_dir)
    await server.handle_initialize({})
    return server


class TestPythonMCPServer:
    """Python MCP 服务器测试类"""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_server_initialization(self, python_server):
        """测试服务器初始化"""
        info = await python_server.handle_initialize({})
        assert info["capabilities"]["tools"]["available"] is True
        assert info["serverInfo"]["name"] == "python_mcp_server"
        assert info["serverInfo"]["version"] == "1.0.0"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_list_tools(self, python_server):
        """测试列出工具"""
        tools = await python_server.handle_list_tools()
        assert len(tools) == 12  # 应该有12个工具

        tool_names = [tool["name"] for tool in tools]
        assert "python_create" in tool_names
        assert "python_execute" in tool_names
        assert "python_sandbox_create" in tool_names

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_and_read_file(self, python_server):
        """测试创建和读取文件"""
        # 创建文件
        result = await python_server.handle_call_tool(
            "python_create",
            {
                "name": "test_script",
                "code": "def greet(name):\n    return f'Hello, {name}!'",
                "description": "测试脚本",
            },
        )
        assert "创建成功" in result[0]["text"]

        # 读取文件
        result = await python_server.handle_call_tool(
            "python_read", {"name": "test_script"}
        )
        assert "def greet" in result[0]["text"]
        assert "测试脚本" in result[0]["text"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_update_file(self, python_server):
        """测试更新文件"""
        # 先创建文件
        await python_server.handle_call_tool(
            "python_create", {"name": "update_test", "code": "x = 1"}
        )

        # 更新文件
        result = await python_server.handle_call_tool(
            "python_update", {"name": "update_test", "code": "x = 42\ny = 100"}
        )
        assert "更新成功" in result[0]["text"]

        # 验证更新
        result = await python_server.handle_call_tool(
            "python_read", {"name": "update_test"}
        )
        assert "x = 42" in result[0]["text"]
        assert "y = 100" in result[0]["text"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_delete_file(self, python_server):
        """测试删除文件"""
        # 创建文件
        await python_server.handle_call_tool(
            "python_create", {"name": "to_delete", "code": "print('delete me')"}
        )

        # 删除文件
        result = await python_server.handle_call_tool(
            "python_delete", {"name": "to_delete"}
        )
        assert "删除成功" in result[0]["text"]

        # 验证删除
        result = await python_server.handle_call_tool(
            "python_read", {"name": "to_delete"}
        )
        assert "出错" in result[0]["text"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_list_files(self, python_server):
        """测试列出文件"""
        # 创建多个文件
        for i in range(3):
            await python_server.handle_call_tool(
                "python_create", {"name": f"file_{i}", "code": f"x = {i}"}
            )

        # 列出文件
        result = await python_server.handle_call_tool("python_list", {})
        text = result[0]["text"]
        assert "找到 3 个 Python 文件" in text
        assert "file_0.py" in text
        assert "file_1.py" in text
        assert "file_2.py" in text

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_search_files(self, python_server):
        """测试搜索文件"""
        # 创建测试文件
        await python_server.handle_call_tool(
            "python_create",
            {"name": "math_helper", "code": "def add(a, b): return a + b"},
        )
        await python_server.handle_call_tool(
            "python_create",
            {"name": "string_helper", "code": "def upper(s): return s.upper()"},
        )

        # 搜索文件
        result = await python_server.handle_call_tool(
            "python_search", {"keyword": "helper"}
        )
        assert "找到 2 个匹配的文件" in result[0]["text"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_execute_code(self, python_server):
        """测试执行代码"""
        result = await python_server.handle_call_tool(
            "python_execute",
            {
                "code": "print('Hello from sandbox!')\nresult = 2 + 2\nprint(f'Result: {result}')",
                "use_process": False,
            },
        )
        assert "执行成功" in result[0]["text"]
        assert "Hello from sandbox!" in result[0]["text"]
        assert "Result: 4" in result[0]["text"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_execute_file(self, python_server):
        """测试执行文件"""
        # 创建文件
        await python_server.handle_call_tool(
            "python_create",
            {
                "name": "calculator",
                "code": "print('Calculator')\nprint(f'10 + 20 = {10 + 20}')",
            },
        )

        # 执行文件
        result = await python_server.handle_call_tool(
            "python_execute_file", {"name": "calculator"}
        )
        assert "执行成功" in result[0]["text"]
        assert "Calculator" in result[0]["text"]
        assert "10 + 20 = 30" in result[0]["text"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_sandbox_operations(self, python_server):
        """测试沙盒操作"""
        # 创建沙盒
        result = await python_server.handle_call_tool(
            "python_sandbox_create", {"sandbox_id": "test_sandbox"}
        )
        assert "创建成功" in result[0]["text"]

        # 在沙盒中执行代码
        result = await python_server.handle_call_tool(
            "python_execute",
            {
                "code": "x = 100\ny = 200",
                "sandbox_id": "test_sandbox",
                "use_process": False,
            },
        )
        assert "执行成功" in result[0]["text"]

        # 获取沙盒状态
        result = await python_server.handle_call_tool(
            "python_sandbox_status", {"sandbox_id": "test_sandbox"}
        )
        assert "变量数量: 2" in result[0]["text"]
        assert "x: int = 100" in result[0]["text"]
        assert "y: int = 200" in result[0]["text"]

        # 列出沙盒
        result = await python_server.handle_call_tool("python_sandbox_list", {})
        assert "test_sandbox" in result[0]["text"]

        # 删除沙盒
        result = await python_server.handle_call_tool(
            "python_sandbox_delete", {"sandbox_id": "test_sandbox"}
        )
        assert "删除成功" in result[0]["text"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_error_handling(self, python_server):
        """测试错误处理"""
        # 测试语法错误
        result = await python_server.handle_call_tool(
            "python_create", {"name": "bad_syntax", "code": "def bad("}
        )
        assert "出错" in result[0]["text"]
        assert "语法错误" in result[0]["text"]

        # 测试执行错误
        result = await python_server.handle_call_tool(
            "python_execute", {"code": "1 / 0", "use_process": False}
        )
        assert "执行失败" in result[0]["text"]
        assert "ZeroDivisionError" in result[0]["text"]

        # 测试不存在的工具
        result = await python_server.handle_call_tool("unknown_tool", {})
        assert "未知的工具" in result[0]["text"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_complex_execution(self, python_server):
        """测试复杂代码执行"""
        code = """
# 斐波那契数列
def fib(n):
    if n <= 1:
        return n
    return fib(n-1) + fib(n-2)

# 计算前10个数
results = [fib(i) for i in range(10)]
print(f"Fibonacci sequence: {results}")

# 数据处理
data = [1, 2, 3, 4, 5]
squared = [x**2 for x in data]
total = sum(squared)
print(f"Squared: {squared}")
print(f"Total: {total}")
"""
        result = await python_server.handle_call_tool(
            "python_execute", {"code": code, "timeout": 10, "use_process": False}
        )
        assert "执行成功" in result[0]["text"]
        assert "Fibonacci sequence" in result[0]["text"]
        assert "[0, 1, 1, 2, 3, 5, 8, 13, 21, 34]" in result[0]["text"]
        assert "Total: 55" in result[0]["text"]
