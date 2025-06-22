"""
AI控制节点

具有智能决策能力的控制节点
"""

from abc import abstractmethod
from typing import Any, Optional, List, Dict

from .node_types import ControlNode
from .core import Graph
from .executor import GraphExecutor
from .agent_interface import IAgent, AgentMessage, AgentProxy


class AIControlNode(ControlNode):
    """AI控制节点基类
    
    通过Agent赋予控制节点智能决策能力
    """
    
    def __init__(
        self, 
        node_id: str, 
        name: Optional[str] = None,
        agent: Optional[IAgent] = None,
        **kwargs
    ):
        """初始化AI控制节点
        
        Args:
            node_id: 节点ID
            name: 节点名称
            agent: AI Agent实例
        """
        super().__init__(node_id, name, **kwargs)
        self.agent = agent or AgentProxy(f"Agent_{node_id}")
        self.sub_graph = Graph(f"{node_id}_ai_subgraph")
        self.sub_executor: Optional[GraphExecutor] = None
        self.conversation_history: List[AgentMessage] = []
        self._setup_sub_graph()
        
    @abstractmethod
    def _setup_sub_graph(self):
        """设置AI控制的子图结构"""
        pass
        
    async def _consult_agent(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """咨询Agent获取决策
        
        Args:
            prompt: 提示词
            context: 上下文信息
            
        Returns:
            Agent的响应内容
        """
        # 构建消息
        message = AgentMessage(role="user", content=prompt)
        self.conversation_history.append(message)
        
        # 调用Agent
        response = await self.agent.think(
            messages=self.conversation_history,
            context=context
        )
        
        # 记录响应
        assistant_msg = AgentMessage(
            role="assistant", 
            content=response.content,
            metadata={"reasoning": response.reasoning, "confidence": response.confidence}
        )
        self.conversation_history.append(assistant_msg)
        
        return response.content
        
    async def exec(self) -> Any:
        """执行AI控制逻辑"""
        # 获取输入
        input_data = self._input_data if hasattr(self, '_input_data') else None
        
        # 构建上下文
        context = {
            "node_id": self.node_id,
            "node_name": self.name,
            "input": input_data,
            "graph_context": getattr(self, 'graph_context', {})
        }
        
        # 让Agent分析当前情况
        analysis = await self._analyze_situation(input_data, context)
        
        # 基于分析结果执行子图或直接返回决策
        if self.sub_graph.nodes:
            # 如果有子图，执行子图
            self.sub_executor = GraphExecutor(self.sub_graph)
            sub_context = await self.sub_executor.execute(
                initial_input={
                    "original_input": input_data,
                    "ai_analysis": analysis
                }
            )
            
            # 获取子图结果
            end_nodes = list(self.sub_graph.end_node_ids)
            if end_nodes:
                return sub_context.node_outputs.get(end_nodes[0])
            return sub_context.node_outputs
        else:
            # 直接返回AI分析结果
            return analysis
            
    @abstractmethod
    async def _analyze_situation(self, input_data: Any, context: Dict[str, Any]) -> Any:
        """分析当前情况 - 子类必须实现
        
        Args:
            input_data: 输入数据
            context: 上下文信息
            
        Returns:
            分析结果
        """
        pass
        
    async def post(self) -> Optional[str]:
        """AI决定下一步动作"""
        # 基于执行结果让AI决定下一步
        if isinstance(self.result, dict) and "next_action" in self.result:
            return self.result["next_action"]
            
        # 让Agent决定
        prompt = f"""
        基于当前执行结果，决定下一步动作：
        执行结果: {self.result}
        
        请返回下一步的动作标识，如果继续正常流程请返回'continue'，
        如果需要特殊处理请返回相应的动作标识。
        """
        
        decision = await self._consult_agent(prompt)
        
        # 解析决策
        if "continue" in decision.lower():
            return None
        elif "error" in decision.lower():
            return "error"
        elif "retry" in decision.lower():
            return "retry"
        else:
            # 尝试从响应中提取动作标识
            return self._extract_action(decision)
            
    def _extract_action(self, response: str) -> Optional[str]:
        """从AI响应中提取动作标识"""
        # 简单实现：查找引号中的内容
        import re
        match = re.search(r"['\"](\w+)['\"]", response)
        if match:
            return match.group(1)
        return None


class AIRouter(AIControlNode):
    """AI路由节点
    
    使用AI进行智能路由决策
    """
    
    def __init__(
        self,
        node_id: str,
        name: Optional[str] = None,
        routes: Optional[List[str]] = None,
        agent: Optional[IAgent] = None,
        **kwargs
    ):
        """初始化AI路由节点
        
        Args:
            node_id: 节点ID
            name: 节点名称
            routes: 可用路由列表
            agent: AI Agent实例
        """
        self.routes = routes or []
        super().__init__(node_id, name, agent, **kwargs)
        
    def _setup_sub_graph(self):
        """AI路由不需要子图"""
        pass
        
    async def _analyze_situation(self, input_data: Any, context: Dict[str, Any]) -> Any:
        """分析输入并选择路由"""
        prompt = f"""
        作为智能路由器，请分析输入并选择最合适的路由：
        
        输入数据: {input_data}
        可用路由: {self.routes}
        
        请基于语义理解选择最匹配的路由，并说明选择理由。
        返回格式: {{"route": "选择的路由", "reason": "选择理由", "confidence": 0.9}}
        """
        
        response = await self._consult_agent(prompt, context)
        
        # 解析响应
        try:
            import json
            result = json.loads(response)
            return {
                "selected_route": result.get("route", self.routes[0] if self.routes else "default"),
                "reason": result.get("reason", ""),
                "confidence": result.get("confidence", 0.5),
                "input": input_data
            }
        except:
            # 如果解析失败，使用默认路由
            return {
                "selected_route": self.routes[0] if self.routes else "default",
                "reason": "Failed to parse AI response",
                "confidence": 0.0,
                "input": input_data
            }
            
    async def post(self) -> Optional[str]:
        """返回选择的路由"""
        if isinstance(self.result, dict) and "selected_route" in self.result:
            return self.result["selected_route"]
        return "default"


class AIPlanner(AIControlNode):
    """AI规划节点
    
    使用AI进行任务规划和分解
    """
    
    def __init__(
        self,
        node_id: str,
        name: Optional[str] = None,
        agent: Optional[IAgent] = None,
        max_steps: int = 10,
        **kwargs
    ):
        """初始化AI规划节点"""
        self.max_steps = max_steps
        super().__init__(node_id, name, agent, **kwargs)
        
    def _setup_sub_graph(self):
        """设置规划执行的子图"""
        # 子图将在规划生成后动态构建
        pass
        
    async def _analyze_situation(self, input_data: Any, context: Dict[str, Any]) -> Any:
        """分析任务并生成规划"""
        # 提取目标
        goal = input_data if isinstance(input_data, str) else str(input_data)
        
        # 让Agent制定计划
        plan_steps = await self.agent.plan(
            goal=goal,
            constraints=[f"最多{self.max_steps}个步骤", "步骤必须可执行"],
            context=context
        )
        
        # 构建执行计划
        return {
            "goal": goal,
            "plan": plan_steps,
            "total_steps": len(plan_steps),
            "status": "planned"
        }
        
    async def exec(self) -> Any:
        """执行规划逻辑"""
        # 先生成计划
        result = await super().exec()
        
        # 如果成功生成计划，可以选择性地构建执行图
        if isinstance(result, dict) and "plan" in result:
            # 这里可以根据计划动态构建子图
            # 简化实现：直接返回计划
            pass
            
        return result