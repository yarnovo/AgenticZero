"""
图实现测试

测试基础图功能和原子节点
"""

import os
import sys

import pytest

# 添加src目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from graph import Graph, GraphExecutor
from graph.atomic_nodes import SequenceNode


@pytest.mark.asyncio
@pytest.mark.unit
async def test_basic_graph():
    """测试基本图功能"""
    print("\n=== 测试基本图功能 ===")

    # 创建节点
    start = SequenceNode("start", "开始节点", lambda x: "开始执行")
    process = SequenceNode("process", "处理节点", lambda x: "处理完成")
    end = SequenceNode("end", "结束节点", lambda x: "执行结束")

    # 使用 >> 操作符构建图
    start >> process >> end

    # 从最后一个节点获取图
    graph = end._temp_graph
    graph.set_start("start")
    graph.add_end("end")

    # 验证图
    valid, errors = graph.validate()
    print(f"图验证结果: {valid}")
    if errors:
        print(f"验证错误: {errors}")

    # 执行图
    executor = GraphExecutor(graph)
    context = await executor.execute(initial_input="test")

    print(f"执行完成，耗时 {context.duration:.2f} 秒")
    print(f"执行历史: {len(context.execution_history)} 个节点")

    for entry in context.execution_history:
        print(f"  - {entry['node_id']}: {entry['result']}")


@pytest.mark.asyncio
@pytest.mark.unit
async def test_data_processing_graph():
    """测试数据处理管道"""
    print("\n=== 测试数据处理管道 ===")

    # 创建数据处理管道
    multiply_node = SequenceNode("multiply", "乘法", lambda x: x * 2)
    add_node = SequenceNode("add", "加法", lambda x: x + 10)
    format_node = SequenceNode("format", "格式化", lambda x: f"最终结果: {x}")

    # 构建图
    multiply_node >> add_node >> format_node

    # 获取图并设置
    graph = format_node._temp_graph
    graph.set_start("multiply")
    graph.add_end("format")

    # 执行
    executor = GraphExecutor(graph)
    context = await executor.execute(initial_input=5)

    print("数据处理结果:")
    for entry in context.execution_history:
        print(f"  {entry['node_id']}: {entry['result']}")


@pytest.mark.asyncio
@pytest.mark.unit
async def test_graph_analysis():
    """测试图分析功能"""
    print("\n=== 测试图分析功能 ===")

    # 创建更复杂的图用于分析
    graph = Graph("分析测试图")

    # 添加节点
    nodes = []
    for i in range(5):
        node = SequenceNode(f"node_{i}", f"节点{i}", lambda x: f"处理{x}")
        nodes.append(node)
        graph.add_node(node)

    # 创建连接
    graph.add_edge("node_0", "node_1")
    graph.add_edge("node_0", "node_2")
    graph.add_edge("node_1", "node_3")
    graph.add_edge("node_2", "node_3")
    graph.add_edge("node_3", "node_4")

    graph.set_start("node_0")
    graph.add_end("node_4")

    # 分析图
    print(f"节点数量: {graph.node_count()}")
    print(f"边数量: {graph.edge_count()}")

    # 验证图
    valid, errors = graph.validate()
    print(f"图验证: {valid}")
    if errors:
        print(f"错误: {errors}")

    # 查找路径
    paths = graph.find_all_paths("node_0", "node_4")
    print(f"从 node_0 到 node_4 的所有路径:")
    for i, path in enumerate(paths):
        print(f"  路径 {i+1}: {' -> '.join(path)}")

    # 执行图
    executor = GraphExecutor(graph)
    context = await executor.execute(initial_input="测试数据")
    print(f"执行完成，共执行 {len(context.execution_history)} 个节点")