"""
AI工作流示例

演示如何使用AI节点创建智能工作流
"""

import asyncio
import json
from typing import List, Dict, Any, Optional
from src.graph import (
    EnhancedGraph,
    AIRouter,
    AIAnalyzer,
    AIGenerator,
    AIEvaluator,
    IAgent,
    AgentMessage,
    AgentResponse,
    SequenceControlNode,
    ResumableExecutor
)


# 模拟的AI Agent实现
class MockLLMAgent(IAgent):
    """模拟的大语言模型Agent"""
    
    def __init__(self, name: str):
        self.name = name
        self.model_info = {"name": name, "type": "mock_llm"}
        
    async def think(self, messages: List[AgentMessage], context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """模拟思考过程"""
        # 获取最后一条消息
        last_message = messages[-1].content if messages else ""
        
        # 模拟回复
        if "分析" in last_message:
            response_content = json.dumps({
                "主要发现": ["数据量增长20%", "用户活跃度提升"],
                "关键洞察": ["季节性因素明显", "需要增加服务器容量"],
                "建议行动": ["优化缓存策略", "准备扩容方案"]
            }, ensure_ascii=False)
        elif "生成" in last_message:
            response_content = "基于分析结果，建议采取以下措施：\n1. 立即优化缓存\n2. 制定扩容计划\n3. 监控系统负载"
        else:
            response_content = f"已收到请求：{last_message[:50]}..."
            
        return AgentResponse(
            content=response_content,
            confidence=0.85,
            reasoning="基于历史数据和模式分析"
        )
        
    async def plan(self, goal: str, constraints: Optional[List[str]] = None, context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """制定计划"""
        return [
            {"step": 1, "action": "收集数据", "duration": "1天"},
            {"step": 2, "action": "分析趋势", "duration": "2小时"},
            {"step": 3, "action": "生成报告", "duration": "1小时"}
        ]
        
    async def decide(self, options: List[str], criteria: Optional[Dict[str, float]] = None, context: Optional[Dict[str, Any]] = None) -> str:
        """做出决策"""
        # 简单的决策逻辑
        if "high_performance" in options:
            return "high_performance"
        elif "balanced" in options:
            return "balanced"
        return options[0] if options else "default"
        
    async def evaluate(self, subject: Any, criteria: Optional[List[str]] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """评估结果"""
        scores = {}
        for criterion in (criteria or ["质量"]):
            # 模拟评分
            scores[criterion] = 0.75 + (len(str(subject)) % 10) * 0.025
            
        return {
            "scores": scores,
            "average": sum(scores.values()) / len(scores),
            "recommendation": "优秀" if sum(scores.values()) / len(scores) > 0.8 else "良好"
        }


async def main():
    """主函数"""
    # 创建增强图
    graph = EnhancedGraph("ai_workflow")
    
    # 创建共享的Agent
    agent = MockLLMAgent("SmartAssistant")
    
    # 创建节点
    start = SequenceControlNode("start", "开始", lambda x: {"raw_data": x})
    
    # AI分析节点
    analyzer = AIAnalyzer(
        "analyzer",
        "数据分析",
        analysis_type="trend_analysis",
        agent=agent
    )
    
    # AI路由节点：根据分析结果选择处理策略
    router = AIRouter(
        "router",
        "智能路由",
        routes=["optimize", "expand", "monitor"],
        agent=agent
    )
    
    # 不同策略的处理节点
    optimize = AIGenerator(
        "optimize",
        "优化方案生成",
        generation_type="plan",
        agent=agent
    )
    
    expand = AIGenerator(
        "expand",
        "扩容方案生成",
        generation_type="plan",
        agent=agent
    )
    
    monitor = SequenceControlNode(
        "monitor",
        "监控设置",
        lambda x: {"action": "设置监控告警", "data": x}
    )
    
    # AI评估节点
    evaluator = AIEvaluator(
        "evaluator",
        "方案评估",
        criteria=["可行性", "成本效益", "风险程度"],
        agent=agent
    )
    
    # 结束节点
    end = SequenceControlNode(
        "end",
        "完成",
        lambda x: {"final_result": x, "status": "completed"}
    )
    
    # 构建图
    graph.add_node(start)
    graph.add_node(analyzer)
    graph.add_node(router)
    graph.add_node(optimize)
    graph.add_node(expand)
    graph.add_node(monitor)
    graph.add_node(evaluator)
    graph.add_node(end)
    
    # 连接节点
    graph.add_edge("start", "analyzer")
    graph.add_edge("analyzer", "router")
    graph.add_edge("router", "optimize", "optimize")
    graph.add_edge("router", "expand", "expand")
    graph.add_edge("router", "monitor", "monitor")
    graph.add_edge("optimize", "evaluator")
    graph.add_edge("expand", "evaluator")
    graph.add_edge("monitor", "end")
    graph.add_edge("evaluator", "end")
    
    # 设置起始和结束节点
    graph.set_start("start")
    graph.add_end("end")
    
    # 验证图
    graph.validate()
    
    # 创建执行器
    executor = ResumableExecutor(graph)
    
    # 设置钩子
    async def on_ai_decision(node):
        if hasattr(node, 'agent'):
            print(f"🤖 AI节点 {node.node_id} 做出决策")
            
    executor.register_hook("node_complete", on_ai_decision)
    
    # 测试数据
    test_data = {
        "metrics": {
            "cpu_usage": 85,
            "memory_usage": 70,
            "request_count": 10000,
            "response_time": 250
        },
        "timestamp": "2024-01-01T10:00:00"
    }
    
    print("=== 执行AI工作流 ===")
    context = await executor.execute_with_checkpoints(initial_input=test_data)
    
    print(f"\n执行完成，总耗时: {context.duration:.2f}秒")
    print(f"访问的节点: {list(context.visited_nodes)}")
    
    # 显示AI节点的对话历史
    print("\n=== AI对话历史 ===")
    for node_id, node in graph.nodes.items():
        if hasattr(node, 'conversation_history') and node.conversation_history:
            print(f"\n{node_id} 的对话:")
            for msg in node.conversation_history:
                role = msg.role
                content = msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
                print(f"  {role}: {content}")
    
    # 创建检查点并演示恢复
    print("\n=== 测试中断和恢复 ===")
    # 创建一个会中断的执行
    graph2 = EnhancedGraph("interruptible_workflow")
    
    # 添加一个会"失败"的节点
    class InterruptibleTask(TaskNode):
        def __init__(self, node_id: str, name: str, fail_on_run: int = 1):
            super().__init__(node_id, name)
            self.run_count = 0
            self.fail_on_run = fail_on_run
            
        async def _execute_task(self, input_data):
            self.run_count += 1
            if self.run_count == self.fail_on_run:
                raise Exception("模拟的中断")
            return {"processed": input_data, "run": self.run_count}
    
    # 构建简单的可中断流程
    task1 = SequenceControlNode("task1", "任务1", lambda x: {"step1": x})
    task2 = InterruptibleTask("task2", "可中断任务", fail_on_run=1)
    task3 = SequenceControlNode("task3", "任务3", lambda x: {"step3": x})
    
    graph2.add_node(task1)
    graph2.add_node(task2)
    graph2.add_node(task3)
    
    graph2.add_edge("task1", "task2")
    graph2.add_edge("task2", "task3")
    
    graph2.set_start("task1")
    graph2.add_end("task3")
    
    executor2 = ResumableExecutor(graph2)
    
    # 第一次执行（会失败）
    print("\n第一次执行（会中断）...")
    try:
        await executor2.execute_with_checkpoints(initial_input="test_data")
    except Exception as e:
        print(f"执行中断: {e}")
        
    # 从快照恢复
    if executor2.snapshots:
        print("\n从快照恢复执行...")
        last_snapshot = executor2.snapshots[-1]
        
        # 修复"问题"
        task2.fail_on_run = 2
        
        # 恢复执行
        context = await executor2.resume_from_snapshot(last_snapshot)
        print(f"恢复执行成功！最终结果: {context.graph_output}")


if __name__ == "__main__":
    asyncio.run(main())