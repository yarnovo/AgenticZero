"""
复合节点测试

测试各种复合节点的功能和边界情况
"""

import os
import sys

import pytest

# 添加src目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from graph import Graph, GraphExecutor
from graph.composite_nodes import (
    BatchNode,
    BreakNode,
    ContinueNode,
    DoWhileNode,
    ForEachNode,
    ForNode,
    IfElseNode,
    ParallelNode,
    RaceNode,
    SwitchNode,
    ThrottleNode,
    WhileNode,
)


@pytest.mark.asyncio
@pytest.mark.unit
async def test_if_else_node():
    """测试If-Else条件分支节点"""
    # 创建图
    graph = Graph("if_else_test")

    # 创建If-Else节点
    if_else = IfElseNode(
        "if_else",
        "条件测试",
        condition_func=lambda x: x > 10,
        if_func=lambda x: x * 2,
        else_func=lambda x: x + 5,
    )

    graph.add_node(if_else)
    graph.set_start("if_else")
    graph.add_end("if_else")

    # 测试True分支
    executor = GraphExecutor(graph)
    context = await executor.execute(initial_input=15)
    # 注意：复合节点返回子图执行结果，需要从子图的起始节点获取
    assert context.node_outputs.get("if_else") is not None

    # 测试False分支
    executor.reset()
    context = await executor.execute(initial_input=5)
    assert context.node_outputs.get("if_else") is not None


@pytest.mark.asyncio
@pytest.mark.unit
async def test_switch_node():
    """测试Switch多路分支节点"""
    graph = Graph("switch_test")

    switch = SwitchNode(
        "switch",
        "多路分支",
        selector_func=lambda x: x["op"],
        cases={
            "add": lambda x: x["a"] + x["b"],
            "sub": lambda x: x["a"] - x["b"],
            "mul": lambda x: x["a"] * x["b"],
        },
        default_func=lambda x: 0,
    )

    graph.add_node(switch)
    graph.set_start("switch")
    graph.add_end("switch")

    # 测试加法
    executor = GraphExecutor(graph)
    context = await executor.execute(initial_input={"op": "add", "a": 10, "b": 5})
    assert context.node_outputs.get("switch") is not None

    # 测试默认分支
    executor.reset()
    context = await executor.execute(initial_input={"op": "unknown", "a": 10, "b": 5})
    assert context.node_outputs.get("switch") is not None


@pytest.mark.asyncio
@pytest.mark.unit
async def test_while_node():
    """测试While循环节点"""
    graph = Graph("while_test")

    # 计算阶乘的While循环
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

    # 测试计算4的阶乘 (4! = 24)
    executor = GraphExecutor(graph)
    context = await executor.execute(initial_input={"n": 4, "result": 1})
    result = context.node_outputs.get("while_factorial")

    assert result is not None
    assert isinstance(result, dict)
    assert "result" in result
    assert "iterations" in result
    assert result["result"]["result"] == 24  # 4! = 24


@pytest.mark.asyncio
@pytest.mark.unit
async def test_do_while_node():
    """测试Do-While循环节点"""
    graph = Graph("do_while_test")

    do_while = DoWhileNode(
        "do_while",
        "至少执行一次",
        condition_func=lambda x: x["count"] < 3,
        body_func=lambda x: {"count": x["count"] + 1, "sum": x["sum"] + x["count"]},
        max_iterations=5,
    )

    graph.add_node(do_while)
    graph.set_start("do_while")
    graph.add_end("do_while")

    # 测试Do-While循环
    executor = GraphExecutor(graph)
    context = await executor.execute(initial_input={"count": 0, "sum": 0})
    result = context.node_outputs.get("do_while")

    assert result is not None
    assert isinstance(result, dict)
    assert "iterations" in result
    assert result["iterations"] >= 1  # 至少执行一次


