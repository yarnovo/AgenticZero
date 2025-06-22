"""
测试简单的图执行
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.graph import Graph, SimpleNode, LoggingNode, GraphExecutor


async def test_basic():
    """测试基础功能"""
    # 创建节点
    start = SimpleNode("start", "开始")
    middle = LoggingNode("middle", "中间", log_message="处理中")
    end = SimpleNode("end", "结束")
    
    # 创建图
    graph = Graph("测试图")
    graph.add_node("start", start)
    graph.add_node("middle", middle)
    graph.add_node("end", end)
    
    # 添加边
    graph.add_edge("start", "middle")
    graph.add_edge("middle", "end")
    
    # 设置起始和结束节点
    graph.set_start("start")
    graph.add_end("end")
    
    # 执行
    executor = GraphExecutor(graph)
    result = await executor.execute()
    
    print(f"执行完成！历史记录: {len(result.execution_history)} 个节点")
    for entry in result.execution_history:
        print(f"  - {entry['node_id']}: action={entry.get('action', 'N/A')}, result={entry.get('result', 'N/A')}")


if __name__ == "__main__":
    asyncio.run(test_basic())