"""基础原子节点使用示例

演示5种原子化控制流节点的基本使用方法。
"""

import asyncio
import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from graph import (
    BranchNode,
    Edge,
    ForkNode,
    Graph,
    GraphExecutor,
    JoinNode,
    MergeNode,
    SequenceNode,
)


async def example_sequence_node():
    """顺序节点示例：简单的数据处理流水线"""
    print("\n=== 顺序节点示例 ===")

    # 创建图
    graph = Graph()

    # 创建顺序节点
    node1 = SequenceNode("input", "输入节点", lambda x: x * 2)
    node2 = SequenceNode("process", "处理节点", lambda x: x + 10)
    node3 = SequenceNode("output", "输出节点", lambda x: f"结果: {x}")

    # 添加节点到图
    graph.add_node(node1)
    graph.add_node(node2)
    graph.add_node(node3)

    # 连接节点
    graph.add_edge(Edge("input", "process"))
    graph.add_edge(Edge("process", "output"))

    # 设置起始节点
    graph.set_start_node("input")
    graph.add_end("output")

    # 执行图，提供初始输入
    executor = GraphExecutor(graph)
    context = await executor.execute(initial_input=5)
    print(f"执行历史: {context.execution_history}")


async def example_branch_merge_nodes():
    """分支和合并节点示例：条件处理流程"""
    print("\n=== 分支和合并节点示例 ===")

    graph = Graph()

    # 创建节点
    input_node = SequenceNode("input", "输入", lambda x: x)

    # 分支节点：根据数值大小选择路径
    branch_node = BranchNode(
        "branch", "条件分支", lambda x: "high" if x > 50 else "low"
    )

    # 两条处理路径
    high_process = SequenceNode(
        "high_path",
        "高值处理",
        lambda x: x["data"] * 0.9 if isinstance(x, dict) else x * 0.9,
    )
    low_process = SequenceNode(
        "low_path",
        "低值处理",
        lambda x: x["data"] * 1.5 if isinstance(x, dict) else x * 1.5,
    )

    # 合并节点
    merge_node = MergeNode("merge", "合并节点")

    # 输出节点
    output_node = SequenceNode("output", "输出", lambda x: f"最终结果: {x}")

    # 添加所有节点
    for node in [
        input_node,
        branch_node,
        high_process,
        low_process,
        merge_node,
        output_node,
    ]:
        graph.add_node(node)

    # 连接节点
    graph.add_edge(Edge("input", "branch"))
    graph.add_edge(Edge("branch", "high_path", action="high"))
    graph.add_edge(Edge("branch", "low_path", action="low"))
    graph.add_edge(Edge("high_path", "merge"))
    graph.add_edge(Edge("low_path", "merge"))
    graph.add_edge(Edge("merge", "output"))

    graph.set_start_node("input")
    graph.add_end("output")

    # 测试高值输入
    print("\n测试高值输入 (75):")
    executor = GraphExecutor(graph)
    await executor.execute(initial_input=75)

    # 测试低值输入
    print("\n测试低值输入 (25):")
    executor.reset()
    await executor.execute(initial_input=25)


async def example_fork_join_nodes():
    """分叉和汇聚节点示例：并行处理"""
    print("\n=== 分叉和汇聚节点示例 ===")

    graph = Graph()

    # 输入节点
    input_node = SequenceNode("input", "输入数据", lambda x: x)

    # 分叉节点：将数据分发到多个并行路径
    fork_node = ForkNode("fork", "分叉节点")

    # 三个并行处理节点
    process1 = SequenceNode(
        "process1", "处理1", lambda x: {"path": "A", "value": x * 2}
    )
    process2 = SequenceNode(
        "process2", "处理2", lambda x: {"path": "B", "value": x + 10}
    )
    process3 = SequenceNode("process3", "处理3", lambda x: {"path": "C", "value": x**2})

    # 汇聚节点：等待所有并行处理完成
    join_node = JoinNode(
        "join",
        "汇聚节点",
        lambda results: {
            "combined": sum(r.get("value", 0) for r in results),
            "paths": [r.get("path", "") for r in results],
        },
        expected_inputs=3,
    )

    # 输出节点
    output_node = SequenceNode(
        "output", "输出", lambda x: f"合并结果: {x['combined']}, 路径: {x['paths']}"
    )

    # 添加所有节点
    for node in [
        input_node,
        fork_node,
        process1,
        process2,
        process3,
        join_node,
        output_node,
    ]:
        graph.add_node(node)

    # 连接节点
    graph.add_edge(Edge("input", "fork"))
    graph.add_edge(Edge("fork", "process1"))
    graph.add_edge(Edge("fork", "process2"))
    graph.add_edge(Edge("fork", "process3"))
    graph.add_edge(Edge("process1", "join"))
    graph.add_edge(Edge("process2", "join"))
    graph.add_edge(Edge("process3", "join"))
    graph.add_edge(Edge("join", "output"))

    graph.set_start_node("input")
    graph.add_end("output")

    # 执行
    executor = GraphExecutor(graph)
    context = await executor.execute(initial_input=5)

    print(f"执行了 {len(context.execution_history)} 个节点")


async def main():
    """运行所有示例"""
    await example_sequence_node()
    await example_branch_merge_nodes()
    await example_fork_join_nodes()


if __name__ == "__main__":
    asyncio.run(main())
