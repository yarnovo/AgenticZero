"""
并行工作流示例

演示Fork/Join模式和异常处理
"""

import asyncio
import random
from typing import Any

from src.graph import (
    CircuitBreakerNode,
    EnhancedGraph,
    ForkControlNode,
    JoinControlNode,
    ResumableExecutor,
    RetryNode,
    TaskNode,
    TimeoutNode,
    TryCatchNode,
)


# 模拟的任务节点
class SimulatedTask(TaskNode):
    """模拟耗时任务"""

    def __init__(
        self, node_id: str, name: str, duration: float = 1.0, fail_rate: float = 0.0
    ):
        super().__init__(node_id, name)
        self.duration = duration
        self.fail_rate = fail_rate

    async def _execute_task(self, input_data: Any) -> Any:
        """执行模拟任务"""
        print(f"[{self.node_id}] 开始执行，预计耗时 {self.duration}秒")

        # 模拟失败
        if random.random() < self.fail_rate:
            raise Exception(f"{self.node_id} 模拟失败")

        # 模拟耗时操作
        await asyncio.sleep(self.duration)

        result = {
            "node": self.node_id,
            "input": input_data,
            "output": f"processed_by_{self.node_id}",
            "duration": self.duration,
        }

        print(f"[{self.node_id}] 执行完成")
        return result


