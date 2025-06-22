"""
运行图配置示例
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.graph import GraphExecutor, load_graph_from_yaml


async def run_simple_flow():
    """运行简单流程示例"""
    print("\n=== 运行简单流程 ===")
    graph = load_graph_from_yaml("examples/graph_configs/simple_flow.yaml")
    executor = GraphExecutor(graph)

    # 设置初始上下文
    executor.context.data = {"message": "Hello World", "data": "test data"}

    # 执行图
    result = await executor.execute()
    print(f"执行结果: {result}")
    print(f"最终上下文: {executor.context}")


async def run_conditional_flow():
    """运行条件分支流程示例"""
    print("\n=== 运行条件分支流程 ===")
    graph = load_graph_from_yaml("examples/graph_configs/conditional_flow.yaml")
    executor = GraphExecutor(graph)

    # 测试高值
    print("\n测试高值情况:")
    executor.context.data = {"value": 75}
    result = await executor.execute()
    print(f"执行结果: {result}")

    # 测试低值
    print("\n测试低值情况:")
    executor.reset()
    executor.context.data = {"value": 25}
    result = await executor.execute()
    print(f"执行结果: {result}")


async def run_function_flow():
    """运行函数节点流程示例"""
    print("\n=== 运行函数节点流程 ===")
    graph = load_graph_from_yaml("examples/graph_configs/function_flow.yaml")
    executor = GraphExecutor(graph)

    # 添加事件监听
    def on_node_start(node, **kwargs):
        print(f"  -> 开始执行: {node.name}")

    def on_node_complete(node, **kwargs):
        print(f"  <- 完成执行: {node.name} (状态: {node.status.value})")

    executor.add_hook("before_node", on_node_start)
    executor.add_hook("after_node", on_node_complete)

    # 执行图
    result = await executor.execute()
    print(f"\n执行结果: {result}")
    print(f"最终上下文包含: {list(executor.context.data.keys())}")


async def run_error_handling_flow():
    """运行错误处理流程示例"""
    print("\n=== 运行错误处理流程 ===")
    graph = load_graph_from_yaml("examples/graph_configs/error_handling_flow.yaml")
    executor = GraphExecutor(graph)

    # 设置重试计数器
    executor.context.data = {"retry_count": 0}

    # 执行图
    try:
        result = await executor.execute()
        print(f"执行结果: {result}")
    except Exception as e:
        print(f"执行失败: {e}")


async def main():
    """主函数"""
    print("图执行框架示例\n")

    # 运行各种示例
    await run_simple_flow()
    await run_conditional_flow()
    await run_function_flow()
    await run_error_handling_flow()

    print("\n所有示例执行完成！")


if __name__ == "__main__":
    asyncio.run(main())
