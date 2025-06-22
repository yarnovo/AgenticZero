"""
图使用示例

展示如何使用图数据结构创建工作流
"""

import asyncio
import os
import sys

# 添加src目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from graph import ConditionalNode, DataProcessorNode, Graph, GraphExecutor, LoggingNode


async def example_tax_calculation():
    """税务计算工作流示例"""
    print("\n=== 税务计算工作流 ===")

    # 定义处理函数
    def validate_amount(amount):
        """验证金额是否有效"""
        return isinstance(amount, int | float) and amount > 0

    def calculate_tax(amount):
        """计算税费（20%税率）"""
        tax = amount * 0.2
        return {"amount": amount, "tax": tax, "total": amount + tax}

    def format_result(data):
        """格式化结果"""
        if isinstance(data, dict):
            return (
                f"金额: ¥{data['amount']:.2f}\n"
                f"税费: ¥{data['tax']:.2f}\n"
                f"总计: ¥{data['total']:.2f}"
            )
        return "无效数据"

    # 创建节点
    start = LoggingNode("start", "开始", "开始税务计算流程")

    # 验证输入
    validate = DataProcessorNode("validate", "验证输入", processor_func=validate_amount)
    validate.metadata["input_data"] = 1000  # 示例输入

    # 计算税费
    calculate = DataProcessorNode("calculate", "计算税费", processor_func=calculate_tax)

    # 格式化输出
    format_node = DataProcessorNode(
        "format", "格式化结果", processor_func=format_result
    )

    # 错误处理
    error = LoggingNode("error", "错误处理", "输入金额无效！")

    # 成功完成
    complete = LoggingNode("complete", "完成", "税务计算完成！")

    # 构建图
    start >> validate
    validate - "success" >> calculate >> format_node >> complete
    validate - "failure" >> error

    # 配置图
    graph = complete._temp_graph
    graph.set_start("start")
    graph.add_end("complete")
    graph.add_end("error")

    # 创建执行器并添加数据传递钩子
    executor = GraphExecutor(graph)

    def pass_data(node, action, context, **kwargs):
        """在节点间传递数据"""
        if hasattr(node, "result") and node.result is not None:
            next_node_id = graph.get_next_node_id(node.node_id, action)
            if next_node_id:
                next_node = graph.get_node(next_node_id)
                if next_node and hasattr(next_node, "metadata"):
                    next_node.metadata["input_data"] = node.result

    executor.add_hook("after_node", pass_data)

    # 执行工作流
    context = await executor.execute()

    # 显示结果
    print(f"\n执行耗时: {context.duration:.2f} 秒")
    print("\n执行路径:")
    for entry in context.execution_history:
        if entry["result"]:
            print(f"  {entry['node_id']}: {entry['result']}")

    # 获取最终结果
    for entry in reversed(context.execution_history):
        if entry["node_id"] == "format":
            print(f"\n最终结果:\n{entry['result']}")
            break


async def example_approval_workflow():
    """审批工作流示例"""
    print("\n\n=== 审批工作流 ===")

    # 创建图
    graph = Graph("审批流程")

    # 审批条件函数
    def check_amount(amount):
        """检查金额是否需要高级审批"""
        return amount > 10000

    def check_department(dept):
        """检查部门是否需要特殊审批"""
        return dept in ["财务部", "采购部"]

    # 创建节点
    start = LoggingNode("start", "开始", "开始审批流程")

    # 金额检查
    amount_check = ConditionalNode(
        "amount_check",
        "金额检查",
        lambda: check_amount(15000),  # 示例：15000元
    )

    # 部门检查
    dept_check = ConditionalNode(
        "dept_check",
        "部门检查",
        lambda: check_department("财务部"),  # 示例：财务部
    )

    # 各级审批
    manager_approval = LoggingNode("manager", "经理审批", "✓ 经理已批准")

    director_approval = LoggingNode("director", "总监审批", "✓ 总监已批准")

    cfo_approval = LoggingNode("cfo", "财务总监审批", "✓ 财务总监已批准")

    # 结果节点
    approved = LoggingNode("approved", "批准", "✓ 审批通过！")

    rejected = LoggingNode("rejected", "拒绝", "✗ 审批被拒绝")

    # 添加节点到图
    for node in [
        start,
        amount_check,
        dept_check,
        manager_approval,
        director_approval,
        cfo_approval,
        approved,
        rejected,
    ]:
        graph.add_node(node.node_id, node)

    # 创建审批流程
    graph.add_edge("start", "amount_check")

    # 金额检查分支
    graph.add_edge("amount_check", "dept_check", "true")  # 大额需要进一步检查
    graph.add_edge("amount_check", "manager", "false")  # 小额只需经理审批

    # 部门检查分支
    graph.add_edge("dept_check", "cfo", "true")  # 特殊部门需要CFO审批
    graph.add_edge("dept_check", "director", "false")  # 其他部门需要总监审批

    # 审批路径
    graph.add_edge("manager", "approved")
    graph.add_edge("director", "approved")
    graph.add_edge("cfo", "approved")

    # 配置图
    graph.set_start("start")
    graph.add_end("approved")
    graph.add_end("rejected")

    # 执行
    executor = GraphExecutor(graph)
    context = await executor.execute()

    print(
        f"\n审批路径: {' -> '.join([h['node_id'] for h in context.execution_history])}"
    )


async def example_data_pipeline():
    """数据处理管道示例"""
    print("\n\n=== 数据处理管道 ===")

    # 数据处理函数
    def load_data(input_data):
        """加载数据"""
        return [1, 2, 3, 4, 5]

    def filter_data(data):
        """过滤数据（只保留偶数）"""
        return [x for x in data if x % 2 == 0]

    def transform_data(data):
        """转换数据（平方）"""
        return [x**2 for x in data]

    def aggregate_data(data):
        """聚合数据（求和）"""
        return sum(data)

    def save_result(result):
        """保存结果"""
        return f"结果已保存: {result}"

    # 创建管道节点
    load = DataProcessorNode("load", "加载数据", load_data)
    filter_node = DataProcessorNode("filter", "过滤数据", filter_data)
    transform = DataProcessorNode("transform", "转换数据", transform_data)
    aggregate = DataProcessorNode("aggregate", "聚合数据", aggregate_data)
    save = DataProcessorNode("save", "保存结果", save_result)

    # 构建管道
    load >> filter_node >> transform >> aggregate >> save

    # 获取图
    graph = save._temp_graph
    graph.set_start("load")
    graph.add_end("save")

    # 创建执行器
    executor = GraphExecutor(graph)

    # 数据传递钩子
    def pass_data(node, action, context, **kwargs):
        if hasattr(node, "result") and node.result is not None:
            next_node_id = graph.get_next_node_id(node.node_id, action)
            if next_node_id:
                next_node = graph.get_node(next_node_id)
                if next_node:
                    next_node.metadata["input_data"] = node.result

    executor.add_hook("after_node", pass_data)

    # 执行管道
    context = await executor.execute()

    print("\n数据处理步骤:")
    for entry in context.execution_history:
        print(f"  {entry['node_id']}: {entry['result']}")

    print(f"\n管道执行完成，耗时: {context.duration:.2f} 秒")


async def main():
    """运行所有示例"""
    print("图工作流示例")
    print("=" * 50)

    await example_tax_calculation()
    await example_approval_workflow()
    await example_data_pipeline()

    print("\n\n所有示例执行完成！")


if __name__ == "__main__":
    asyncio.run(main())
