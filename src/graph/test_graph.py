"""
图实现测试

测试各种图功能和节点类型
"""

import os
import sys

import pytest

# 添加src目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from graph import (
    ConditionalNode,
    DataProcessorNode,
    ErrorNode,
    Graph,
    GraphExecutor,
    LoggingNode,
    RandomChoiceNode,
    SimpleNode,
)


@pytest.mark.asyncio
@pytest.mark.unit
async def test_basic_graph():
    """测试基本图功能"""
    print("\n=== 测试基本图功能 ===")

    # 创建节点
    start = SimpleNode("start", "开始节点")
    process = SimpleNode("process", "处理节点")
    end = SimpleNode("end", "结束节点")

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
    context = await executor.execute()

    print(f"执行完成，耗时 {context.duration:.2f} 秒")
    print(f"执行历史: {len(context.execution_history)} 个节点")

    for entry in context.execution_history:
        print(f"  - {entry['node_id']}: {entry['result']}")


@pytest.mark.asyncio
@pytest.mark.unit
async def test_conditional_graph():
    """测试条件分支图"""
    print("\n=== 测试条件分支图 ===")

    # 创建图
    graph = Graph("条件流程")

    # 创建节点
    start = LoggingNode("start", "开始", "开始条件流程")
    check = ConditionalNode("check", "检查条件", lambda: True)  # 总是返回True
    if_true = LoggingNode("if_true", "真分支", "条件为真")
    if_false = LoggingNode("if_false", "假分支", "条件为假")
    end = LoggingNode("end", "结束", "流程结束")

    # 添加节点到图
    graph.add_node("start", start)
    graph.add_node("check", check)
    graph.add_node("if_true", if_true)
    graph.add_node("if_false", if_false)
    graph.add_node("end", end)

    # 添加边
    graph.add_edge("start", "check")
    graph.add_edge("check", "if_true", "true")
    graph.add_edge("check", "if_false", "false")
    graph.add_edge("if_true", "end")
    graph.add_edge("if_false", "end")

    graph.set_start("start")
    graph.add_end("end")

    # 执行
    executor = GraphExecutor(graph)
    context = await executor.execute()

    print(f"执行路径: {' -> '.join([h['node_id'] for h in context.execution_history])}")


@pytest.mark.asyncio
@pytest.mark.unit
async def test_data_processing_graph():
    """测试数据处理管道"""
    print("\n=== 测试数据处理管道 ===")

    # 处理函数
    def multiply_by_2(x):
        """乘以2"""
        return x * 2

    def add_10(x):
        """加10"""
        return x + 10

    def to_string(x):
        """转换为字符串"""
        return f"结果: {x}"

    # 创建节点
    start = DataProcessorNode("start", "输入", lambda x: 5)
    multiply = DataProcessorNode("multiply", "乘法", multiply_by_2)
    add = DataProcessorNode("add", "加法", add_10)
    format_result = DataProcessorNode("format", "格式化", to_string)

    # 链式操作
    start >> multiply >> add >> format_result

    # 获取图并配置
    graph = format_result._temp_graph
    graph.set_start("start")
    graph.add_end("format")

    # 创建执行器
    executor = GraphExecutor(graph)

    # 添加数据传递钩子
    def pass_data(node, action, context, **kwargs):
        """在节点间传递数据"""
        if hasattr(node, "result") and node.result is not None:
            # 将结果传递给下一个节点
            next_node_id = graph.get_next_node_id(node.node_id, action)
            if next_node_id:
                next_node = graph.get_node(next_node_id)
                if next_node:
                    next_node.metadata["input_data"] = node.result

    executor.add_hook("after_node", pass_data)

    context = await executor.execute()

    print("数据处理结果:")
    for entry in context.execution_history:
        print(f"  {entry['node_id']}: {entry['result']}")


