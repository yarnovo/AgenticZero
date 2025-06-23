"""MCP 模块演示脚本"""

import asyncio
import tempfile

from src.graph import GraphManager
from src.mcp import MCPServiceManager


async def main():
    """演示 MCP 模块的主要功能"""
    print("=== MCP 模块功能演示 ===\n")

    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建服务管理器
        graph_manager = GraphManager(base_path=tmpdir)
        service_manager = MCPServiceManager(graph_manager=graph_manager)
        await service_manager.handle_initialize({})

        print("1. 服务管理器初始化完成")

        # 列出可用的服务类型
        result = await service_manager.handle_call_tool("service_types", {})
        print(f"\n2. 可用的服务类型:\n{result[0]['text']}")

        # 创建 Python 服务
        await service_manager.handle_call_tool(
            "service_create",
            {"service_type": "python", "service_id": "py_demo", "config": {"base_dir": tmpdir}},
        )
        print("\n3. Python 服务创建成功")

        # 创建 Graph 服务
        await service_manager.handle_call_tool(
            "service_create", {"service_type": "graph", "service_id": "graph_demo"}
        )
        print("\n4. Graph 服务创建成功")

        # 在 Python 服务中创建文件
        result = await service_manager.handle_call_tool(
            "service_call",
            {
                "service_id": "py_demo",
                "tool_name": "python_create",
                "arguments": {
                    "name": "hello",
                    "code": """
def greet(name):
    '''向某人问好'''
    return f"你好，{name}！"

# 测试函数
message = greet("MCP")
print(message)
""",
                    "description": "问候函数",
                },
            },
        )
        print(f"\n5. Python 文件创建:\n{result[0]['text']}")

        # 执行 Python 文件
        result = await service_manager.handle_call_tool(
            "service_call",
            {
                "service_id": "py_demo",
                "tool_name": "python_execute_file",
                "arguments": {"name": "hello"},
            },
        )
        print(f"\n6. Python 文件执行:\n{result[0]['text']}")

        # 在沙盒中执行代码
        result = await service_manager.handle_call_tool(
            "service_call",
            {
                "service_id": "py_demo",
                "tool_name": "python_execute",
                "arguments": {
                    "code": """
# 计算斐波那契数列
def fib(n):
    if n <= 1:
        return n
    return fib(n-1) + fib(n-2)

# 计算前 10 个数
fib_sequence = [fib(i) for i in range(10)]
print(f"斐波那契数列: {fib_sequence}")

# 数据处理
data = [1, 2, 3, 4, 5]
total = sum(data)
avg = total / len(data)
print(f"数据: {data}")
print(f"总和: {total}, 平均值: {avg}")
""",
                    "use_process": False,
                },
            },
        )
        print(f"\n7. 沙盒代码执行:\n{result[0]['text']}")

        # 创建图
        result = await service_manager.handle_call_tool(
            "service_call",
            {
                "service_id": "graph_demo",
                "tool_name": "graph_create",
                "arguments": {"graph_id": "demo_workflow", "description": "演示工作流"},
            },
        )
        print(f"\n8. 图创建:\n{result[0]['text']}")

        # 添加节点
        result = await service_manager.handle_call_tool(
            "service_call",
            {
                "service_id": "graph_demo",
                "tool_name": "graph_node_add",
                "arguments": {
                    "graph_id": "demo_workflow",
                    "node_type": "TaskNode",
                    "node_id": "process",
                    "config": {"name": "数据处理节点"},
                },
            },
        )
        print(f"\n9. 节点添加:\n{result[0]['text']}")

        # 获取图信息
        result = await service_manager.handle_call_tool(
            "service_call",
            {
                "service_id": "graph_demo",
                "tool_name": "graph_info",
                "arguments": {"graph_id": "demo_workflow"},
            },
        )
        print(f"\n10. 图信息:\n{result[0]['text']}")

        # 列出所有服务
        result = await service_manager.handle_call_tool("service_list", {})
        print(f"\n11. 活动服务列表:\n{result[0]['text']}")

        print("\n=== 演示完成 ===")


if __name__ == "__main__":
    asyncio.run(main())
EOF < /dev/null
