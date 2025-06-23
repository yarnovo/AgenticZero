"""MCP 服务管理器测试"""

import tempfile

import pytest

from src.graph import GraphManager
from src.mcp import MCPServiceManager


@pytest.fixture
def temp_dir():
    """创建临时目录"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def graph_manager(temp_dir):
    """创建图管理器实例"""
    return GraphManager(base_path=temp_dir)


@pytest.fixture
async def service_manager(graph_manager):
    """创建 MCP 服务管理器实例"""
    manager = MCPServiceManager(graph_manager=graph_manager)
    await manager.handle_initialize({})
    return manager


class TestMCPServiceManager:
    """MCP 服务管理器测试类"""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_manager_initialization(self, service_manager):
        """测试管理器初始化"""
        info = await service_manager.handle_initialize({})
        assert info["capabilities"]["tools"]["available"] is True
        assert info["serverInfo"]["name"] == "mcp_service_manager"
        assert info["serverInfo"]["version"] == "1.0.0"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_list_tools(self, service_manager):
        """测试列出工具"""
        tools = await service_manager.handle_list_tools()
        assert len(tools) == 6  # 应该有6个管理工具

        tool_names = [tool["name"] for tool in tools]
        assert "service_list" in tool_names
        assert "service_create" in tool_names
        assert "service_delete" in tool_names
        assert "service_info" in tool_names
        assert "service_call" in tool_names
        assert "service_list_tools" in tool_names

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_list_service_types(self, service_manager):
        """测试列出服务类型"""
        result = await service_manager.handle_call_tool(
            "service_list", {"show_instances": False}
        )
        text = result[0]["text"]
        assert "可用的 MCP 服务类型" in text
        assert "python: Python 代码管理和执行服务" in text
        assert "graph: 图管理和执行服务" in text

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_python_service(self, service_manager, temp_dir):
        """测试创建 Python 服务"""
        result = await service_manager.handle_call_tool(
            "service_create",
            {
                "service_type": "python",
                "service_id": "my_python",
                "config": {"base_dir": temp_dir},
            },
        )
        assert "服务实例 'my_python' (类型: python) 创建成功" in result[0]["text"]
        assert "my_python" in service_manager.services

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_graph_service(self, service_manager):
        """测试创建 Graph 服务"""
        result = await service_manager.handle_call_tool(
            "service_create", {"service_type": "graph", "service_id": "my_graph"}
        )
        assert "服务实例 'my_graph' (类型: graph) 创建成功" in result[0]["text"]
        assert "my_graph" in service_manager.services

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_duplicate_service(self, service_manager):
        """测试创建重复服务"""
        # 创建第一个服务
        await service_manager.handle_call_tool(
            "service_create", {"service_type": "python", "service_id": "duplicate"}
        )

        # 尝试创建同名服务
        result = await service_manager.handle_call_tool(
            "service_create", {"service_type": "python", "service_id": "duplicate"}
        )
        assert "服务实例 'duplicate' 已存在" in result[0]["text"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_invalid_service_type(self, service_manager):
        """测试创建无效服务类型"""
        result = await service_manager.handle_call_tool(
            "service_create", {"service_type": "invalid", "service_id": "test"}
        )
        assert "未知的服务类型: invalid" in result[0]["text"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_delete_service(self, service_manager):
        """测试删除服务"""
        # 创建服务
        await service_manager.handle_call_tool(
            "service_create", {"service_type": "python", "service_id": "to_delete"}
        )

        # 删除服务
        result = await service_manager.handle_call_tool(
            "service_delete", {"service_id": "to_delete"}
        )
        assert "服务实例 'to_delete' (类型: python) 删除成功" in result[0]["text"]
        assert "to_delete" not in service_manager.services

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_delete_nonexistent_service(self, service_manager):
        """测试删除不存在的服务"""
        result = await service_manager.handle_call_tool(
            "service_delete", {"service_id": "nonexistent"}
        )
        assert "服务实例 'nonexistent' 不存在" in result[0]["text"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_service_info(self, service_manager, temp_dir):
        """测试获取服务信息"""
        # 创建服务
        await service_manager.handle_call_tool(
            "service_create",
            {
                "service_type": "python",
                "service_id": "info_test",
                "config": {"base_dir": temp_dir},
            },
        )

        # 获取服务信息
        result = await service_manager.handle_call_tool(
            "service_info", {"service_id": "info_test"}
        )
        text = result[0]["text"]
        assert "服务实例: info_test" in text
        assert "类型: python" in text
        assert "创建时间:" in text
        assert f'"base_dir": "{temp_dir}"' in text

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_service_call(self, service_manager):
        """测试调用服务工具"""
        # 创建 Python 服务
        await service_manager.handle_call_tool(
            "service_create", {"service_type": "python", "service_id": "call_test"}
        )

        # 调用服务的工具
        result = await service_manager.handle_call_tool(
            "service_call",
            {
                "service_id": "call_test",
                "tool_name": "python_execute",
                "arguments": {
                    "code": "print('Hello from service!')",
                    "use_process": False,
                },
            },
        )
        assert "[call_test]" in result[0]["text"]
        assert "执行成功" in result[0]["text"]
        assert "Hello from service!" in result[0]["text"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_service_list_tools(self, service_manager):
        """测试列出服务工具"""
        # 创建服务
        await service_manager.handle_call_tool(
            "service_create", {"service_type": "python", "service_id": "tools_test"}
        )

        # 列出服务工具
        result = await service_manager.handle_call_tool(
            "service_list_tools", {"service_id": "tools_test"}
        )
        text = result[0]["text"]
        assert "服务 'tools_test' 的可用工具" in text
        assert "python_create: 创建新的 Python 文件" in text
        assert "python_execute: 在沙盒中执行 Python 代码" in text

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_list_active_services(self, service_manager):
        """测试列出活动服务"""
        # 创建多个服务
        for i in range(3):
            await service_manager.handle_call_tool(
                "service_create",
                {"service_type": "python", "service_id": f"service_{i}"},
            )

        # 列出所有服务
        result = await service_manager.handle_call_tool(
            "service_list", {"show_instances": True}
        )
        text = result[0]["text"]
        assert "活动的服务实例:" in text
        assert "service_0 (类型: python" in text
        assert "service_1 (类型: python" in text
        assert "service_2 (类型: python" in text

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_complex_service_interaction(self, service_manager, temp_dir):
        """测试复杂的服务交互"""
        # 创建 Python 和 Graph 服务
        await service_manager.handle_call_tool(
            "service_create", 
            {"service_type": "python", "service_id": "py_service", "config": {"base_dir": temp_dir}}
        )
        await service_manager.handle_call_tool(
            "service_create", {"service_type": "graph", "service_id": "graph_service"}
        )

        # 在 Python 服务中创建文件
        result = await service_manager.handle_call_tool(
            "service_call",
            {
                "service_id": "py_service",
                "tool_name": "python_create",
                "arguments": {
                    "name": "workflow_processor",
                    "code": "def process(data):\n    return [x * 2 for x in data]",
                },
            },
        )
        assert "创建成功" in result[0]["text"]

        # 在 Graph 服务中创建图
        result = await service_manager.handle_call_tool(
            "service_call",
            {
                "service_id": "graph_service",
                "tool_name": "graph_create",
                "arguments": {"graph_id": "workflow", "description": "工作流图"},
            },
        )
        assert "创建成功" in result[0]["text"]

        # 验证两个服务都正常工作
        info = await service_manager.handle_call_tool(
            "service_info", {"service_id": "py_service"}
        )
        assert "类型: python" in info[0]["text"]

        info = await service_manager.handle_call_tool(
            "service_info", {"service_id": "graph_service"}
        )
        assert "类型: graph" in info[0]["text"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_error_handling(self, service_manager):
        """测试错误处理"""
        # 调用不存在的服务
        result = await service_manager.handle_call_tool(
            "service_call",
            {"service_id": "nonexistent", "tool_name": "some_tool", "arguments": {}},
        )
        assert "服务实例 'nonexistent' 不存在" in result[0]["text"]

        # 未知的工具
        result = await service_manager.handle_call_tool("unknown_tool", {})
        assert "未知的工具: unknown_tool" in result[0]["text"]

        # Graph 服务需要 graph_manager
        service_manager.graph_manager = None
        result = await service_manager.handle_call_tool(
            "service_create", {"service_type": "graph", "service_id": "no_manager"}
        )
        assert "需要 GraphManager 实例" in result[0]["text"]
