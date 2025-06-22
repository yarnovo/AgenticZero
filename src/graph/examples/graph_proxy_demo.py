#!/usr/bin/env python3
"""
图代理API演示

展示如何使用GraphProxy操作内存中的图结构。
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.graph import GraphProxy, TaskNode


def demo_basic_operations():
    """演示基础操作"""
    print("=== 基础操作演示 ===\n")

    # 创建图代理
    proxy = GraphProxy.create("演示工作流", "展示GraphProxy的基本功能")
    print(f"创建图代理: {proxy.name}")

    # 添加节点
    print("\n添加节点:")
    proxy.add_node("start", "TaskNode", "开始")
    print("  ✓ 添加开始节点")

    proxy.add_node(
        "process",
        "BranchControlNode",
        "处理分支",
        condition_func=lambda x: "high" if x > 50 else "low",
    )
    print("  ✓ 添加分支节点")

    proxy.add_node("high_path", "TaskNode", "高优先级处理")
    proxy.add_node("low_path", "TaskNode", "低优先级处理")
    proxy.add_node("end", "TaskNode", "结束")
    print("  ✓ 添加其他节点")

    # 添加边
    print("\n添加边:")
    proxy.add_edge("start", "process")
    proxy.add_edge("process", "high_path", action="high", weight=2.0)
    proxy.add_edge("process", "low_path", action="low")
    proxy.add_edge("high_path", "end")
    proxy.add_edge("low_path", "end")
    print("  ✓ 添加所有连接")

    # 设置起始和结束节点
    proxy.set_start_node("start")
    proxy.add_end_node("end")
    print("\n设置起始节点: start")
    print("设置结束节点: end")

    # 验证
    if proxy.is_valid():
        print("\n✅ 图结构验证通过")
    else:
        print("\n❌ 图结构验证失败:")
        for error in proxy.get_validation_errors():
            print(f"  - {error}")

    return proxy


def demo_graph_analysis(proxy: GraphProxy):
    """演示图分析功能"""
    print("\n\n=== 图分析功能演示 ===\n")

    # 路径查找
    print("路径查找:")
    paths = proxy.find_all_paths("start", "end")
    print(f"  从start到end共有 {len(paths)} 条路径:")
    for i, path in enumerate(paths, 1):
        print(f"    路径{i}: {' -> '.join(path)}")

    # 邻居查询
    print("\n邻居查询:")
    neighbors = proxy.get_neighbors("process")
    print(f"  process节点的邻居: {neighbors}")

    predecessors = proxy.get_predecessors("end")
    print(f"  end节点的前驱: {predecessors}")

    # 环检测
    print("\n环检测:")
    cycles = proxy.detect_cycles()
    if cycles:
        print(f"  发现 {len(cycles)} 个环")
    else:
        print("  ✓ 图中无环")

    # 拓扑排序
    print("\n拓扑排序:")
    try:
        order = proxy.topological_sort()
        print(f"  排序结果: {' -> '.join(order)}")
    except ValueError as e:
        print(f"  ❌ 无法排序: {e}")


def demo_statistics(proxy: GraphProxy):
    """演示统计功能"""
    print("\n\n=== 统计信息演示 ===\n")

    stats = proxy.get_statistics()
    print(f"节点总数: {stats['node_count']}")
    print(f"边总数: {stats['edge_count']}")
    print(f"是否有环: {'是' if stats['has_cycles'] else '否'}")
    print(f"起始节点: {stats['start_node']}")
    print(f"结束节点数: {stats['end_node_count']}")

    print("\n节点类型分布:")
    for node_type, count in stats["node_types"].items():
        print(f"  {node_type}: {count}")

    print(f"\n最大入度: {stats['max_in_degree']}")
    print(f"最大出度: {stats['max_out_degree']}")


def demo_serialization(proxy: GraphProxy):
    """演示序列化功能"""
    print("\n\n=== 序列化功能演示 ===\n")

    # 导出为字典
    data = proxy.to_dict()
    print("导出为字典:")
    print(f"  图名称: {data['name']}")
    print(f"  节点数: {len(data['nodes'])}")
    print(f"  边数: {len(data['edges'])}")

    # 导出为JSON
    json_str = proxy.to_json()
    print("\n导出为JSON (前100字符):")
    print(f"  {json_str[:100]}...")

    # 从字典恢复
    print("\n从字典恢复:")
    proxy2 = GraphProxy.from_dict(data)
    print(f"  ✓ 恢复成功，节点数: {proxy2.graph.node_count()}")


def demo_advanced_operations():
    """演示高级操作"""
    print("\n\n=== 高级操作演示 ===\n")

    # 创建序列
    proxy = GraphProxy.create("序列演示")
    print("添加节点序列:")
    proxy.add_sequence(["step1", "step2", "step3", "step4"])
    print("  ✓ 创建了4步序列")

    # 批量操作
    print("\n批量添加节点:")
    nodes = [
        ("batch1", "TaskNode", "批量节点1", {}),
        ("batch2", "TaskNode", "批量节点2", {"priority": "high"}),
    ]
    count = proxy.add_nodes_batch(nodes)
    print(f"  ✓ 成功添加 {count} 个节点")

    # 克隆
    print("\n克隆操作:")
    cloned = proxy.clone()
    print(f"  ✓ 克隆成功，新图有 {cloned.graph.node_count()} 个节点")

    # 合并
    print("\n合并操作:")
    other = GraphProxy.create("子工作流")
    other.add_sequence(["sub1", "sub2"])

    if proxy.merge(other, prefix="merged_"):
        print("  ✓ 合并成功")
        print(f"  合并后节点数: {proxy.graph.node_count()}")

    # 自定义节点类型
    print("\n注册自定义节点类型:")

    class DataProcessorNode(TaskNode):
        """自定义数据处理节点"""

        def __init__(self, node_id, name, **kwargs):
            super().__init__(node_id, name, **kwargs)
            self.processor_type = kwargs.get("processor_type", "default")

    proxy.register_node_type("DataProcessorNode", DataProcessorNode)
    proxy.add_node(
        "custom", "DataProcessorNode", "自定义处理器", processor_type="advanced"
    )
    print("  ✓ 注册并添加自定义节点")

    # 验证自定义节点
    custom_node = proxy.get_node("custom")
    if hasattr(custom_node, "processor_type"):
        print(f"  自定义节点处理器类型: {custom_node.processor_type}")


def demo_error_handling():
    """演示错误处理"""
    print("\n\n=== 错误处理演示 ===\n")

    proxy = GraphProxy.create("错误演示")

    # 添加重复节点
    print("尝试添加重复节点:")
    proxy.add_node("node1", "TaskNode")
    if not proxy.add_node("node1", "TaskNode"):
        print("  ✓ 正确拒绝了重复节点")

    # 添加无效边
    print("\n尝试添加无效边:")
    if not proxy.add_edge("node1", "nonexistent"):
        print("  ✓ 正确拒绝了无效边")

    # 验证不完整的图
    print("\n验证不完整的图:")
    proxy.add_node("isolated", "TaskNode", "孤立节点")
    valid, errors = proxy.validate()
    if not valid:
        print("  验证失败，错误信息:")
        for error in errors[:3]:  # 只显示前3个错误
            print(f"    - {error}")
        if len(errors) > 3:
            print(f"    ... 还有 {len(errors) - 3} 个错误")


def main():
    """主函数"""
    print("GraphProxy API 演示程序")
    print("=" * 40)

    # 基础操作
    proxy = demo_basic_operations()

    # 图分析
    demo_graph_analysis(proxy)

    # 统计信息
    demo_statistics(proxy)

    # 序列化
    demo_serialization(proxy)

    # 高级操作
    demo_advanced_operations()

    # 错误处理
    demo_error_handling()

    print("\n\n演示完成！")


if __name__ == "__main__":
    main()
