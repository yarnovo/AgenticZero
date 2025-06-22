"""
基础工作流示例

演示如何使用新架构创建一个简单的工作流
"""

import asyncio
from src.graph import (
    EnhancedGraph,
    SequenceControlNode,
    BranchControlNode,
    TaskNode,
    ResumableExecutor
)


# 自定义任务节点
class DataProcessorTask(TaskNode):
    """数据处理任务节点"""
    
    async def _execute_task(self, input_data):
        """处理数据"""
        print(f"处理数据: {input_data}")
        # 模拟数据处理
        return {"processed": input_data * 2}


class DataValidatorTask(TaskNode):
    """数据验证任务节点"""
    
    async def _execute_task(self, input_data):
        """验证数据"""
        print(f"验证数据: {input_data}")
        # 检查是否有processed字段
        if isinstance(input_data, dict) and "processed" in input_data:
            return {"valid": True, "data": input_data["processed"]}
        return {"valid": False, "data": input_data}


async def main():
    """主函数"""
    # 创建增强图
    graph = EnhancedGraph("basic_workflow")
    
    # 创建节点
    start = SequenceControlNode("start", "开始", lambda x: {"input": x})
    processor = DataProcessorTask("processor", "数据处理器")
    validator = DataValidatorTask("validator", "数据验证器")
    
    # 分支节点：根据验证结果选择路径
    router = BranchControlNode(
        "router", 
        "路由器",
        lambda x: "success" if x.get("valid", False) else "error"
    )
    
    # 成功和错误处理节点
    success_handler = SequenceControlNode(
        "success", 
        "成功处理",
        lambda x: {"result": "成功", "data": x.get("data")}
    )
    
    error_handler = SequenceControlNode(
        "error",
        "错误处理", 
        lambda x: {"result": "失败", "reason": "验证未通过"}
    )
    
    # 添加节点到图
    graph.add_node(start)
    graph.add_node(processor)
    graph.add_node(validator)
    graph.add_node(router)
    graph.add_node(success_handler)
    graph.add_node(error_handler)
    
    # 连接节点
    graph.add_edge("start", "processor")
    graph.add_edge("processor", "validator")
    graph.add_edge("validator", "router")
    graph.add_edge("router", "success", "success")
    graph.add_edge("router", "error", "error")
    
    # 设置起始和结束节点
    graph.set_start("start")
    graph.add_end("success")
    graph.add_end("error")
    
    # 验证图结构
    graph.validate()
    
    # 创建可恢复的执行器
    executor = ResumableExecutor(graph)
    
    # 注册钩子
    def on_node_complete(node):
        print(f"节点完成: {node.node_id} - 结果: {node.result}")
    
    executor.register_hook("node_complete", on_node_complete)
    
    # 执行工作流
    print("=== 执行工作流 ===")
    context = await executor.execute_with_checkpoints(initial_input=10)
    
    print(f"\n执行完成，总耗时: {context.duration:.2f}秒")
    print(f"最终输出: {context.graph_output}")
    
    # 序列化图
    print("\n=== 序列化图 ===")
    serialized = graph.serialize()
    print(f"序列化成功，包含 {len(serialized['nodes'])} 个节点")
    
    # 保存快照
    if executor.snapshots:
        snapshot = executor.snapshots[-1]
        graph.save_snapshot(snapshot, "workflow_snapshot.json")
        print("快照已保存到 workflow_snapshot.json")


if __name__ == "__main__":
    asyncio.run(main())