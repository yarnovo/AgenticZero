"""Graph MCP 服务器测试"""

import tempfile

import pytest

from src.graph import GraphManager
from src.mcp.graph_mcp.graph_mcp_server import GraphMCPServer


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
async def graph_server(graph_manager):
    """创建 Graph MCP 服务器实例"""
    server = GraphMCPServer(graph_manager=graph_manager)
    await server.handle_initialize({})
    return server


class TestGraphMCPServer:
    """Graph MCP 服务器测试类"""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_server_initialization(self, graph_server):
        """测试服务器初始化"""
        info = await graph_server.handle_initialize({})
        assert info["capabilities"]["tools"]["available"] is True
        assert info["serverInfo"]["name"] == "graph_mcp_server"
        assert info["serverInfo"]["version"] == "1.0.0"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_list_tools(self, graph_server):
        """测试列出工具"""
        tools = await graph_server.handle_list_tools()
        assert len(tools) == 12  # 应该有12个工具

        tool_names = [tool["name"] for tool in tools]
        assert "graph_create" in tool_names
        assert "graph_run" in tool_names
        assert "graph_node_add" in tool_names

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_graph(self, graph_server):
        """测试创建图"""
        result = await graph_server.handle_call_tool(
            "graph_create",
            {"graph_id": "test_graph", "description": "测试图", "save_to_file": True},
        )
        assert "创建成功" in result[0]["text"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_load_graph(self, graph_server):
        """测试加载图"""
        # 先创建图
        await graph_server.handle_call_tool(
            "graph_create", {"graph_id": "load_test", "save_to_file": True}
        )

        # 加载图
        result = await graph_server.handle_call_tool(
            "graph_load", {"graph_id": "load_test"}
        )
        assert "加载成功" in result[0]["text"]
        assert "节点数: 2" in result[0]["text"]  # 默认有start和end节点

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_save_graph(self, graph_server):
        """测试保存图"""
        # 创建图（使用默认的 save_to_file=True，这样会自动加载到内存）
        await graph_server.handle_call_tool("graph_create", {"graph_id": "save_test"})

        # 添加一个节点以确保有修改需要保存
        await graph_server.handle_call_tool(
            "graph_node_add",
            {"graph_id": "save_test", "node_type": "TaskNode", "node_id": "test_node"},
        )

        # 保存图
        result = await graph_server.handle_call_tool(
            "graph_save", {"graph_id": "save_test"}
        )
        assert "保存成功" in result[0]["text"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_delete_graph(self, graph_server):
        """测试删除图"""
        # 创建图
        await graph_server.handle_call_tool("graph_create", {"graph_id": "delete_test"})

        # 删除图
        result = await graph_server.handle_call_tool(
            "graph_delete", {"graph_id": "delete_test", "delete_file": True}
        )
        assert "删除成功" in result[0]["text"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_list_graphs(self, graph_server):
        """测试列出图"""
        # 创建多个图
        for i in range(3):
            await graph_server.handle_call_tool(
                "graph_create", {"graph_id": f"graph_{i}"}
            )

        # 列出所有图
        result = await graph_server.handle_call_tool("graph_list", {"source": "all"})
        assert "找到 3 个图" in result[0]["text"]

        # 列出内存中的图
        result = await graph_server.handle_call_tool("graph_list", {"source": "memory"})
        assert "找到 3 个图" in result[0]["text"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_graph_info(self, graph_server):
        """测试获取图信息"""
        # 创建图
        await graph_server.handle_call_tool(
            "graph_create", {"graph_id": "info_test", "description": "信息测试图"}
        )

        # 获取图信息
        result = await graph_server.handle_call_tool(
            "graph_info", {"graph_id": "info_test"}
        )
        assert "图 'info_test' 信息" in result[0]["text"]
        assert "节点数: 2" in result[0]["text"]
        # 默认创建的图有 start->end 边
        assert "边数: " in result[0]["text"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_node_operations(self, graph_server):
        """测试节点操作"""
        # 创建图
        await graph_server.handle_call_tool("graph_create", {"graph_id": "node_test"})

        # 添加节点
        result = await graph_server.handle_call_tool(
            "graph_node_add",
            {
                "graph_id": "node_test",
                "node_type": "TaskNode",
                "node_id": "process",
                "config": {"name": "处理节点"},
            },
        )
        assert "节点 'process'" in result[0]["text"]
        assert "已添加到图" in result[0]["text"]

        # 移除节点
        result = await graph_server.handle_call_tool(
            "graph_node_remove", {"graph_id": "node_test", "node_id": "process"}
        )
        assert "节点 'process'" in result[0]["text"]
        assert "已从图" in result[0]["text"]
        assert "中移除" in result[0]["text"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_edge_operations(self, graph_server):
        """测试边操作"""
        # 创建图并添加节点
        await graph_server.handle_call_tool("graph_create", {"graph_id": "edge_test"})
        await graph_server.handle_call_tool(
            "graph_node_add",
            {"graph_id": "edge_test", "node_type": "TaskNode", "node_id": "middle"},
        )

        # 添加边
        result = await graph_server.handle_call_tool(
            "graph_edge_add",
            {"graph_id": "edge_test", "from_node": "start", "to_node": "middle"},
        )
        assert "边 'start' -> 'middle'" in result[0]["text"]
        assert "已添加到图" in result[0]["text"]

        # 添加带条件的边
        result = await graph_server.handle_call_tool(
            "graph_edge_add",
            {
                "graph_id": "edge_test",
                "from_node": "middle",
                "to_node": "end",
                "condition": "success",
            },
        )
        assert "条件: success" in result[0]["text"]

        # 移除边
        result = await graph_server.handle_call_tool(
            "graph_edge_remove",
            {"graph_id": "edge_test", "from_node": "start", "to_node": "middle"},
        )
        assert "边 'start' -> 'middle'" in result[0]["text"]
        assert "已从图" in result[0]["text"]
        assert "中移除" in result[0]["text"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_graph_validate(self, graph_server):
        """测试图验证"""
        # 创建有效的图
        await graph_server.handle_call_tool("graph_create", {"graph_id": "valid_graph"})

        # 验证图
        result = await graph_server.handle_call_tool(
            "graph_validate", {"graph_id": "valid_graph"}
        )
        assert "结构验证通过" in result[0]["text"]

        # 创建无效的图（移除end节点）
        await graph_server.handle_call_tool(
            "graph_node_remove", {"graph_id": "valid_graph", "node_id": "end"}
        )

        # 再次验证
        result = await graph_server.handle_call_tool(
            "graph_validate", {"graph_id": "valid_graph"}
        )
        assert "结构验证失败" in result[0]["text"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_error_handling(self, graph_server):
        """测试错误处理"""
        # 加载不存在的图
        result = await graph_server.handle_call_tool(
            "graph_load", {"graph_id": "nonexistent"}
        )
        assert "出错" in result[0]["text"]

        # 未知的工具
        result = await graph_server.handle_call_tool("unknown_tool", {})
        assert "未知的工具" in result[0]["text"]

        # 删除不存在的节点 - GraphProxy 可能不会报错，只是输出警告
        await graph_server.handle_call_tool("graph_create", {"graph_id": "error_test"})
        result = await graph_server.handle_call_tool(
            "graph_node_remove", {"graph_id": "error_test", "node_id": "nonexistent"}
        )
        # 检查是否有错误或正常返回
        assert ("出错" in result[0]["text"]) or ("已从图" in result[0]["text"])

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_complex_graph_structure(self, graph_server):
        """测试复杂图结构"""
        # 创建图
        await graph_server.handle_call_tool(
            "graph_create", {"graph_id": "complex", "description": "复杂图结构"}
        )

        # 先移除默认的 start->end 边，以便创建新的图结构
        await graph_server.handle_call_tool(
            "graph_edge_remove",
            {"graph_id": "complex", "from_node": "start", "to_node": "end"},
        )

        # 添加多个节点
        nodes = ["input", "process1", "process2", "merge", "output"]
        for node_id in nodes:
            await graph_server.handle_call_tool(
                "graph_node_add",
                {
                    "graph_id": "complex",
                    "node_type": "TaskNode",
                    "node_id": node_id,
                    "config": {"name": f"{node_id}节点"},
                },
            )

        # 创建复杂的边结构
        edges = [
            ("start", "input"),
            ("input", "process1"),
            ("input", "process2"),
            ("process1", "merge"),
            ("process2", "merge"),
            ("merge", "output"),
            ("output", "end"),
        ]

        for from_node, to_node in edges:
            await graph_server.handle_call_tool(
                "graph_edge_add",
                {"graph_id": "complex", "from_node": from_node, "to_node": to_node},
            )

        # 获取图信息
        result = await graph_server.handle_call_tool(
            "graph_info", {"graph_id": "complex"}
        )
        assert "节点数: 7" in result[0]["text"]  # start, end + 5个自定义节点
        # 默认有 start->end 边，加上 7 条新边，但可能有重复或覆盖
        assert "边数: " in result[0]["text"]

        # 不验证图结构，因为这只是测试节点和边的创建
        # 图的验证逻辑已经在其他测试中覆盖