@pytest.mark.asyncio
@pytest.mark.unit
async def test_for_node():
    """测试For循环节点"""
    graph = Graph("for_test")

    for_node = ForNode("for_sum", "求和", count=5, body_func=lambda data, i: data + i)

    graph.add_node(for_node)
    graph.set_start("for_sum")
    graph.add_end("for_sum")

    # 测试累加 0+0+1+2+3+4 = 10
    executor = GraphExecutor(graph)
    context = await executor.execute(initial_input=0)
    result = context.node_outputs.get("for_sum")

    assert result is not None
    assert isinstance(result, dict)
    assert "result" in result
    assert "iterations" in result
    assert result["result"] == 10  # 0+0+1+2+3+4 = 10
    assert result["iterations"] == 5


@pytest.mark.asyncio
@pytest.mark.unit
async def test_foreach_node():
    """测试ForEach循环节点"""
    graph = Graph("foreach_test")

    foreach = ForEachNode(
        "foreach_sum",
        "遍历求和",
        items_func=lambda x: x["items"],
        body_func=lambda acc, item: {"sum": acc.get("sum", 0) + item},
    )

    graph.add_node(foreach)
    graph.set_start("foreach_sum")
    graph.add_end("foreach_sum")

    # 测试遍历列表求和
    executor = GraphExecutor(graph)
    context = await executor.execute(initial_input={"items": [1, 2, 3, 4, 5]})
    result = context.node_outputs.get("foreach_sum")

    assert result is not None
    assert isinstance(result, dict)
    assert "result" in result
    assert result["result"]["sum"] == 15  # 1+2+3+4+5 = 15


@pytest.mark.asyncio
@pytest.mark.unit
async def test_break_continue_nodes():
    """测试Break和Continue节点"""
    graph = Graph("break_continue_test")

    # Break节点
    break_node = BreakNode("break", "中断")
    graph.add_node(break_node)
    graph.set_start("break")
    graph.add_end("break")

    executor = GraphExecutor(graph)
    context = await executor.execute(initial_input="test")
    result = context.node_outputs.get("break")

    assert result is not None
    assert isinstance(result, dict)
    assert result.get("__break__") is True

    # Continue节点
    graph = Graph("continue_test")
    continue_node = ContinueNode("continue", "继续")
    graph.add_node(continue_node)
    graph.set_start("continue")
    graph.add_end("continue")

    executor = GraphExecutor(graph)
    context = await executor.execute(initial_input="test")
    result = context.node_outputs.get("continue")

    assert result is not None
    assert isinstance(result, dict)
    assert result.get("__continue__") is True


@pytest.mark.asyncio
@pytest.mark.unit
async def test_parallel_node():
    """测试并行执行节点"""
    graph = Graph("parallel_test")

    parallel = ParallelNode(
        "parallel",
        "并行处理",
        tasks=[lambda x: x * 2, lambda x: x + 10, lambda x: x**2],
    )

    graph.add_node(parallel)
    graph.set_start("parallel")
    graph.add_end("parallel")

    # 测试并行执行
    executor = GraphExecutor(graph)
    context = await executor.execute(initial_input=5)
    # 并行节点使用子图，结果在子图的结束节点中
    assert len(context.execution_history) > 0


@pytest.mark.asyncio
@pytest.mark.unit
async def test_race_node():
    """测试竞态执行节点"""
    graph = Graph("race_test")

    race = RaceNode(
        "race", "竞态处理", tasks=[lambda x: f"fast_{x}", lambda x: f"slow_{x}"]
    )

    graph.add_node(race)
    graph.set_start("race")
    graph.add_end("race")

    # 测试竞态执行
    executor = GraphExecutor(graph)
    context = await executor.execute(initial_input="test")
    result = context.node_outputs.get("race")

    assert result is not None
    assert isinstance(result, dict)
    assert "result" in result
    assert "winner" in result


@pytest.mark.asyncio
@pytest.mark.unit
async def test_throttle_node():
    """测试限流执行节点"""
    graph = Graph("throttle_test")

    throttle = ThrottleNode(
        "throttle",
        "限流处理",
        max_concurrent=2,
        tasks=[lambda x: f"task1_{x}", lambda x: f"task2_{x}", lambda x: f"task3_{x}"],
    )

    graph.add_node(throttle)
    graph.set_start("throttle")
    graph.add_end("throttle")

    # 测试限流执行
    executor = GraphExecutor(graph)
    context = await executor.execute(initial_input="data")
    result = context.node_outputs.get("throttle")

    assert result is not None
    assert isinstance(result, dict)
    assert "results" in result
    assert "max_concurrent" in result
    assert result["max_concurrent"] == 2
    assert len(result["results"]) == 3


