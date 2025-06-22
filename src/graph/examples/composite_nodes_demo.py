"""复合节点演示示例

展示各种复合节点的使用方法，包括控制流和并行控制。
"""

import asyncio
import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from graph import Graph, GraphExecutor
from graph.composite_nodes import (
    BatchNode,
    ForEachNode,
    ForNode,
    IfElseNode,
    ParallelNode,
    RaceNode,
    SwitchNode,
    ThrottleNode,
    WhileNode,
)


async def demo_if_else_node():
    """演示If-Else条件分支节点"""
    print("\n=== If-Else节点演示 ===")

    # 创建图
    graph = Graph("if_else_demo")

    # 创建If-Else节点
    if_else = IfElseNode(
        "if_else",
        "数值检查",
        condition_func=lambda x: x > 50,
        if_func=lambda x: f"大数值: {x} * 2 = {x * 2}",
        else_func=lambda x: f"小数值: {x} + 10 = {x + 10}",
    )

    graph.add_node(if_else)
    graph.set_start("if_else")
    graph.add_end("if_else")

    # 测试不同输入
    for test_value in [75, 25]:
        print(f"\n测试输入: {test_value}")
        executor = GraphExecutor(graph)
        context = await executor.execute(initial_input=test_value)
        print(f"结果: {context.node_outputs.get('if_else')}")


async def demo_switch_node():
    """演示Switch多路分支节点"""
    print("\n=== Switch节点演示 ===")

    # 创建图
    graph = Graph("switch_demo")

    # 创建Switch节点
    switch = SwitchNode(
        "switch",
        "操作选择器",
        selector_func=lambda x: x.get("operation", "default"),
        cases={
            "add": lambda x: x["a"] + x["b"],
            "multiply": lambda x: x["a"] * x["b"],
            "divide": lambda x: x["a"] / x["b"] if x["b"] != 0 else "除零错误",
        },
        default_func=lambda x: f"未知操作: {x}",
    )

    graph.add_node(switch)
    graph.set_start("switch")
    graph.add_end("switch")

    # 测试不同操作
    test_cases = [
        {"operation": "add", "a": 10, "b": 5},
        {"operation": "multiply", "a": 10, "b": 5},
        {"operation": "divide", "a": 10, "b": 2},
        {"operation": "unknown", "a": 10, "b": 5},
    ]

    for test_case in test_cases:
        print(f"\n测试输入: {test_case}")
        executor = GraphExecutor(graph)
        context = await executor.execute(initial_input=test_case)
        print(f"结果: {context.node_outputs.get('switch')}")


async def demo_while_node():
    """演示While循环节点"""
    print("\n=== While节点演示 ===")

    # 创建图
    graph = Graph("while_demo")

    # 创建While节点 - 计算阶乘
    while_node = WhileNode(
        "while_factorial",
        "阶乘计算",
        condition_func=lambda x: x["n"] > 1,
        body_func=lambda x: {"n": x["n"] - 1, "result": x["result"] * x["n"]},
        max_iterations=10,
    )

    graph.add_node(while_node)
    graph.set_start("while_factorial")
    graph.add_end("while_factorial")

    # 测试计算5的阶乘
    test_input = {"n": 5, "result": 1}
    print(f"\n计算 {test_input['n']} 的阶乘")
    executor = GraphExecutor(graph)
    context = await executor.execute(initial_input=test_input)
    result = context.node_outputs.get("while_factorial")
    print(f"结果: {result}")


async def demo_for_node():
    """演示For循环节点"""
    print("\n=== For节点演示 ===")

    # 创建图
    graph = Graph("for_demo")

    # 创建For节点 - 累加器
    for_node = ForNode(
        "for_accumulator",
        "累加器",
        count=5,
        body_func=lambda data, i: data + i + 1,  # 累加1到5
    )

    graph.add_node(for_node)
    graph.set_start("for_accumulator")
    graph.add_end("for_accumulator")

    # 测试累加
    test_input = 0  # 起始值
    print(f"\n从 {test_input} 开始累加1到5")
    executor = GraphExecutor(graph)
    context = await executor.execute(initial_input=test_input)
    result = context.node_outputs.get("for_accumulator")
    print(f"结果: {result}")


async def demo_foreach_node():
    """演示ForEach循环节点"""
    print("\n=== ForEach节点演示 ===")

    # 创建图
    graph = Graph("foreach_demo")

    # 创建ForEach节点 - 处理列表
    foreach_node = ForEachNode(
        "foreach_processor",
        "列表处理器",
        items_func=lambda x: x["items"],
        body_func=lambda acc, item: {
            "processed": acc.get("processed", []) + [item * 2],
            "sum": acc.get("sum", 0) + item,
        },
    )

    graph.add_node(foreach_node)
    graph.set_start("foreach_processor")
    graph.add_end("foreach_processor")

    # 测试处理数字列表
    test_input = {"items": [1, 2, 3, 4, 5]}
    print(f"\n处理列表: {test_input['items']}")
    executor = GraphExecutor(graph)
    context = await executor.execute(initial_input=test_input)
    result = context.node_outputs.get("foreach_processor")
    print(f"结果: {result}")


async def demo_parallel_node():
    """演示并行执行节点"""
    print("\n=== Parallel节点演示 ===")

    # 创建图
    graph = Graph("parallel_demo")

    # 创建Parallel节点 - 并行数据处理
    parallel_node = ParallelNode(
        "parallel_processor",
        "并行处理器",
        tasks=[
            lambda x: x * 2,  # 任务1: 乘以2
            lambda x: x + 10,  # 任务2: 加10
            lambda x: x**2,  # 任务3: 平方
            lambda x: x / 2,  # 任务4: 除以2
        ],
    )

    graph.add_node(parallel_node)
    graph.set_start("parallel_processor")
    graph.add_end("parallel_processor")

    # 测试并行处理
    test_input = 8
    print(f"\n并行处理数值: {test_input}")
    executor = GraphExecutor(graph)
    context = await executor.execute(initial_input=test_input)
    result = context.node_outputs.get("parallel_processor")
    print(f"结果: {result}")