async def main():
    """主函数"""
    print("=== 并行工作流示例 ===\n")

    # 创建图
    graph = EnhancedGraph("parallel_workflow")

    # 创建节点
    start = TaskNode("start", "开始")
    start.process_func = lambda x: {"initial_data": x, "timestamp": "2024-01-01"}

    # Fork节点 - 分叉为3个并行任务
    fork = ForkControlNode("fork", "分叉", fork_count=3)

    # 并行任务
    task_a = SimulatedTask("task_a", "任务A", duration=1.0)
    task_b = SimulatedTask("task_b", "任务B", duration=1.5)
    task_c = SimulatedTask("task_c", "任务C", duration=0.8)

    # Join节点 - 汇聚结果
    def join_results(results):
        """汇聚函数"""
        return {"joined": True, "results": results, "task_count": len(results)}

    join = JoinControlNode("join", "汇聚", join_func=join_results)

    # 结束节点
    end = TaskNode("end", "结束")
    end.process_func = lambda x: {"final": x, "status": "completed"}

    # 构建图
    nodes = [start, fork, task_a, task_b, task_c, join, end]
    for node in nodes:
        graph.add_node(node)

    # 连接节点
    graph.add_edge("start", "fork")
    graph.add_edge("fork", "task_a")
    graph.add_edge("fork", "task_b")
    graph.add_edge("fork", "task_c")
    graph.add_edge("task_a", "join")
    graph.add_edge("task_b", "join")
    graph.add_edge("task_c", "join")
    graph.add_edge("join", "end")

    # 设置起始和结束
    graph.set_start("start")
    graph.add_end("end")

    # 验证图
    graph.validate()

    # 执行
    executor = ResumableExecutor(graph)

    print("执行并行工作流...")
    context = await executor.execute_with_checkpoints(initial_input="parallel_test")

    print(f"\n并行执行完成，总耗时: {context.duration:.2f}秒")
    print(f"最终结果: {context.graph_output}")

    # ===== 异常处理示例 =====
    print("\n\n=== 异常处理工作流 ===\n")

    graph2 = EnhancedGraph("exception_workflow")

    # 创建会失败的任务
    unreliable_task = SimulatedTask(
        "unreliable", "不可靠任务", duration=0.5, fail_rate=0.7
    )

    # 重试节点
    retry_task = RetryNode(
        "retry",
        "重试任务",
        target_func=unreliable_task.process_func,
        max_retries=3,
        retry_delay=0.5,
    )

    # 超时控制节点
    timeout_task = TimeoutNode(
        "timeout",
        "超时任务",
        target_func=lambda x: asyncio.sleep(5),  # 会超时的任务
        timeout_seconds=2.0,
    )

    # Try-Catch节点
    def safe_process(data):
        if random.random() < 0.3:
            raise ValueError("随机错误")
        return {"processed": data}

    def handle_error(data, error):
        return {"error_handled": True, "original_error": str(error)}

    try_catch = TryCatchNode(
        "try_catch", "安全处理", try_func=safe_process, catch_func=handle_error
    )

    # 熔断器节点
    circuit_breaker = CircuitBreakerNode(
        "circuit",
        "熔断器",
        target_func=lambda x: {"protected": x},
        failure_threshold=3,
        timeout_seconds=5.0,
    )

    # 构建异常处理流程
    start2 = TaskNode("start2", "开始2")
    start2.process_func = lambda x: {"test_data": x}

    end2 = TaskNode("end2", "结束2")
    end2.process_func = lambda x: {"completed": x}

    # 添加节点
    exception_nodes = [
        start2,
        retry_task,
        timeout_task,
        try_catch,
        circuit_breaker,
        end2,
    ]
    for node in exception_nodes:
        graph2.add_node(node)

    # 连接节点（串行执行各种异常处理）
    graph2.add_edge("start2", "retry")
    graph2.add_edge("retry", "timeout")
    graph2.add_edge("timeout", "try_catch")
    graph2.add_edge("try_catch", "circuit")
    graph2.add_edge("circuit", "end2")

    graph2.set_start("start2")
    graph2.add_end("end2")

    # 执行异常处理流程
    executor2 = ResumableExecutor(graph2)

    # 注册错误处理钩子
    def on_error(node, error):
        print(f"❌ 节点 {node.node_id} 发生错误: {error}")

    executor2.register_hook("node_error", on_error)

    print("执行异常处理工作流...")
    try:
        context2 = await executor2.execute_with_checkpoints(
            initial_input="exception_test"
        )
        print(f"\n异常处理完成: {context2.graph_output}")
    except Exception as e:
        print(f"\n工作流执行失败: {e}")

    # 显示各节点的执行结果
    print("\n各节点执行结果:")
    for node_id, output in context2.node_outputs.items():
        print(f"  {node_id}: {output}")

    # ===== 复杂并行+异常处理示例 =====
    print("\n\n=== 复杂工作流（并行+异常处理）===\n")

    graph3 = EnhancedGraph("complex_workflow")

    # 创建一个包含并行任务和异常处理的复杂流程
    start3 = TaskNode("start3", "开始3")
    start3.process_func = lambda x: {"complex_data": x}

    # Fork为两个分支
    fork2 = ForkControlNode("fork2", "分叉2", fork_count=2)

    # 分支1：带重试的任务
    branch1 = RetryNode(
        "branch1",
        "分支1-重试",
        target_func=lambda x: {"branch1": x} if random.random() > 0.3 else 1 / 0,
        max_retries=2,
    )

    # 分支2：带超时的任务
    async def long_task(x):
        await asyncio.sleep(1)
        return {"branch2": x}

    branch2 = TimeoutNode(
        "branch2", "分支2-超时", target_func=long_task, timeout_seconds=2.0
    )

    # 汇聚结果
    join2 = JoinControlNode("join2", "汇聚2")

    # 最终处理
    final = TaskNode("final", "最终处理")
    final.process_func = lambda x: {"final_result": x, "workflow": "complex"}

    # 构建复杂图
    complex_nodes = [start3, fork2, branch1, branch2, join2, final]
    for node in complex_nodes:
        graph3.add_node(node)

    graph3.add_edge("start3", "fork2")
    graph3.add_edge("fork2", "branch1")
    graph3.add_edge("fork2", "branch2")
    graph3.add_edge("branch1", "join2")
    graph3.add_edge("branch2", "join2")
    graph3.add_edge("join2", "final")

    graph3.set_start("start3")
    graph3.add_end("final")

    # 执行复杂流程
    executor3 = ResumableExecutor(graph3)

    print("执行复杂工作流...")
    context3 = await executor3.execute_with_checkpoints(initial_input="complex_test")

    print("\n复杂工作流执行完成!")
    print(f"最终结果: {context3.graph_output}")
    print(f"总耗时: {context3.duration:.2f}秒")


if __name__ == "__main__":
    asyncio.run(main())
