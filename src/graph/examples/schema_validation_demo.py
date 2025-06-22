"""
Schema验证和配置代理示例

演示如何使用Schema验证器和配置代理对象来操作图配置。
"""

import asyncio
import os
import sys
from pathlib import Path

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from src.graph.config_proxy import GraphConfigProxy
from src.graph.schema import validate_graph_config, validate_graph_config_file


def demo_schema_validation():
    """演示Schema验证功能"""
    print("=== Schema验证演示 ===\n")

    # 1. 有效配置示例
    print("1. 验证有效配置:")
    valid_config = {
        "name": "示例工作流",
        "description": "一个简单的顺序工作流",
        "version": "1.0",
        "nodes": [
            {
                "id": "start",
                "type": "SequenceControlNode",
                "name": "开始节点",
                "description": "工作流起始点",
                "params": {"process_func": "lambda x: x"},
            },
            {
                "id": "process",
                "type": "TaskNode",
                "name": "处理节点",
                "description": "数据处理",
                "params": {"process_func": "lambda x: x * 2"},
            },
            {
                "id": "end",
                "type": "TaskNode",
                "name": "结束节点",
                "description": "输出结果",
            },
        ],
        "edges": [
            {"from": "start", "to": "process", "action": "default", "weight": 1.0},
            {"from": "process", "to": "end", "action": "default", "weight": 1.0},
        ],
        "start_node": "start",
        "end_nodes": ["end"],
        "metadata": {
            "author": "示例作者",
            "category": "演示",
            "tags": ["简单", "顺序"],
        },
    }

    valid, errors = validate_graph_config(valid_config)
    print(f"配置有效: {valid}")
    if errors:
        print(f"错误: {errors}")
    else:
        print("✅ 配置验证通过")

    # 2. 无效配置示例
    print("\n2. 验证无效配置:")
    invalid_config = {
        "name": "",  # 空名称
        "nodes": [
            {
                "id": "invalid_node",
                "type": "NonexistentType",  # 无效类型
                "name": "无效节点",
            },
            {
                "id": "branch_node",
                "type": "BranchControlNode",
                "name": "分支节点",
                # 缺少必需的condition_func参数
            },
        ],
        "edges": [
            {
                "from": "invalid_node",
                "to": "nonexistent_node",  # 引用不存在的节点
            }
        ],
        "start_node": "missing_start",  # 不存在的起始节点
        "end_nodes": ["missing_end"],  # 不存在的结束节点
    }

    valid, errors = validate_graph_config(invalid_config)
    print(f"配置有效: {valid}")
    print("发现的错误:")
    for i, error in enumerate(errors, 1):
        print(f"  {i}. {error}")

    print()


def demo_config_proxy():
    """演示配置代理功能"""
    print("=== 配置代理演示 ===\n")

    # 1. 创建空图
    print("1. 创建空图:")
    proxy = GraphConfigProxy.create_empty("演示工作流", "配置代理演示图")
    print(f"创建的图: {proxy}")

    # 2. 添加节点
    print("\n2. 添加节点:")
    proxy.add_node(
        "input",
        "SequenceControlNode",
        "输入处理",
        "处理输入数据",
        {"process_func": "lambda x: {'input': x}"},
        {"category": "输入"},
    )
    print("✅ 添加输入节点")

    proxy.add_node(
        "branch",
        "BranchControlNode",
        "条件分支",
        "根据条件选择路径",
        {"condition_func": "lambda x: 'high' if x.get('input', 0) > 10 else 'low'"},
        {"category": "控制"},
    )
    print("✅ 添加分支节点")

    proxy.add_node(
        "high_path",
        "TaskNode",
        "高值处理",
        "处理高值情况",
        {"process_func": "lambda x: {'result': x['input'] * 0.9, 'path': 'high'}"},
    )
    print("✅ 添加高值处理节点")

    proxy.add_node(
        "low_path",
        "TaskNode",
        "低值处理",
        "处理低值情况",
        {"process_func": "lambda x: {'result': x['input'] * 1.2, 'path': 'low'}"},
    )
    print("✅ 添加低值处理节点")

    proxy.add_node(
        "output",
        "TaskNode",
        "结果输出",
        "输出最终结果",
        {"process_func": "lambda x: f\"最终结果: {x['result']} (路径: {x['path']})\""},
    )
    print("✅ 添加输出节点")

    # 3. 添加边
    print("\n3. 添加边:")
    proxy.add_edge("input", "branch", "default", 1.0)
    print("✅ 输入 -> 分支")

    proxy.add_edge("branch", "high_path", "high", 1.0)
    print("✅ 分支 -> 高值处理 (条件: high)")

    proxy.add_edge("branch", "low_path", "low", 1.0)
    print("✅ 分支 -> 低值处理 (条件: low)")

    proxy.add_edge("high_path", "output", "default", 1.0)
    print("✅ 高值处理 -> 输出")

    proxy.add_edge("low_path", "output", "default", 1.0)
    print("✅ 低值处理 -> 输出")

    # 4. 设置起始和结束节点
    print("\n4. 设置起始和结束节点:")
    proxy.start_node = "input"
    proxy.add_end_node("output")
    print(f"✅ 起始节点: {proxy.start_node}")
    print(f"✅ 结束节点: {proxy.end_nodes}")

    # 5. 验证配置
    print("\n5. 验证配置:")
    valid, errors = proxy.validate()
    print(f"配置有效: {valid}")
    if errors:
        print("错误:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✅ 配置验证通过")

    # 6. 查看统计信息
    print("\n6. 图统计信息:")
    stats = proxy.get_statistics()
    print(f"  - 节点数量: {stats['node_count']}")
    print(f"  - 边数量: {stats['edge_count']}")
    print(f"  - 节点类型分布: {stats['node_types']}")
    print(f"  - 最大入度: {stats['max_in_degree']}")
    print(f"  - 最大出度: {stats['max_out_degree']}")
    print(f"  - 孤立节点: {stats['isolated_nodes']}")

    return proxy