async def demo_race_node():
    """演示竞态执行节点"""
    print("\n=== Race节点演示 ===")

    # 创建图
    graph = Graph("race_demo")

    # 创建Race节点 - 竞态任务
    race_node = RaceNode(
        "race_processor",
        "竞态处理器",
        tasks=[
            lambda x: f"快速任务: {x}",
            lambda x: f"中等任务: {x}",
            lambda x: f"慢速任务: {x}",
        ],
    )

    graph.add_node(race_node)
    graph.set_start("race_processor")
    graph.add_end("race_processor")

    # 测试竞态执行
    test_input = "测试数据"
    print(f"\n竞态执行，输入: {test_input}")
    executor = GraphExecutor(graph)
    context = await executor.execute(initial_input=test_input)
    result = context.node_outputs.get("race_processor")
    print(f"获胜者结果: {result}")


async def demo_throttle_node():
    """演示限流执行节点"""
    print("\n=== Throttle节点演示 ===")

    # 创建图
    graph = Graph("throttle_demo")

    # 创建Throttle节点 - 限流处理
    throttle_node = ThrottleNode(
        "throttle_processor",
        "限流处理器",
        max_concurrent=2,  # 最多同时执行2个任务
        tasks=[
            lambda x: f"任务1结果: {x}",
            lambda x: f"任务2结果: {x}",
            lambda x: f"任务3结果: {x}",
            lambda x: f"任务4结果: {x}",
            lambda x: f"任务5结果: {x}",
        ],
    )

    graph.add_node(throttle_node)
    graph.set_start("throttle_processor")
    graph.add_end("throttle_processor")

    # 测试限流执行
    test_input = "共享数据"
    print(f"\n限流执行，最大并发数: 2，输入: {test_input}")
    executor = GraphExecutor(graph)
    context = await executor.execute(initial_input=test_input)
    result = context.node_outputs.get("throttle_processor")
    print(f"结果: {result}")


async def demo_batch_node():
    """演示批量执行节点"""
    print("\n=== Batch节点演示 ===")

    # 创建图
    graph = Graph("batch_demo")

    # 创建Batch节点 - 批量处理
    batch_node = BatchNode(
        "batch_processor",
        "批量处理器",
        batch_size=3,
        batch_func=lambda batch: {
            "batch_sum": sum(batch),
            "batch_size": len(batch),
            "batch_avg": sum(batch) / len(batch),
        },
    )

    graph.add_node(batch_node)
    graph.set_start("batch_processor")
    graph.add_end("batch_processor")

    # 测试批量处理
    test_input = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    print(f"\n批量处理数据: {test_input}")
    print("批量大小: 3")
    executor = GraphExecutor(graph)
    context = await executor.execute(initial_input=test_input)
    result = context.node_outputs.get("batch_processor")
    print(f"结果: {result}")


async def demo_complex_workflow():
    """演示复杂工作流 - 组合多个复合节点"""
    print("\n=== 复杂工作流演示 ===")

    # 创建图
    graph = Graph("complex_workflow")

    # 1. 输入验证
    input_validator = IfElseNode(
        "validator",
        "输入验证",
        condition_func=lambda x: isinstance(x, dict) and "data" in x,
        if_func=lambda x: x["data"],
        else_func=lambda x: [],
    )

    # 2. 批量处理
    batch_processor = BatchNode(
        "batch_proc",
        "批量处理",
        batch_size=2,
        batch_func=lambda batch: [x * 2 for x in batch],
    )

    # 3. 并行分析
    parallel_analyzer = ParallelNode(
        "parallel_analysis",
        "并行分析",
        tasks=[
            lambda x: {
                "type": "sum",
                "value": sum([sum(batch) for batch in x["results"]]),
            },
            lambda x: {
                "type": "count",
                "value": sum([len(batch) for batch in x["results"]]),
            },
            lambda x: {"type": "batches", "value": x["batch_count"]},
        ],
    )

    # 添加节点到图
    graph.add_node(input_validator)
    graph.add_node(batch_processor)
    graph.add_node(parallel_analyzer)

    # 连接节点
    graph.add_edge("validator", "batch_proc")
    graph.add_edge("batch_proc", "parallel_analysis")

    # 设置起始和结束节点
    graph.set_start("validator")
    graph.add_end("parallel_analysis")

    # 测试复杂工作流
    test_input = {"data": [1, 2, 3, 4, 5, 6, 7]}
    print(f"\n复杂工作流输入: {test_input}")
    executor = GraphExecutor(graph)
    context = await executor.execute(initial_input=test_input)

    print("\n执行步骤:")
    for step in context.execution_history:
        print(f"  {step['node_id']}: {step['result']}")

    final_result = context.node_outputs.get("parallel_analysis")
    print(f"\n最终结果: {final_result}")


async def main():
    """运行所有演示"""
    print("复合节点功能演示")
    print("=" * 50)

    # 控制流类演示
    await demo_if_else_node()
    await demo_switch_node()
    await demo_while_node()
    await demo_for_node()
    await demo_foreach_node()

    # 并行控制类演示
    await demo_parallel_node()
    await demo_race_node()
    await demo_throttle_node()
    await demo_batch_node()

    # 复杂工作流演示
    await demo_complex_workflow()


if __name__ == "__main__":
    asyncio.run(main())
