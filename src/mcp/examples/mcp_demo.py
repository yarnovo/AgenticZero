"""MCP 服务使用示例

演示如何使用 MCP 服务管理器及其子服务
"""

import asyncio

from src.graph import GraphManager
from src.mcp import MCPServiceManager


async def demo_service_management():
    """演示服务管理功能"""
    print("=== MCP 服务管理演示 ===\n")

    # 创建服务管理器
    graph_manager = GraphManager()
    mcp_manager = MCPServiceManager(graph_manager=graph_manager)

    # 初始化
    await mcp_manager.handle_initialize({})

    # 1. 列出可用服务类型
    print("1. 列出可用服务类型")
    result = await mcp_manager.handle_call_tool(
        "service_list", {"show_instances": False}
    )
    print(result[0]["text"])
    print()

    # 2. 创建 Python 服务
    print("2. 创建 Python 服务")
    result = await mcp_manager.handle_call_tool(
        "service_create",
        {
            "service_type": "python",
            "service_id": "demo_python",
            "config": {"base_dir": "demo_scripts"},
        },
    )
    print(result[0]["text"])
    print()

    # 3. 创建 Graph 服务
    print("3. 创建 Graph 服务")
    result = await mcp_manager.handle_call_tool(
        "service_create", {"service_type": "graph", "service_id": "demo_graph"}
    )
    print(result[0]["text"])
    print()

    # 4. 列出所有服务实例
    print("4. 列出所有服务实例")
    result = await mcp_manager.handle_call_tool(
        "service_list", {"show_instances": True}
    )
    print(result[0]["text"])
    print()

    return mcp_manager


async def demo_python_service(mcp_manager: MCPServiceManager):
    """演示 Python 服务功能"""
    print("\n=== Python 服务演示 ===\n")

    # 1. 创建 Python 文件
    print("1. 创建 Python 文件")
    code = '''def fibonacci(n):
    """计算斐波那契数列"""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# 测试函数
for i in range(10):
    print(f"F({i}) = {fibonacci(i)}")
'''

    result = await mcp_manager.handle_call_tool(
        "service_call",
        {
            "service_id": "demo_python",
            "tool_name": "python_create",
            "arguments": {
                "name": "fibonacci",
                "code": code,
                "description": "斐波那契数列计算",
            },
        },
    )
    print(result[0]["text"])
    print()

    # 2. 列出文件
    print("2. 列出所有 Python 文件")
    result = await mcp_manager.handle_call_tool(
        "service_call",
        {"service_id": "demo_python", "tool_name": "python_list", "arguments": {}},
    )
    print(result[0]["text"])
    print()

    # 3. 执行文件
    print("3. 执行 Python 文件")
    result = await mcp_manager.handle_call_tool(
        "service_call",
        {
            "service_id": "demo_python",
            "tool_name": "python_execute_file",
            "arguments": {"name": "fibonacci"},
        },
    )
    print(result[0]["text"])
    print()

    # 4. 创建沙盒并执行交互式代码
    print("4. 创建沙盒环境")
    result = await mcp_manager.handle_call_tool(
        "service_call",
        {
            "service_id": "demo_python",
            "tool_name": "python_sandbox_create",
            "arguments": {"sandbox_id": "interactive"},
        },
    )
    print(result[0]["text"])
    print()

    # 5. 在沙盒中定义变量
    print("5. 在沙盒中定义变量和函数")
    result = await mcp_manager.handle_call_tool(
        "service_call",
        {
            "service_id": "demo_python",
            "tool_name": "python_execute",
            "arguments": {
                "code": "data = [1, 2, 3, 4, 5]\nsquares = [x**2 for x in data]\nprint(f'原始数据: {data}')\nprint(f'平方值: {squares}')",
                "sandbox_id": "interactive",
            },
        },
    )
    print(result[0]["text"])
    print()

    # 6. 查看沙盒状态
    print("6. 查看沙盒状态")
    result = await mcp_manager.handle_call_tool(
        "service_call",
        {
            "service_id": "demo_python",
            "tool_name": "python_sandbox_status",
            "arguments": {"sandbox_id": "interactive"},
        },
    )
    print(result[0]["text"])
    print()