def demo_advanced_operations(proxy):
    """演示高级操作"""
    print("\n=== 高级操作演示 ===\n")

    # 1. 节点操作
    print("1. 节点查询和过滤:")
    all_nodes = proxy.list_nodes()
    print(f"  - 所有节点: {[node['id'] for node in all_nodes]}")

    task_nodes = proxy.filter_nodes("TaskNode")
    print(f"  - 任务节点: {[node['id'] for node in task_nodes]}")

    control_nodes = proxy.filter_nodes("SequenceControlNode")
    print(f"  - 序列控制节点: {[node['id'] for node in control_nodes]}")

    # 2. 边操作
    print("\n2. 边查询:")
    all_edges = proxy.list_edges()
    print(f"  - 总边数: {len(all_edges)}")

    branch_edges = proxy.get_node_edges("branch")
    print(f"  - 分支节点入边: {len(branch_edges['incoming'])}")
    print(f"  - 分支节点出边: {len(branch_edges['outgoing'])}")

    # 3. 更新操作
    print("\n3. 节点更新:")
    proxy.update_node(
        "output",
        description="更新的输出节点描述",
        metadata={"updated": True, "version": "2.0"},
    )
    updated_node = proxy.get_node("output")
    print(f"  ✅ 更新输出节点描述: {updated_node['description']}")
    print(f"  ✅ 添加元数据: {updated_node.get('metadata', {})}")

    # 4. 边更新
    print("\n4. 边更新:")
    proxy.update_edge(
        "input", "branch", "default", new_weight=2.0, new_metadata={"priority": "high"}
    )
    updated_edge = proxy.get_edge("input", "branch", "default")
    print(f"  ✅ 更新边权重: {updated_edge['weight']}")
    print(f"  ✅ 添加边元数据: {updated_edge.get('metadata', {})}")

    # 5. 元数据操作
    print("\n5. 图元数据:")
    proxy.set_metadata("created_by", "演示程序")
    proxy.set_metadata("complexity", "中等")
    proxy.set_metadata("estimated_runtime", "5秒")

    print(f"  - 创建者: {proxy.get_metadata('created_by')}")
    print(f"  - 复杂度: {proxy.get_metadata('complexity')}")
    print(f"  - 预估运行时间: {proxy.get_metadata('estimated_runtime')}")

    return proxy


def demo_serialization_and_merge(proxy):
    """演示序列化和合并"""
    print("\n=== 序列化和合并演示 ===\n")

    # 1. 序列化
    print("1. 序列化:")
    config_dict = proxy.to_dict()
    print(f"  ✅ 导出为字典，包含 {len(config_dict)} 个字段")

    yaml_str = proxy.to_yaml()
    print(f"  ✅ 导出为YAML，长度: {len(yaml_str)} 字符")

    # 2. 克隆
    print("\n2. 克隆图:")
    cloned = proxy.clone()
    print(f"  ✅ 克隆成功: {cloned}")

    # 验证独立性
    cloned.name = "克隆的图"
    print(f"  - 原图名称: {proxy.name}")
    print(f"  - 克隆图名称: {cloned.name}")
    print("  ✅ 克隆独立性验证通过")

    # 3. 创建另一个图用于合并
    print("\n3. 创建另一个图:")
    other_proxy = GraphConfigProxy.create_empty("附加功能", "用于合并的额外功能")

    other_proxy.add_node(
        "logger", "TaskNode", "日志记录", "记录处理日志", {"log_level": "INFO"}
    )

    other_proxy.add_node(
        "validator",
        "TaskNode",
        "数据验证",
        "验证输出数据",
        {"validation_rules": ["not_null", "positive"]},
    )

    other_proxy.add_edge("logger", "validator")
    print(f"  ✅ 创建附加图: {other_proxy}")

    # 4. 合并图
    print("\n4. 合并图:")
    merged = proxy.merge(other_proxy, "keep")
    merged_stats = merged.get_statistics()

    print("  ✅ 合并成功:")
    print(f"    - 原图节点: {proxy.get_statistics()['node_count']}")
    print(f"    - 附加图节点: {other_proxy.get_statistics()['node_count']}")
    print(f"    - 合并后节点: {merged_stats['node_count']}")
    print(f"    - 合并后边数: {merged_stats['edge_count']}")

    return merged


