"""MCP 模块集成测试"""

import tempfile

import pytest

from src.graph import GraphManager
from src.mcp import MCPServiceManager


class TestMCPIntegration:
    """MCP 集成测试类"""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_mcp_service_in_agent(self):
        """测试 MCP 服务在 Agent 中的集成"""
        # 创建 Agent 配置（跳过此测试，因为需要真实的 LLM provider）
        pytest.skip("需要配置真实的 LLM provider 才能运行此测试")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_python_and_graph_service_integration(self):
        """测试 Python 和 Graph 服务的集成"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建服务管理器
            graph_manager = GraphManager(base_path=tmpdir)
            service_manager = MCPServiceManager(graph_manager=graph_manager)
            await service_manager.handle_initialize({})

            # 创建 Python 服务
            await service_manager.handle_call_tool(
                "service_create",
                {
                    "service_type": "python",
                    "service_id": "py_svc",
                    "config": {"base_dir": tmpdir},
                },
            )

            # 创建 Graph 服务
            await service_manager.handle_call_tool(
                "service_create", {"service_type": "graph", "service_id": "graph_svc"}
            )

            # 在 Python 服务中创建处理函数
            result = await service_manager.handle_call_tool(
                "service_call",
                {
                    "service_id": "py_svc",
                    "tool_name": "python_create",
                    "arguments": {
                        "name": "data_processor",
                        "code": """
def process_numbers(numbers):
    '''处理数字列表'''
    return {
        'sum': sum(numbers),
        'avg': sum(numbers) / len(numbers),
        'max': max(numbers),
        'min': min(numbers),
        'count': len(numbers)
    }

# 测试
test_data = [1, 2, 3, 4, 5]
result = process_numbers(test_data)
print(f"处理结果: {result}")
""",
                        "description": "数据处理函数",
                    },
                },
            )
            assert "创建成功" in result[0]["text"]

            # 执行 Python 文件
            result = await service_manager.handle_call_tool(
                "service_call",
                {
                    "service_id": "py_svc",
                    "tool_name": "python_execute_file",
                    "arguments": {"name": "data_processor"},
                },
            )
            assert "执行成功" in result[0]["text"]
            assert "sum': 15" in result[0]["text"]
            assert "avg': 3.0" in result[0]["text"]

            # 创建图来使用这个处理函数
            result = await service_manager.handle_call_tool(
                "service_call",
                {
                    "service_id": "graph_svc",
                    "tool_name": "graph_create",
                    "arguments": {
                        "graph_id": "data_pipeline",
                        "description": "数据处理管道",
                    },
                },
            )
            assert "创建成功" in result[0]["text"]

            # 添加处理节点
            result = await service_manager.handle_call_tool(
                "service_call",
                {
                    "service_id": "graph_svc",
                    "tool_name": "graph_node_add",
                    "arguments": {
                        "graph_id": "data_pipeline",
                        "node_type": "TaskNode",
                        "node_id": "process_data",
                        "config": {"name": "数据处理节点"},
                    },
                },
            )
            assert "已添加到图" in result[0]["text"]

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_sandbox_persistence_across_calls(self):
        """测试沙盒在多次调用间的持久性"""
        with tempfile.TemporaryDirectory():
            service_manager = MCPServiceManager()
            await service_manager.handle_initialize({})

            # 创建 Python 服务
            await service_manager.handle_call_tool(
                "service_create",
                {"service_type": "python", "service_id": "sandbox_test"},
            )

            # 创建持久沙盒
            result = await service_manager.handle_call_tool(
                "service_call",
                {
                    "service_id": "sandbox_test",
                    "tool_name": "python_sandbox_create",
                    "arguments": {"sandbox_id": "data_analysis"},
                },
            )
            assert "创建成功" in result[0]["text"]

            # 第一次执行：初始化数据
            result = await service_manager.handle_call_tool(
                "service_call",
                {
                    "service_id": "sandbox_test",
                    "tool_name": "python_execute",
                    "arguments": {
                        "code": """
# 初始化数据
data = [10, 20, 30, 40, 50]
total = sum(data)
print(f"数据: {data}")
print(f"总和: {total}")
""",
                        "sandbox_id": "data_analysis",
                        "use_process": False,
                    },
                },
            )
            assert "总和: 150" in result[0]["text"]

            # 第二次执行：使用之前的数据
            result = await service_manager.handle_call_tool(
                "service_call",
                {
                    "service_id": "sandbox_test",
                    "tool_name": "python_execute",
                    "arguments": {
                        "code": """