async def demo_graph_service(mcp_manager: MCPServiceManager):
    """演示 Graph 服务功能"""
    print("\n=== Graph 服务演示 ===\n")

    # 1. 创建图
    print("1. 创建新图")
    result = await mcp_manager.handle_call_tool(
        "service_call",
        {
            "service_id": "demo_graph",
            "tool_name": "graph_create",
            "arguments": {"graph_id": "data_flow", "description": "数据处理流程图"},
        },
    )
    print(result[0]["text"])
    print()

    # 2. 添加节点
    print("2. 添加节点")
    # 添加输入节点
    result = await mcp_manager.handle_call_tool(
        "service_call",
        {
            "service_id": "demo_graph",
            "tool_name": "graph_node_add",
            "arguments": {
                "graph_id": "data_flow",
                "node_type": "InputNode",
                "node_id": "input",
                "config": {"data": {"numbers": [1, 2, 3, 4, 5]}},
            },
        },
    )
    print(result[0]["text"])

    # 添加处理节点
    result = await mcp_manager.handle_call_tool(
        "service_call",
        {
            "service_id": "demo_graph",
            "tool_name": "graph_node_add",
            "arguments": {
                "graph_id": "data_flow",
                "node_type": "LLMNode",
                "node_id": "process",
                "config": {"prompt": "将输入的数字列表中的每个数字乘以2，返回新的列表"},
            },
        },
    )
    print(result[0]["text"])

    # 添加输出节点
    result = await mcp_manager.handle_call_tool(
        "service_call",
        {
            "service_id": "demo_graph",
            "tool_name": "graph_node_add",
            "arguments": {
                "graph_id": "data_flow",
                "node_type": "OutputNode",
                "node_id": "output",
                "config": {},
            },
        },
    )
    print(result[0]["text"])
    print()

    # 3. 添加边
    print("3. 添加边连接节点")
    # input -> process
    result = await mcp_manager.handle_call_tool(
        "service_call",
        {
            "service_id": "demo_graph",
            "tool_name": "graph_edge_add",
            "arguments": {
                "graph_id": "data_flow",
                "from_node": "input",
                "to_node": "process",
            },
        },
    )
    print(result[0]["text"])

    # process -> output
    result = await mcp_manager.handle_call_tool(
        "service_call",
        {
            "service_id": "demo_graph",
            "tool_name": "graph_edge_add",
            "arguments": {
                "graph_id": "data_flow",
                "from_node": "process",
                "to_node": "output",
            },
        },
    )
    print(result[0]["text"])
    print()

    # 4. 验证图结构
    print("4. 验证图结构")
    result = await mcp_manager.handle_call_tool(
        "service_call",
        {
            "service_id": "demo_graph",
            "tool_name": "graph_validate",
            "arguments": {"graph_id": "data_flow"},
        },
    )
    print(result[0]["text"])
    print()

    # 5. 获取图信息
    print("5. 获取图信息")
    result = await mcp_manager.handle_call_tool(
        "service_call",
        {
            "service_id": "demo_graph",
            "tool_name": "graph_info",
            "arguments": {"graph_id": "data_flow"},
        },
    )
    print(result[0]["text"])
    print()

    # 注意：实际执行图需要配置 LLM，这里仅演示结构操作


async def main():
    """主函数"""
    try:
        # 演示服务管理
        mcp_manager = await demo_service_management()

        # 演示 Python 服务
        await demo_python_service(mcp_manager)

        # 演示 Graph 服务
        await demo_graph_service(mcp_manager)

        # 清理：删除服务
        print("\n=== 清理服务 ===\n")
        for service_id in ["demo_python", "demo_graph"]:
            result = await mcp_manager.handle_call_tool(
                "service_delete", {"service_id": service_id}
            )
            print(result[0]["text"])

    except Exception as e:
        print(f"错误: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
