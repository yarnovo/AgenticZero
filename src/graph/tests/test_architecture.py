#!/usr/bin/env python3
"""
测试图架构功能

演示图架构的核心功能
"""

import asyncio

from src.graph import (
    BranchControlNode,
    EnhancedGraph,
    ForkControlNode,
    JoinControlNode,
    ResumableExecutor,
    RetryNode,
    SequenceControlNode,
    TaskNode,
)


async def test_basic_workflow():
    """测试基础工作流"""
    print("=== 测试基础工作流 ===")

    # 创建图
    graph = EnhancedGraph("test_basic")

    # 创建节点
    start = SequenceControlNode("start", "开始", lambda x: {"value": x})
    double = TaskNode("double", "翻倍", lambda x: x["value"] * 2)
    result = TaskNode("result", "结果", lambda x: {"final": x})

    # 构建图
    graph.add_node(start)
    graph.add_node(double)
    graph.add_node(result)

    graph.add_edge("start", "double")
    graph.add_edge("double", "result")

    graph.set_start("start")
    graph.add_end("result")

    # 执行
    executor = ResumableExecutor(graph)
    context = await executor.execute(initial_input=5)

    print("输入: 5")
    print(f"输出: {context.graph_output}")
    print("执行成功！\n")


async def test_branch_workflow():
    """测试分支工作流"""
    print("=== 测试分支工作流 ===")

    graph = EnhancedGraph("test_branch")

    # 节点
    start = TaskNode("start", "开始", lambda x: {"score": x})
    branch = BranchControlNode(
        "branch", "分支", lambda x: "high" if x["score"] > 50 else "low"
    )
    high_path = TaskNode(
        "high", "高分", lambda x: {"result": "优秀", "score": x["score"]}
    )
    low_path = TaskNode(
        "low", "低分", lambda x: {"result": "需要改进", "score": x["score"]}
    )

    # 构建
    for node in [start, branch, high_path, low_path]:
        graph.add_node(node)

    graph.add_edge("start", "branch")
    graph.add_edge("branch", "high", "high")
    graph.add_edge("branch", "low", "low")

    graph.set_start("start")
    graph.add_end("high")
    graph.add_end("low")

    # 测试高分
    executor = ResumableExecutor(graph)
    context = await executor.execute(initial_input=80)
    print(f"输入: 80, 结果: {context.graph_output}")

    # 重置执行器
    executor.reset()

    # 测试低分
    context = await executor.execute(initial_input=30)
    print(f"输入: 30, 结果: {context.graph_output}")
    print("分支测试成功！\n")


async def test_parallel_workflow():
    """测试并行工作流"""
    print("=== 测试并行工作流 ===")

    graph = EnhancedGraph("test_parallel")

    # 节点
    start = TaskNode("start", "开始", lambda x: {"data": x})
    fork = ForkControlNode("fork", "分叉", fork_count=3)

    # 并行任务
    task1 = TaskNode("task1", "任务1", lambda x: {"task1": x["data"] + 1})
    task2 = TaskNode("task2", "任务2", lambda x: {"task2": x["data"] + 2})
    task3 = TaskNode("task3", "任务3", lambda x: {"task3": x["data"] + 3})

    # 汇聚
    join = JoinControlNode("join", "汇聚", lambda x: {"all_results": x})

    # 构建
    nodes = [start, fork, task1, task2, task3, join]
    for node in nodes:
        graph.add_node(node)

    graph.add_edge("start", "fork")
    graph.add_edge("fork", "task1")
    graph.add_edge("fork", "task2")
    graph.add_edge("fork", "task3")
    graph.add_edge("task1", "join")
    graph.add_edge("task2", "join")
    graph.add_edge("task3", "join")

    graph.set_start("start")
    graph.add_end("join")

    # 执行
    executor = ResumableExecutor(graph)
    context = await executor.execute(initial_input=10)

    print("输入: 10")
    print(f"并行执行结果: {context.graph_output}")
    print("并行测试成功！\n")


async def test_exception_handling():
    """测试异常处理"""
    print("=== 测试异常处理 ===")

    graph = EnhancedGraph("test_exception")

    # 会失败的函数
    fail_count = 0

    def unreliable_func(x):
        nonlocal fail_count
        fail_count += 1
        if fail_count < 3:
            raise ValueError(f"第{fail_count}次失败")
        return {"success": x}

    # 节点
    start = TaskNode("start", "开始", lambda x: x)
    retry = RetryNode(
        "retry", "重试任务", target_func=unreliable_func, max_retries=3, retry_delay=0.1
    )

    # 构建
    graph.add_node(start)
    graph.add_node(retry)
    graph.add_edge("start", "retry")

    graph.set_start("start")
    graph.add_end("retry")

    # 执行
    executor = ResumableExecutor(graph)
    context = await executor.execute(initial_input="test_data")

    print(f"重试结果: {context.graph_output}")
    print("异常处理测试成功！\n")


async def test_serialization():
    """测试序列化"""
    print("=== 测试序列化 ===")

    # 创建简单图
    graph = EnhancedGraph("test_serialize")
    node1 = SequenceControlNode("node1", "节点1")
    node2 = TaskNode("node2", "节点2")

    graph.add_node(node1)
    graph.add_node(node2)
    graph.add_edge("node1", "node2")
    graph.set_start("node1")
    graph.add_end("node2")

    # 序列化
    serialized = graph.serialize()
    print(f"序列化成功，包含 {len(serialized['nodes'])} 个节点")

    # 创建快照
    snapshot = graph.create_snapshot()
    print(f"创建快照成功，时间戳: {snapshot.timestamp}")
    print("序列化测试成功！\n")


async def main():
    """主函数"""
    print("\n开始测试图架构...\n")

    try:
        await test_basic_workflow()
        await test_branch_workflow()
        await test_parallel_workflow()
        await test_exception_handling()
        await test_serialization()

        print("✅ 所有测试通过！图架构工作正常。")

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
