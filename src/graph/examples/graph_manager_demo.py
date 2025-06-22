"""
Graph 管理系统使用示例

演示如何使用 GraphManager 来管理图的完整生命周期。
"""

import asyncio
from pathlib import Path

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from src.graph import GraphManager, TaskNode


async def main():
    """主函数"""
    # 创建管理器（使用临时目录作为示例）
    manager = GraphManager("./demo_graphs")
    
    print("=== Graph 管理系统演示 ===\n")
    
    # 1. 创建新图
    print("1. 创建新的工作流图...")
    workflow = manager.create(
        name="data_pipeline",
        description="数据处理管道示例"
    )
    print(f"   ✓ 创建成功: {workflow.name}")
    print(f"   - 文件保存在: demo_graphs/data_pipeline.yaml")
    print(f"   - 已自动加载到内存")
    
    # 2. 动态修改图结构
    print("\n2. 动态添加节点和边...")
    
    # 添加数据处理节点
    workflow.add_node("load_data", "TaskNode", "加载数据")
    workflow.add_node("clean_data", "TaskNode", "清洗数据")
    workflow.add_node("analyze_data", "TaskNode", "分析数据")
    workflow.add_node("save_results", "TaskNode", "保存结果")
    
    # 移除默认的 start->end 边
    workflow.remove_edge("start", "end")
    
    # 创建新的执行路径
    workflow.add_edge("start", "load_data")
    workflow.add_edge("load_data", "clean_data")
    workflow.add_edge("clean_data", "analyze_data")
    workflow.add_edge("analyze_data", "save_results")
    workflow.add_edge("save_results", "end")
    
    print("   ✓ 添加了4个数据处理节点")
    print("   ✓ 创建了完整的处理流程")
    
    # 验证图结构
    valid, errors = workflow.validate()
    print(f"   ✓ 图结构验证: {'通过' if valid else '失败'}")
    if not valid:
        for error in errors:
            print(f"     - {error}")
    
    # 3. 保存修改
    print("\n3. 保存修改到文件...")
    manager.save("data_pipeline")
    print("   ✓ 已保存到 demo_graphs/data_pipeline.yaml")
    
    # 4. 创建另一个图
    print("\n4. 创建分支处理图...")
    branch_flow = manager.create("branch_pipeline", "带条件分支的管道")
    
    # 添加分支节点
    branch_flow.add_node("check", "BranchControlNode", "条件检查", 
                        condition_func=lambda x: "high" if x > 100 else "low")
    branch_flow.add_node("high_process", "TaskNode", "高值处理")
    branch_flow.add_node("low_process", "TaskNode", "低值处理")
    
    # 调整边
    branch_flow.remove_edge("start", "end")
    branch_flow.add_edge("start", "check")
    branch_flow.add_edge("check", "high_process", action="high")
    branch_flow.add_edge("check", "low_process", action="low")
    branch_flow.add_edge("high_process", "end")
    branch_flow.add_edge("low_process", "end")
    
    print("   ✓ 创建了条件分支结构")
    
    # 5. 列出所有图
    print("\n5. 查看所有图的状态...")
    all_graphs = manager.list_all()
    for name, info in all_graphs.items():
        status = "已加载" if info["in_memory"] else "未加载"
        print(f"   - {name}: {status}")
    
    # 6. 卸载和重新加载
    print("\n6. 内存管理演示...")
    print("   - 卸载 data_pipeline...")
    manager.unload("data_pipeline")
    print("   ✓ 已从内存卸载")
    
    print("   - 重新加载 data_pipeline...")
    reloaded = manager.load("data_pipeline")
    print("   ✓ 重新加载成功")
    print(f"   - 节点数: {len(reloaded.list_nodes())}")
    print(f"   - 边数: {len(reloaded.list_edges())}")
    
    # 7. 获取代理进行实时修改
    print("\n7. 获取代理进行实时修改...")
    proxy = manager.get_proxy("branch_pipeline")
    if proxy:
        # 添加日志节点
        proxy.add_node("logger", "TaskNode", "日志记录")
        proxy.add_edge("check", "logger")
        proxy.add_edge("logger", "high_process", action="high")
        proxy.add_edge("logger", "low_process", action="low")
        
        # 移除原来的直接连接
        proxy.remove_edge("check", "high_process", "high")
        proxy.remove_edge("check", "low_process", "low")
        
        print("   ✓ 添加了日志节点到分支流程")
    
    # 8. 查看图的统计信息
    print("\n8. 查看图的统计信息...")
    for name in ["data_pipeline", "branch_pipeline"]:
        proxy = manager.get_proxy(name)
        if proxy:
            stats = proxy.get_statistics()
            print(f"\n   {name}:")
            print(f"   - 节点数: {stats['node_count']}")
            print(f"   - 边数: {stats['edge_count']}")
            print(f"   - 有环: {'是' if stats['has_cycles'] else '否'}")
            print(f"   - 节点类型分布: {stats['node_types']}")
    
    # 9. 运行图（模拟）
    print("\n9. 准备运行图...")
    # 为节点设置执行函数
    data_proxy = manager.get_proxy("data_pipeline")
    if data_proxy:
        # 这里只是演示，实际使用时需要设置真实的执行逻辑
        nodes = data_proxy.list_nodes()
        for node_id, node in nodes:
            if isinstance(node, TaskNode):
                # 设置简单的执行函数
                if node_id == "load_data":
                    node.execute_func = lambda: {"data": [1, 2, 3, 4, 5]}
                elif node_id == "clean_data":
                    node.execute_func = lambda x: {"data": [i * 2 for i in x.get("data", [])]}
                elif node_id == "analyze_data":
                    node.execute_func = lambda x: {"mean": sum(x.get("data", [])) / len(x.get("data", [])), "data": x.get("data", [])}
                elif node_id == "save_results":
                    node.execute_func = lambda x: f"分析完成，平均值: {x.get('mean', 0)}"
                else:
                    node.execute_func = lambda x=None: x
        
        print("   ✓ 已为数据管道设置执行函数")
        
        # 运行图
        try:
            print("   - 执行数据处理管道...")
            result = await manager.run("data_pipeline")
            print(f"   ✓ 执行成功: {result}")
        except Exception as e:
            print(f"   ✗ 执行失败: {e}")
    
    # 10. 清理演示
    print("\n10. 清理演示数据...")
    manager.delete("data_pipeline", force=True)
    manager.delete("branch_pipeline", force=True)
    print("   ✓ 已删除所有演示图")
    
    print("\n=== 演示完成 ===")


if __name__ == "__main__":
    asyncio.run(main())