# 使用之前的数据计算平均值
avg = total / len(data)
print(f"平均值: {avg}")

# 计算标准差
variance = sum((x - avg) ** 2 for x in data) / len(data)
std_dev = variance ** 0.5
print(f"标准差: {std_dev:.2f}")
""",
                        "sandbox_id": "data_analysis",
                        "use_process": False,
                    },
                },
            )
            assert "平均值: 30.0" in result[0]["text"]
            assert "标准差: 14.14" in result[0]["text"]

            # 检查沙盒状态
            result = await service_manager.handle_call_tool(
                "service_call",
                {
                    "service_id": "sandbox_test",
                    "tool_name": "python_sandbox_status",
                    "arguments": {"sandbox_id": "data_analysis"},
                },
            )
            assert (
                "变量数量: 5" in result[0]["text"]
            )  # data, total, avg, variance, std_dev

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_file_and_memory_sync(self):
        """测试文件系统和内存的同步"""
        with tempfile.TemporaryDirectory() as tmpdir:
            graph_manager = GraphManager(base_path=tmpdir)
            service_manager = MCPServiceManager(graph_manager=graph_manager)
            await service_manager.handle_initialize({})

            # 创建 Graph 服务
            await service_manager.handle_call_tool(
                "service_create", {"service_type": "graph", "service_id": "sync_test"}
            )

            # 创建并保存图
            await service_manager.handle_call_tool(
                "service_call",
                {
                    "service_id": "sync_test",
                    "tool_name": "graph_create",
                    "arguments": {
                        "graph_id": "test_graph",
                        "description": "测试图",
                        "save_to_file": True,
                    },
                },
            )

            # 列出内存中的图
            result = await service_manager.handle_call_tool(
                "service_call",
                {
                    "service_id": "sync_test",
                    "tool_name": "graph_list",
                    "arguments": {"source": "memory"},
                },
            )
            assert "test_graph" in result[0]["text"]

            # 列出文件中的图
            result = await service_manager.handle_call_tool(
                "service_call",
                {
                    "service_id": "sync_test",
                    "tool_name": "graph_list",
                    "arguments": {"source": "file"},
                },
            )
            assert "test_graph" in result[0]["text"]

            # 修改图结构
            await service_manager.handle_call_tool(
                "service_call",
                {
                    "service_id": "sync_test",
                    "tool_name": "graph_node_add",
                    "arguments": {
                        "graph_id": "test_graph",
                        "node_type": "TaskNode",
                        "node_id": "new_node",
                    },
                },
            )

            # 保存修改
            await service_manager.handle_call_tool(
                "service_call",
                {
                    "service_id": "sync_test",
                    "tool_name": "graph_save",
                    "arguments": {"graph_id": "test_graph"},
                },
            )

            # 验证修改已保存
            result = await service_manager.handle_call_tool(
                "service_call",
                {
                    "service_id": "sync_test",
                    "tool_name": "graph_info",
                    "arguments": {"graph_id": "test_graph"},
                },
            )
            assert "节点数: 3" in result[0]["text"]  # start, end, new_node

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_error_recovery(self):
        """测试错误恢复能力"""
        service_manager = MCPServiceManager()
        await service_manager.handle_initialize({})

        # 创建 Python 服务
        await service_manager.handle_call_tool(
            "service_create", {"service_type": "python", "service_id": "error_test"}
        )

        # 执行会出错的代码
        result = await service_manager.handle_call_tool(
            "service_call",
            {
                "service_id": "error_test",
                "tool_name": "python_execute",
                "arguments": {"code": "x = 1 / 0", "use_process": False},
            },
        )
        assert "执行失败" in result[0]["text"]
        assert "ZeroDivisionError" in result[0]["text"]

        # 确保服务仍然可用
        result = await service_manager.handle_call_tool(
            "service_call",
            {
                "service_id": "error_test",
                "tool_name": "python_execute",
                "arguments": {
                    "code": "print('服务仍然正常工作')",
                    "use_process": False,
                },
            },
        )
        assert "执行成功" in result[0]["text"]
        assert "服务仍然正常工作" in result[0]["text"]