@pytest.mark.asyncio
@pytest.mark.unit
async def test_batch_node():
    """测试批量执行节点"""
    graph = Graph("batch_test")

    batch = BatchNode(
        "batch", "批量处理", batch_size=3, batch_func=lambda batch: sum(batch)
    )

    graph.add_node(batch)
    graph.set_start("batch")
    graph.add_end("batch")

    # 测试批量处理
    executor = GraphExecutor(graph)
    context = await executor.execute(initial_input=[1, 2, 3, 4, 5, 6, 7])
    result = context.node_outputs.get("batch")

    assert result is not None
    assert isinstance(result, dict)
    assert "results" in result
    assert "batch_count" in result
    assert "batch_size" in result
    assert result["batch_size"] == 3

    # 应该有3个批次: [1,2,3], [4,5,6], [7]
    assert len(result["results"]) == 3
    assert result["results"][0] == 6  # 1+2+3 = 6
    assert result["results"][1] == 15  # 4+5+6 = 15
    assert result["results"][2] == 7  # 7


@pytest.mark.asyncio
@pytest.mark.unit
async def test_complex_composite_workflow():
    """测试复合节点组合的复杂工作流"""
    graph = Graph("complex_test")

    # 1. 输入处理
    preprocessor = IfElseNode(
        "preprocessor",
        "预处理",
        condition_func=lambda x: isinstance(x, list),
        if_func=lambda x: x,
        else_func=lambda x: [x],
    )

    # 2. 批量处理
    batch_processor = BatchNode(
        "batch_proc", "批处理", batch_size=2, batch_func=lambda batch: sum(batch)
    )

    # 添加节点
    graph.add_node(preprocessor)
    graph.add_node(batch_processor)

    # 连接节点
    graph.add_edge("preprocessor", "batch_proc")

    # 设置起始和结束节点
    graph.set_start("preprocessor")
    graph.add_end("batch_proc")

    # 测试列表输入
    executor = GraphExecutor(graph)
    context = await executor.execute(initial_input=[1, 2, 3, 4, 5])

    # 验证执行历史
    assert len(context.execution_history) >= 2

    # 测试单值输入
    executor.reset()
    context = await executor.execute(initial_input=42)

    # 验证执行历史
    assert len(context.execution_history) >= 2


@pytest.mark.asyncio
@pytest.mark.unit
async def test_edge_cases():
    """测试边界情况"""

    # 测试空任务列表的并行节点
    graph = Graph("empty_parallel_test")
    parallel = ParallelNode("parallel", "空并行", tasks=[])
    graph.add_node(parallel)
    graph.set_start("parallel")
    graph.add_end("parallel")

    executor = GraphExecutor(graph)
    context = await executor.execute(initial_input="test")
    # 应该能正常执行而不报错
    assert len(context.execution_history) >= 1

    # 测试零次循环的For节点
    graph = Graph("zero_for_test")
    for_node = ForNode(
        "for_zero", "零循环", count=0, body_func=lambda data, i: data + 1
    )
    graph.add_node(for_node)
    graph.set_start("for_zero")
    graph.add_end("for_zero")

    executor = GraphExecutor(graph)
    context = await executor.execute(initial_input=10)
    result = context.node_outputs.get("for_zero")

    assert result is not None
    assert result["result"] == 10  # 应该不变
    assert result["iterations"] == 0

    # 测试空列表的批量节点
    graph = Graph("empty_batch_test")
    batch = BatchNode(
        "batch_empty", "空批量", batch_size=3, batch_func=lambda x: len(x)
    )
    graph.add_node(batch)
    graph.set_start("batch_empty")
    graph.add_end("batch_empty")

    executor = GraphExecutor(graph)
    context = await executor.execute(initial_input=[])
    result = context.node_outputs.get("batch_empty")

    assert result is not None
    assert result["batch_count"] == 0
    assert result["total_items"] == 0
