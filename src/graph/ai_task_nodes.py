"""
AI任务节点

具有智能处理能力的任务节点
"""

from abc import abstractmethod
from typing import Any

from .agent_interface import AgentMessage, AgentProxy, IAgent
from .node_types import TaskNode


class AITaskNode(TaskNode):
    """AI任务节点基类

    通过Agent赋予任务节点智能处理能力
    """

    def __init__(
        self,
        node_id: str,
        name: str | None = None,
        agent: IAgent | None = None,
        **kwargs,
    ):
        """初始化AI任务节点

        Args:
            node_id: 节点ID
            name: 节点名称
            agent: AI Agent实例
        """
        super().__init__(node_id, name, **kwargs)
        self.agent = agent or AgentProxy(f"TaskAgent_{node_id}")
        self.conversation_history: list[AgentMessage] = []

    async def _consult_agent(
        self, prompt: str, context: dict[str, Any] | None = None
    ) -> str:
        """咨询Agent

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
            messages=self.conversation_history, context=context
        )

        # 记录响应
        assistant_msg = AgentMessage(
            role="assistant",
            content=response.content,
            metadata={
                "reasoning": response.reasoning,
                "confidence": response.confidence,
            },
        )
        self.conversation_history.append(assistant_msg)

        return response.content

    async def exec(self) -> Any:
        """执行AI任务"""
        # 获取输入
        input_data = self._input_data if hasattr(self, "_input_data") else None

        # 构建上下文
        context = {
            "node_id": self.node_id,
            "node_name": self.name,
            "task_type": self.__class__.__name__,
            "input": input_data,
        }

        # 执行智能处理
        return await self._process_with_ai(input_data, context)

    @abstractmethod
    async def _process_with_ai(self, input_data: Any, context: dict[str, Any]) -> Any:
        """使用AI处理任务 - 子类必须实现

        Args:
            input_data: 输入数据
            context: 上下文信息

        Returns:
            处理结果
        """
        pass


class AIAnalyzer(AITaskNode):
    """AI分析任务节点

    使用AI进行数据分析
    """

    def __init__(
        self,
        node_id: str,
        name: str | None = None,
        analysis_type: str = "general",
        agent: IAgent | None = None,
        **kwargs,
    ):
        """初始化AI分析节点

        Args:
            node_id: 节点ID
            name: 节点名称
            analysis_type: 分析类型
            agent: AI Agent实例
        """
        self.analysis_type = analysis_type
        super().__init__(node_id, name, agent, **kwargs)

    async def _process_with_ai(self, input_data: Any, context: dict[str, Any]) -> Any:
        """使用AI进行分析"""
        prompt = f"""
        请对以下数据进行{self.analysis_type}分析：

        数据: {input_data}

        请提供：
        1. 主要发现
        2. 关键洞察
        3. 建议行动

        返回JSON格式的分析结果。
        """

        analysis = await self._consult_agent(prompt, context)

        # 尝试解析JSON
        try:
            import json

            result = json.loads(analysis)
            return {
                "analysis_type": self.analysis_type,
                "input": input_data,
                "findings": result,
            }
        except Exception:
            # 如果解析失败，返回原始文本
            return {
                "analysis_type": self.analysis_type,
                "input": input_data,
                "findings": {"raw_analysis": analysis},
            }


class AIGenerator(AITaskNode):
    """AI生成任务节点

    使用AI生成内容
    """

    def __init__(
        self,
        node_id: str,
        name: str | None = None,
        generation_type: str = "text",
        agent: IAgent | None = None,
        **kwargs,
    ):
        """初始化AI生成节点

        Args:
            node_id: 节点ID
            name: 节点名称
            generation_type: 生成类型（text/code/plan等）
            agent: AI Agent实例
        """
        self.generation_type = generation_type
        super().__init__(node_id, name, agent, **kwargs)

    async def _process_with_ai(self, input_data: Any, context: dict[str, Any]) -> Any:
        """使用AI生成内容"""
        # 根据生成类型构建不同的提示词
        if self.generation_type == "code":
            prompt = f"""
            基于以下需求生成代码：
            需求: {input_data}

            请生成完整、可运行的代码，并添加必要的注释。
            """
        elif self.generation_type == "plan":
            prompt = f"""
            基于以下目标生成详细计划：
            目标: {input_data}

            请生成结构化的执行计划，包括步骤、依赖和预期结果。
            """
        else:  # text
            prompt = f"""
            基于以下输入生成文本内容：
            输入: {input_data}

            请生成高质量、相关的文本内容。
            """

        generated = await self._consult_agent(prompt, context)

        return {
            "generation_type": self.generation_type,
            "input": input_data,
            "generated": generated,
            "metadata": {"agent": self.agent.model_info, "timestamp": "current_time"},
        }


class AIEvaluator(AITaskNode):
    """AI评估任务节点

    使用AI进行评估和打分
    """

    def __init__(
        self,
        node_id: str,
        name: str | None = None,
        criteria: list[str] | None = None,
        agent: IAgent | None = None,
        **kwargs,
    ):
        """初始化AI评估节点

        Args:
            node_id: 节点ID
            name: 节点名称
            criteria: 评估标准列表
            agent: AI Agent实例
        """
        self.criteria = criteria or ["质量", "完整性", "准确性"]
        super().__init__(node_id, name, agent, **kwargs)

    async def _process_with_ai(self, input_data: Any, context: dict[str, Any]) -> Any:
        """使用AI进行评估"""
        # 让Agent进行评估
        evaluation = await self.agent.evaluate(
            subject=input_data, criteria=self.criteria, context=context
        )

        return {
            "subject": input_data,
            "criteria": self.criteria,
            "evaluation": evaluation,
            "overall_score": evaluation.get("average", 0),
            "recommendation": self._generate_recommendation(evaluation),
        }

    def _generate_recommendation(self, evaluation: dict[str, Any]) -> str:
        """基于评估结果生成建议"""
        avg_score = evaluation.get("average", 0)
        if avg_score >= 0.8:
            return "优秀，继续保持"
        elif avg_score >= 0.6:
            return "良好，仍有改进空间"
        else:
            return "需要显著改进"