@pytest.mark.asyncio
@pytest.mark.unit
async def test_random_choice_graph():
    """测试随机选择图"""
    print("\n=== 测试随机选择图 ===")

    # 创建节点
    start = LoggingNode("start", "开始", "开始随机流程")
    choice = RandomChoiceNode(
        "choice",
        "随机选择",
        {
            "path_a": 0.6,  # 60% 概率
            "path_b": 0.3,  # 30% 概率
            "path_c": 0.1,  # 10% 概率
        },
    )
    path_a = LoggingNode("path_a", "路径A", "选择了路径A (60%概率)")
    path_b = LoggingNode("path_b", "路径B", "选择了路径B (30%概率)")
    path_c = LoggingNode("path_c", "路径C", "选择了路径C (10%概率)")
    end = LoggingNode("end", "结束", "随机流程结束")

    # 使用条件操作符构建图
    start >> choice
    choice - "path_a" >> path_a >> end
    choice - "path_b" >> path_b >> end
    choice - "path_c" >> path_c >> end

    # 获取图
    graph = end._temp_graph
    graph.set_start("start")
    graph.add_end("end")

    # 执行多次以查看分布
    print("运行10次迭代:")
    path_counts = {"path_a": 0, "path_b": 0, "path_c": 0}

    for i in range(10):
        executor = GraphExecutor(graph)
        context = await executor.execute()

        # 查找选择的路径
        for entry in context.execution_history:
            if entry["node_id"] in path_counts:
                path_counts[entry["node_id"]] += 1

    print(f"路径分布: {path_counts}")


@pytest.mark.asyncio
@pytest.mark.unit
async def test_error_handling():
    """测试错误处理"""
    print("\n=== 测试错误处理 ===")

    # 创建带错误处理的图
    graph = Graph("错误流程")

    start = LoggingNode("start", "开始", "开始错误流程")
    risky_op = ErrorNode("risky", "风险操作", "出错了！")
    error_handler = LoggingNode("error_handler", "错误处理", "优雅地处理错误")
    success = LoggingNode("success", "成功", "操作成功")
    end = LoggingNode("end", "结束", "流程结束")

    # 添加节点
    for node in [start, risky_op, error_handler, success, end]:
        graph.add_node(node.node_id, node)

    # 添加边
    graph.add_edge("start", "risky")
    graph.add_edge("risky", "success", "default")
    graph.add_edge("risky", "error_handler", "error")
    graph.add_edge("success", "end")
    graph.add_edge("error_handler", "end")

    graph.set_start("start")
    graph.add_end("end")

    # 执行错误处理
    executor = GraphExecutor(graph)
    context = None

    try:
        context = await executor.execute()
    except Exception as e:
        print(f"捕获错误: {e}")
        context = executor.context

    if context:
        print("执行历史:")
        for entry in context.execution_history:
            print(f"  {entry['node_id']}: {entry.get('error', entry.get('result'))}")


@pytest.mark.asyncio
@pytest.mark.unit
async def test_graph_analysis():
    """测试图分析功能"""
    print("\n=== 测试图分析功能 ===")

    # 创建复杂图
    graph = Graph("复杂流程")

    # 创建节点
    nodes = {
        "A": SimpleNode("A", "节点A"),
        "B": SimpleNode("B", "节点B"),
        "C": SimpleNode("C", "节点C"),
        "D": SimpleNode("D", "节点D"),
        "E": SimpleNode("E", "节点E"),
        "F": SimpleNode("F", "节点F"),
    }

    # 添加所有节点
    for node_id, node in nodes.items():
        graph.add_node(node_id, node)

    # 创建边（包含一个环）
    graph.add_edge("A", "B")
    graph.add_edge("A", "C")
    graph.add_edge("B", "D")
    graph.add_edge("C", "D")
    graph.add_edge("D", "E")
    graph.add_edge("E", "F")
    graph.add_edge("F", "C")  # 创建环: C -> D -> E -> F -> C

    graph.set_start("A")
    graph.add_end("F")

    # 分析图
    print(f"图: {graph}")
    print(f"存在路径 A->F: {graph.has_path('A', 'F')}")
    print(f"存在路径 F->A: {graph.has_path('F', 'A')}")

    # 查找所有路径
    paths = graph.find_all_paths("A", "F")
    print(f"从A到F的所有路径: 找到 {len(paths)} 条")
    for i, path in enumerate(paths[:3]):  # 显示前3条路径
        print(f"  路径 {i + 1}: {' -> '.join(path)}")

    # 检测环
    cycles = graph.detect_cycles()
    print(f"检测到的环: {len(cycles)} 个")
    for cycle in cycles:
        print(f"  环: {' -> '.join(cycle)}")

    # 图指标
    print(f"节点数: {graph.node_count()}")
    print(f"边数: {graph.edge_count()}")

    # 邻居和前驱
    print(f"D的邻居: {graph.get_neighbors('D')}")
    print(f"D的前驱: {graph.get_predecessors('D')}")

    # 导出为JSON
    print("\n图的JSON表示:")
    print(graph.to_json())


# 移除了 main() 函数和 if __name__ == "__main__" 块
# 这些测试现在只能通过 pytest 运行
# 如果需要单独运行，使用: pytest src/graph/test_graph.py -v
