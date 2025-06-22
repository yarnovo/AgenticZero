"""
测试AI节点

测试AI任务节点和AI控制节点
"""

import pytest
import json
from typing import List, Dict, Any, Optional
from src.graph import (
    AITaskNode,
    AIControlNode,
    AIAnalyzer,
    AIGenerator,
    AIEvaluator,
    AIRouter,
    AIPlanner,
    IAgent,
    AgentMessage,
    AgentResponse,
    AgentProxy
)


# 模拟Agent实现
class MockAgent(IAgent):
    """用于测试的模拟Agent"""
    
    def __init__(self, name: str = "MockAgent"):
        self.name = name
        self._model_info = {"name": name, "type": "mock"}
        self.call_history = []
        
    @property
    def capabilities(self) -> List[str]:
        """获取能力列表"""
        return ["think", "plan", "decide", "evaluate"]
        
    @property
    def model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        return self._model_info
        
    async def think(self, messages: List[AgentMessage], context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """模拟思考"""
        self.call_history.append(("think", messages, context))
        
        # 根据消息内容返回不同响应
        last_msg = messages[-1].content if messages else ""
        
        if "分析" in last_msg:
            content = json.dumps({
                "主要发现": ["发现1", "发现2"],
                "关键洞察": ["洞察1"],
                "建议行动": ["行动1"]
            }, ensure_ascii=False)
        else:
            content = f"思考结果: {last_msg}"
            
        return AgentResponse(
            content=content,
            confidence=0.9,
            reasoning="模拟推理过程"
        )
        
    async def plan(self, goal: str, constraints: Optional[List[str]] = None, context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """模拟规划"""
        self.call_history.append(("plan", goal, constraints, context))
        return [
            {"step": 1, "action": "步骤1", "description": "执行步骤1"},
            {"step": 2, "action": "步骤2", "description": "执行步骤2"}
        ]
        
    async def decide(self, options: List[str], criteria: Optional[Dict[str, float]] = None, context: Optional[Dict[str, Any]] = None) -> str:
        """模拟决策"""
        self.call_history.append(("decide", options, criteria, context))
        return options[0] if options else "default"
        
    async def evaluate(self, subject: Any, criteria: Optional[List[str]] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """模拟评估"""
        self.call_history.append(("evaluate", subject, criteria, context))
        scores = {c: 0.8 for c in (criteria or ["default"])}
        return {
            "scores": scores,
            "average": 0.8,
            "feedback": "良好"
        }


@pytest.mark.unit
class TestAITaskNode:
    """测试AI任务节点基类"""
    
    def test_ai_task_node_creation(self):
        """测试AI任务节点创建"""
        # 创建一个具体的AI任务节点实现来测试基类功能
        class TestAITask(AITaskNode):
            async def _process_with_ai(self, input_data, context):
                return {"processed": input_data}
                
        agent = MockAgent()
        node = TestAITask("ai_task1", "AI任务", agent=agent)
        
        assert node.node_id == "ai_task1"
        assert node.agent is agent
        assert node.conversation_history == []
        
    def test_ai_task_node_default_agent(self):
        """测试默认Agent"""
        # AITaskNode是抽象类，需要使用具体实现
        from src.graph import AIAnalyzer
        node = AIAnalyzer("ai_task2", "默认Agent任务")
        assert isinstance(node.agent, AgentProxy)
        
    @pytest.mark.asyncio
    async def test_consult_agent(self):
        """测试咨询Agent"""
        agent = MockAgent()
        # 使用具体的AI任务节点
        from src.graph import AIAnalyzer
        node = AIAnalyzer("ai_task3", "咨询测试", agent=agent)
        
        response = await node._consult_agent("测试提示", {"key": "value"})
        
        assert response == "思考结果: 测试提示"
        assert len(node.conversation_history) == 2  # 用户消息 + 助手消息
        assert node.conversation_history[0].role == "user"
        assert node.conversation_history[1].role == "assistant"


@pytest.mark.unit
class TestAIAnalyzer:
    """测试AI分析节点"""
    
    def test_analyzer_creation(self):
        """测试分析节点创建"""
        agent = MockAgent()
        node = AIAnalyzer(
            "analyzer1",
            "数据分析",
            analysis_type="trend",
            agent=agent
        )
        
        assert node.analysis_type == "trend"
        assert node.agent is agent
        
    @pytest.mark.asyncio
    async def test_analyzer_execution(self):
        """测试分析节点执行"""
        agent = MockAgent()
        node = AIAnalyzer(
            "analyzer2",
            "执行分析",
            analysis_type="pattern",
            agent=agent
        )
        node._input_data = {"data": [1, 2, 3, 4, 5]}
        
        result = await node.exec()
        
        assert result["analysis_type"] == "pattern"
        assert result["input"] == {"data": [1, 2, 3, 4, 5]}
        assert "findings" in result
        
        # 检查Agent被调用
        assert len(agent.call_history) == 1
        assert agent.call_history[0][0] == "think"


@pytest.mark.unit
class TestAIGenerator:
    """测试AI生成节点"""
    
    def test_generator_creation(self):
        """测试生成节点创建"""
        node = AIGenerator(
            "gen1",
            "代码生成",
            generation_type="code"
        )
        
        assert node.generation_type == "code"
        
    @pytest.mark.asyncio
    async def test_generator_code(self):
        """测试代码生成"""
        agent = MockAgent()
        node = AIGenerator(
            "gen2",
            "生成代码",
            generation_type="code",
            agent=agent
        )
        node._input_data = "创建一个函数计算两数之和"
        
        result = await node.exec()
        
        assert result["generation_type"] == "code"
        assert result["input"] == "创建一个函数计算两数之和"
        assert "generated" in result
        assert "metadata" in result
        
    @pytest.mark.asyncio
    async def test_generator_plan(self):
        """测试计划生成"""
        agent = MockAgent()
        node = AIGenerator(
            "gen3",
            "生成计划",
            generation_type="plan",
            agent=agent
        )
        node._input_data = "开发新功能"
        
        result = await node.exec()
        
        assert result["generation_type"] == "plan"
        assert "generated" in result


@pytest.mark.unit
class TestAIEvaluator:
    """测试AI评估节点"""
    
    def test_evaluator_creation(self):
        """测试评估节点创建"""
        criteria = ["质量", "性能", "可维护性"]
        node = AIEvaluator(
            "eval1",
            "代码评估",
            criteria=criteria
        )
        
        assert node.criteria == criteria
        
    @pytest.mark.asyncio
    async def test_evaluator_execution(self):
        """测试评估执行"""
        agent = MockAgent()
        node = AIEvaluator(
            "eval2",
            "执行评估",
            criteria=["完整性", "准确性"],
            agent=agent
        )
        node._input_data = {"code": "def add(a, b): return a + b"}
        
        result = await node.exec()
        
        assert result["subject"] == {"code": "def add(a, b): return a + b"}
        assert result["criteria"] == ["完整性", "准确性"]
        assert "evaluation" in result
        assert result["overall_score"] == 0.8
        assert "recommendation" in result
        
        # 检查Agent evaluate方法被调用
        assert any(call[0] == "evaluate" for call in agent.call_history)


@pytest.mark.unit
class TestAIControlNodes:
    """测试AI控制节点"""
    
    def test_ai_control_node_creation(self):
        """测试AI控制节点创建"""
        agent = MockAgent()
        node = AIControlNode("ai_ctrl1", "AI控制", agent=agent)
        
        assert node.agent is agent
        assert node.sub_graph is not None
        assert node.sub_graph.name == "ai_ctrl1_ai_subgraph"
        
    @pytest.mark.asyncio
    async def test_ai_router(self):
        """测试AI路由器"""
        agent = MockAgent()
        routes = ["route_a", "route_b", "route_c"]
        node = AIRouter(
            "router1",
            "智能路由",
            routes=routes,
            agent=agent
        )
        node._input_data = {"metric": 100}
        
        result = await node.exec()
        
        assert "selected_route" in result
        assert result["selected_route"] in routes
        assert result["input"] == {"metric": 100}
        
        # 检查决策方法被调用
        assert any(call[0] == "decide" for call in agent.call_history)
        
    @pytest.mark.asyncio
    async def test_ai_router_post(self):
        """测试AI路由器后处理"""
        node = AIRouter("router2", "路由后处理", routes=["a", "b"])
        node.result = {"selected_route": "custom_route"}
        
        next_node = await node.post()
        assert next_node == "custom_route"
        
    @pytest.mark.asyncio
    async def test_ai_planner(self):
        """测试AI规划器"""
        agent = MockAgent()
        node = AIPlanner(
            "planner1",
            "智能规划",
            agent=agent
        )
        node._input_data = {"goal": "完成项目"}
        
        await node.exec()
        
        # 检查规划方法被调用
        assert any(call[0] == "plan" for call in agent.call_history)
        
        # 检查子图被构建
        assert len(node.sub_graph.nodes) > 0
        
    @pytest.mark.asyncio
    async def test_ai_planner_sub_graph_execution(self):
        """测试AI规划器子图执行"""
        agent = MockAgent()
        node = AIPlanner(
            "planner2",
            "子图执行",
            agent=agent
        )
        node._input_data = {"task": "测试任务"}
        
        result = await node.exec()
        
        # 应该返回子图执行结果
        assert "graph_output" in result or "plan_executed" in result


@pytest.mark.unit
class TestAgentProxy:
    """测试Agent代理"""
    
    def test_agent_proxy_creation(self):
        """测试代理创建"""
        proxy = AgentProxy("TestProxy")
        assert proxy.name == "TestProxy"
        assert proxy.model_info["name"] == "TestProxy"
        
    @pytest.mark.asyncio
    async def test_agent_proxy_think(self):
        """测试代理思考"""
        proxy = AgentProxy("ThinkProxy")
        messages = [AgentMessage(role="user", content="测试")]
        
        response = await proxy.think(messages)
        
        assert isinstance(response, AgentResponse)
        assert response.confidence > 0
        assert response.content != ""
        
    @pytest.mark.asyncio
    async def test_agent_proxy_plan(self):
        """测试代理规划"""
        proxy = AgentProxy("PlanProxy")
        
        plan = await proxy.plan("测试目标", ["约束1"])
        
        assert isinstance(plan, list)
        assert len(plan) > 0
        assert all("action" in step for step in plan)
        
    @pytest.mark.asyncio
    async def test_agent_proxy_decide(self):
        """测试代理决策"""
        proxy = AgentProxy("DecideProxy")
        
        decision = await proxy.decide(["选项A", "选项B", "选项C"])
        
        assert decision in ["选项A", "选项B", "选项C"]
        
    @pytest.mark.asyncio
    async def test_agent_proxy_evaluate(self):
        """测试代理评估"""
        proxy = AgentProxy("EvalProxy")
        
        evaluation = await proxy.evaluate(
            "测试对象",
            ["标准1", "标准2"]
        )
        
        assert "scores" in evaluation
        assert "average" in evaluation
        assert len(evaluation["scores"]) == 2