def demo_error_handling():
    """演示错误处理"""
    print("\n=== 错误处理演示 ===\n")

    proxy = GraphConfigProxy.create_empty("错误测试")

    # 1. 节点操作错误
    print("1. 节点操作错误:")

    try:
        proxy.add_node("", "TaskNode", "空ID节点")
    except Exception as e:
        print(f"  ❌ 空节点ID: {e}")

    try:
        proxy.add_node("test", "TaskNode", "测试节点")
        proxy.add_node("test", "TaskNode", "重复节点")  # 重复ID
    except Exception as e:
        print(f"  ❌ 重复节点ID: {e}")

    # 2. 边操作错误
    print("\n2. 边操作错误:")

    try:
        proxy.add_edge("nonexistent1", "nonexistent2")
    except Exception as e:
        print(f"  ❌ 不存在的节点: {e}")

    # 3. 起始节点错误
    print("\n3. 起始节点错误:")

    try:
        proxy.start_node = "nonexistent"
    except Exception as e:
        print(f"  ❌ 不存在的起始节点: {e}")

    # 4. 结束节点错误
    print("\n4. 结束节点错误:")

    try:
        proxy.add_end_node("nonexistent")
    except Exception as e:
        print(f"  ❌ 不存在的结束节点: {e}")

    # 5. 参数验证错误
    print("\n5. 参数验证错误:")

    try:
        proxy.add_node(
            "branch_bad",
            "BranchControlNode",
            "错误的分支节点",
            # 缺少condition_func
        )
    except Exception as e:
        print(f"  ❌ 分支节点参数错误: {e}")

    try:
        proxy.add_node(
            "retry_bad",
            "RetryNode",
            "错误的重试节点",
            params={"max_retries": -1},  # 无效参数
        )
    except Exception as e:
        print(f"  ❌ 重试节点参数错误: {e}")


def demo_file_validation():
    """演示文件验证"""
    print("\n=== 文件验证演示 ===\n")

    # 查找示例配置文件
    config_dir = Path(__file__).parent.parent / "examples" / "graph_configs"

    if config_dir.exists():
        yaml_files = list(config_dir.glob("*.yaml"))

        if yaml_files:
            print(f"找到 {len(yaml_files)} 个示例配置文件:")

            for yaml_file in yaml_files[:3]:  # 只演示前3个
                print(f"\n验证文件: {yaml_file.name}")
                valid, errors = validate_graph_config_file(str(yaml_file))

                if valid:
                    print("  ✅ 文件有效")
                else:
                    print(f"  ❌ 文件无效，错误数: {len(errors)}")
                    for error in errors[:3]:  # 只显示前3个错误
                        print(f"    - {error}")
                    if len(errors) > 3:
                        print(f"    ... 还有 {len(errors) - 3} 个错误")
        else:
            print("未找到YAML配置文件")
    else:
        print("配置目录不存在")


async def main():
    """主演示函数"""
    print("AgenticZero 图配置Schema验证和代理操作演示")
    print("=" * 60)

    try:
        # 1. Schema验证演示
        demo_schema_validation()

        # 2. 配置代理基础演示
        proxy = demo_config_proxy()

        # 3. 高级操作演示
        proxy = demo_advanced_operations(proxy)

        # 4. 序列化和合并演示
        merged_proxy = demo_serialization_and_merge(proxy)

        # 5. 错误处理演示
        demo_error_handling()

        # 6. 文件验证演示
        demo_file_validation()

        print("\n" + "=" * 60)
        print("✅ 所有演示完成！")
        print("\n主要功能:")
        print("  • Schema验证器：提供完整的YAML配置验证和语义化错误信息")
        print("  • 配置代理：提供图结构操作的高级API")
        print("  • 实时验证：所有操作都会实时验证配置有效性")
        print("  • 序列化支持：支持YAML和字典格式的导入导出")
        print("  • 错误处理：提供详细的错误信息和异常处理")

        # 7. 保存最终配置示例
        if merged_proxy.is_valid():
            output_file = Path(__file__).parent / "generated_demo_config.yaml"
            merged_proxy.save_to_file(str(output_file))
            print(f"\n💾 演示配置已保存到: {output_file}")

    except Exception as e:
        print(f"\n❌ 演示过程中发生错误: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
