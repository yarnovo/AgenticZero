"""高级控制流模式示例

使用原子节点组合实现复杂的控制流模式：
- 循环：分支节点 + 合并节点
- 条件执行：分支节点 + 合并节点
- 并行执行：分叉节点 + 汇聚节点
- 异常处理：分支节点的特殊应用
"""

import asyncio
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.graph import (
    BranchNode,
    Edge,
    ForkNode,
    Graph,
    GraphExecutor,
    JoinNode,
    MergeNode,
    SequenceNode,
)


async def example_loop_pattern():
    """循环模式：使用分支和合并节点形成回路"""
    print("\n=== 循环模式示例 ===")
    print("计算1到N的累加和")

    graph = Graph()

    # 初始化节点
    init_node = SequenceNode(
        "init", "初始化", lambda _: {"sum": 0, "current": 1, "max": 5}
    )

    # 合并节点（循环入口）
    merge_node = MergeNode("merge", "循环入口")

    # 累加节点
    accumulate_node = SequenceNode(
        "accumulate",
        "累加",
        lambda data: {
            "sum": data["sum"] + data["current"],
            "current": data["current"] + 1,
            "max": data["max"],
        },
    )

    # 分支节点（循环条件）
    branch_node = BranchNode(
        "check",
        "检查条件",
        lambda data: "continue" if data["current"] <= data["max"] else "done",
    )

    # 输出节点
    output_node = SequenceNode(
        "output", "输出结果", lambda data: f"1到{data['max']}的和为: {data['sum']}"
    )

    # 构建图
    for node in [init_node, merge_node, accumulate_node, branch_node, output_node]:
        graph.add_node(node)

    # 连接节点形成循环
    graph.add_edge(Edge("init", "merge"))
    graph.add_edge(Edge("merge", "accumulate"))
    graph.add_edge(Edge("accumulate", "check"))
    graph.add_edge(Edge("check", "merge", action="continue"))  # 循环回边
    graph.add_edge(Edge("check", "output", action="done"))  # 退出循环

    graph.set_start_node("init")

    # 执行
    executor = GraphExecutor(graph)
    context = await executor.execute()

    print(
        f"循环执行了 {len([h for h in context.execution_history if h['node_id'] == 'accumulate'])} 次"
    )


async def example_conditional_execution():
    """条件执行模式：根据条件选择执行路径"""
    print("\n=== 条件执行模式示例 ===")
    print("用户权限检查系统")

    graph = Graph()

    # 输入用户信息
    input_node = SequenceNode(
        "input",
        "输入用户",
        lambda _: {
            "user": "admin",
            "role": "admin",
            "permissions": ["read", "write", "delete"],
        },
    )

    # 权限检查分支
    auth_check = BranchNode(
        "auth_check",
        "权限检查",
        lambda data: "admin" if data["role"] == "admin" else "user",
    )

    # 管理员路径
    admin_process = SequenceNode(
        "admin_process",
        "管理员处理",
        lambda data: {**data, "access": "full", "message": "欢迎管理员！"},
    )

    # 普通用户路径
    user_process = SequenceNode(
        "user_process",
        "用户处理",
        lambda data: {**data, "access": "limited", "message": "欢迎用户！"},
    )

    # 合并路径
    merge_node = MergeNode("merge", "合并路径")

    # 最终处理
    final_node = SequenceNode(
        "final",
        "最终处理",
        lambda data: f"{data['message']} 访问级别: {data['access']}",
    )

    # 构建图
    for node in [
        input_node,
        auth_check,
        admin_process,
        user_process,
        merge_node,
        final_node,
    ]:
        graph.add_node(node)

    graph.add_edge(Edge("input", "auth_check"))
    graph.add_edge(Edge("auth_check", "admin_process", action="admin"))
    graph.add_edge(Edge("auth_check", "user_process", action="user"))
    graph.add_edge(Edge("admin_process", "merge"))
    graph.add_edge(Edge("user_process", "merge"))
    graph.add_edge(Edge("merge", "final"))

    graph.set_start_node("input")

    # 执行
    executor = GraphExecutor(graph)
    await executor.execute()


