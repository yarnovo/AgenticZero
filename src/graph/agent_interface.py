"""
Agent接口定义

定义AI节点与外部Agent的交互接口
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from dataclasses import dataclass


@dataclass
class AgentMessage:
    """Agent消息"""
    role: str  # system/user/assistant
    content: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class AgentResponse:
    """Agent响应"""
    content: str
    reasoning: Optional[str] = None
    confidence: float = 1.0
    metadata: Optional[Dict[str, Any]] = None


class IAgent(ABC):
    """Agent接口
    
    定义了AI节点与外部Agent交互的标准接口
    """
    
    @abstractmethod
    async def think(self, 
                   messages: List[AgentMessage], 
                   context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """让Agent思考并返回响应
        
        Args:
            messages: 对话历史
            context: 额外的上下文信息
            
        Returns:
            Agent的响应
        """
        pass
        
    @abstractmethod
    async def plan(self, 
                  goal: str, 
                  constraints: Optional[List[str]] = None,
                  context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """让Agent制定计划
        
        Args:
            goal: 目标描述
            constraints: 约束条件
            context: 上下文信息
            
        Returns:
            计划步骤列表
        """
        pass
        
    @abstractmethod
    async def decide(self, 
                    options: List[str], 
                    criteria: Optional[Dict[str, float]] = None,
                    context: Optional[Dict[str, Any]] = None) -> str:
        """让Agent做决策
        
        Args:
            options: 可选项列表
            criteria: 决策标准及权重
            context: 上下文信息
            
        Returns:
            选择的选项
        """
        pass
        
    @abstractmethod
    async def evaluate(self, 
                      subject: Any, 
                      criteria: List[str],
                      context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """让Agent评估
        
        Args:
            subject: 评估对象
            criteria: 评估标准
            context: 上下文信息
            
        Returns:
            评估结果
        """
        pass
        
    @property
    @abstractmethod
    def capabilities(self) -> List[str]:
        """获取Agent的能力列表"""
        pass
        
    @property
    @abstractmethod
    def model_info(self) -> Dict[str, Any]:
        """获取Agent的模型信息"""
        pass


class AgentProxy(IAgent):
    """Agent代理
    
    用于测试的简单Agent实现
    """
    
    def __init__(self, name: str = "TestAgent"):
        self.name = name
        
    async def think(self, messages: List[AgentMessage], context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """模拟思考"""
        return AgentResponse(
            content=f"[{self.name}] 基于输入进行了思考",
            reasoning="这是一个测试响应",
            confidence=0.8
        )
        
    async def plan(self, goal: str, constraints: Optional[List[str]] = None, context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """模拟规划"""
        return [
            {"step": 1, "action": "分析目标", "description": f"分析目标: {goal}"},
            {"step": 2, "action": "制定方案", "description": "制定实施方案"},
            {"step": 3, "action": "执行计划", "description": "执行具体步骤"}
        ]
        
    async def decide(self, options: List[str], criteria: Optional[Dict[str, float]] = None, context: Optional[Dict[str, Any]] = None) -> str:
        """模拟决策"""
        return options[0] if options else "default"
        
    async def evaluate(self, subject: Any, criteria: List[str], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """模拟评估"""
        scores = {criterion: 0.7 + hash(criterion) % 3 * 0.1 for criterion in criteria}
        return {
            "scores": scores,
            "average": sum(scores.values()) / len(scores) if scores else 0,
            "summary": f"对{subject}的评估完成"
        }
        
    @property
    def capabilities(self) -> List[str]:
        """获取能力列表"""
        return ["think", "plan", "decide", "evaluate"]
        
    @property
    def model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        return {
            "name": self.name,
            "type": "test",
            "version": "1.0"
        }