async def example_parallel_execution():
    """并行执行模式：同时执行多个任务"""
    print("\n=== 并行执行模式示例 ===")
    print("并行数据处理管道")

    graph = Graph()

    # 输入数据
    input_node = SequenceNode(
        "input",
        "输入数据",
        lambda _: {"data": [1, 2, 3, 4, 5], "config": {"multiplier": 2}},
    )

    # 分叉节点：开始并行处理
    fork_node = ForkNode("fork", "开始并行")

    # 并行任务1：计算总和
    sum_task = SequenceNode(
        "sum_task", "求和任务", lambda data: {"sum": sum(data["data"]), "task": "sum"}
    )

    # 并行任务2：计算平均值
    avg_task = SequenceNode(
        "avg_task",
        "平均值任务",
        lambda data: {"avg": sum(data["data"]) / len(data["data"]), "task": "avg"},
    )

    # 并行任务3：计算最大最小值
    minmax_task = SequenceNode(
        "minmax_task",
        "最大最小值任务",
        lambda data: {
            "min": min(data["data"]),
            "max": max(data["data"]),
            "task": "minmax",
        },
    )

    # 汇聚节点：等待所有任务完成
    join_node = JoinNode(
        "join",
        "汇聚结果",
        lambda results: {
            "summary": {
                task_result.get("task", "unknown"): {
                    k: v for k, v in task_result.items() if k != "task"
                }
                for task_result in results
            }
        },
        expected_inputs=3,
    )

    # 输出结果
    output_node = SequenceNode(
        "output", "输出结果", lambda data: f"统计结果: {data['summary']}"
    )

    # 构建图
    for node in [
        input_node,
        fork_node,
        sum_task,
        avg_task,
        minmax_task,
        join_node,
        output_node,
    ]:
        graph.add_node(node)

    graph.add_edge(Edge("input", "fork"))
    graph.add_edge(Edge("fork", "sum_task"))
    graph.add_edge(Edge("fork", "avg_task"))
    graph.add_edge(Edge("fork", "minmax_task"))
    graph.add_edge(Edge("sum_task", "join"))
    graph.add_edge(Edge("avg_task", "join"))
    graph.add_edge(Edge("minmax_task", "join"))
    graph.add_edge(Edge("join", "output"))

    graph.set_start_node("input")

    # 执行
    executor = GraphExecutor(graph)
    await executor.execute()


async def example_exception_handling():
    """异常处理模式：使用分支节点处理错误"""
    print("\n=== 异常处理模式示例 ===")
    print("带错误处理的数据验证流程")

    graph = Graph()

    # 输入数据
    input_node = SequenceNode(
        "input", "输入数据", lambda _: {"value": "not_a_number", "retry_count": 0}
    )

    # 数据验证和处理节点（可能出错）
    class ValidateNode(SequenceNode):
        def exec_sync(self, data: Any) -> Any:
            try:
                # 尝试转换为数字
                value = int(data["value"])
                return {
                    "status": "success",
                    "value": value * 2,
                    "retry_count": data["retry_count"],
                }
            except ValueError:
                return {
                    "status": "error",
                    "error": "无效数字",
                    "retry_count": data["retry_count"],
                }

    validate_node = ValidateNode("validate", "验证处理")

    # 错误检查分支
    error_check = BranchNode(
        "error_check",
        "错误检查",
        lambda data: "error" if data["status"] == "error" else "success",
    )

    # 错误处理路径
    error_handler = SequenceNode(
        "error_handler",
        "错误处理",
        lambda data: {
            "value": "0",  # 使用默认值
            "retry_count": data["retry_count"] + 1,
            "message": f"错误: {data.get('error', '未知错误')}，使用默认值",
        },
    )

    # 重试检查
    retry_check = BranchNode(
        "retry_check",
        "重试检查",
        lambda data: "retry" if data["retry_count"] < 3 else "fail",
    )

    # 成功处理
    success_node = SequenceNode(
        "success",
        "成功处理",
        lambda data: f"处理成功！结果: {data.get('value', 'N/A')}",
    )

    # 最终失败
    fail_node = SequenceNode(
        "fail", "最终失败", lambda data: f"处理失败！{data.get('message', '未知错误')}"
    )

    # 合并节点
    merge_node = MergeNode("merge", "合并")

    # 构建图
    for node in [
        input_node,
        validate_node,
        error_check,
        error_handler,
        retry_check,
        success_node,
        fail_node,
        merge_node,
    ]:
        graph.add_node(node)

    # 主流程
    graph.add_edge(Edge("input", "validate"))
    graph.add_edge(Edge("validate", "error_check"))
    graph.add_edge(Edge("error_check", "success", action="success"))
    graph.add_edge(Edge("error_check", "error_handler", action="error"))

    # 错误处理流程
    graph.add_edge(Edge("error_handler", "retry_check"))
    graph.add_edge(Edge("retry_check", "merge", action="retry"))
    graph.add_edge(Edge("retry_check", "fail", action="fail"))
    graph.add_edge(Edge("merge", "validate"))  # 重试循环

    graph.set_start_node("input")

    # 执行
    executor = GraphExecutor(graph, max_iterations=20)
    await executor.execute()


async def main():
    """运行所有高级模式示例"""
    await example_loop_pattern()
    await example_conditional_execution()
    await example_parallel_execution()
    await example_exception_handling()


if __name__ == "__main__":
    asyncio.run(main())
