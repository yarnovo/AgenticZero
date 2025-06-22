"""
原子控制节点

基于ControlNode的原子化控制流节点实现
"""

from typing import Any, Callable, Optional, Dict, List

from .node_types import ControlNode


class AtomicControlNode(ControlNode):
    """原子控制节点基类
    
    提供原子控制节点的通用功能
    """
    
    def __init__(self, node_id: str, name: Optional[str] = None, **kwargs):
        """初始化原子控制节点"""
        super().__init__(node_id, name, **kwargs)
        self.is_atomic = True
        
    def reset(self) -> None:
        """重置节点状态"""
        super().reset()
        # 清除控制结果
        self._control_result = None


class SequenceControlNode(AtomicControlNode):
    """顺序控制节点
    
    原子化的顺序执行节点，处理数据并传递给下一个节点
    """
    
    def __init__(
        self, 
        node_id: str, 
        name: Optional[str] = None,
        process_func: Optional[Callable[[Any], Any]] = None,
        **kwargs
    ):
        """初始化顺序控制节点
        
        Args:
            node_id: 节点ID
            name: 节点名称
            process_func: 数据处理函数
        """
        super().__init__(node_id, name, **kwargs)
        self.process_func = process_func or (lambda x: x)
        
    async def exec(self) -> Any:
        """执行顺序处理"""
        input_data = self._get_input_data()
        return self.process_func(input_data)
        
    async def post(self) -> Optional[str]:
        """顺序节点默认继续执行"""
        # 保存控制决策以供post使用
        self._control_result = None
        return None


class BranchControlNode(AtomicControlNode):
    """分支控制节点
    
    根据条件选择不同的执行路径
    """
    
    def __init__(
        self,
        node_id: str,
        name: Optional[str] = None,
        condition_func: Optional[Callable[[Any], str]] = None,
        **kwargs
    ):
        """初始化分支控制节点
        
        Args:
            node_id: 节点ID
            name: 节点名称  
            condition_func: 条件函数，返回分支名称
        """
        super().__init__(node_id, name, **kwargs)
        self.condition_func = condition_func or (lambda x: "default")
        
    async def exec(self) -> Any:
        """执行条件判断"""
        input_data = self._get_input_data()
        branch = self.condition_func(input_data)
        # 返回带有action的结果，以便执行器能正确处理
        return {"action": branch, "data": input_data}
        
    async def post(self) -> Optional[str]:
        """返回选择的分支"""
        if self.result and isinstance(self.result, dict):
            branch = self.result.get("action", "default")
            # 保存控制决策
            self._control_result = branch
            return branch
        return "default"


class MergeControlNode(AtomicControlNode):
    """合并控制节点
    
    将多个输入路径合并为一个输出
    """
    
    def __init__(
        self,
        node_id: str,
        name: Optional[str] = None,
        merge_func: Optional[Callable[[list], Any]] = None,
        **kwargs
    ):
        """初始化合并控制节点
        
        Args:
            node_id: 节点ID
            name: 节点名称
            merge_func: 合并函数
        """
        super().__init__(node_id, name, **kwargs)
        self.merge_func = merge_func or (lambda x: x[-1] if x else None)
        self.merge_inputs: List[Any] = []
        self._waiting_for_inputs = False
        
    async def exec(self) -> Any:
        """执行合并逻辑"""
        input_data = self._get_input_data()
        
        # 处理特殊的合并数据格式
        if isinstance(input_data, dict) and "__merge__" in input_data:
            # 执行器传递的多输入数据
            merge_data = input_data["__merge__"]
            return self.merge_func(merge_data)
        elif isinstance(input_data, list):
            # 直接的列表输入
            return self.merge_func(input_data)
        else:
            # 单个输入，收集并等待
            self.merge_inputs.append(input_data)
            if self._check_merge_complete():
                result = self.merge_func(self.merge_inputs)
                self.merge_inputs = []  # 清空以备下次使用
                return result
            else:
                return {"__waiting__": True, "collected": len(self.merge_inputs)}
                
    def _check_merge_complete(self) -> bool:
        """检查是否所有输入都已到达"""
        # 简化逻辑：可以根据图结构判断
        if hasattr(self, 'graph') and self.graph:
            incoming_edges = self.graph.get_incoming_edges(self.node_id)
            expected_count = len(incoming_edges)
            return len(self.merge_inputs) >= expected_count
        return True
            
    async def post(self) -> Optional[str]:
        """合并节点继续执行"""
        return None


class ForkControlNode(AtomicControlNode):
    """分叉控制节点
    
    将执行流分叉为多个并行路径
    """
    
    def __init__(
        self,
        node_id: str,
        name: Optional[str] = None,
        fork_count: int = 2,
        **kwargs
    ):
        """初始化分叉控制节点
        
        Args:
            node_id: 节点ID
            name: 节点名称
            fork_count: 分叉数量
        """
        super().__init__(node_id, name, **kwargs)
        self.fork_count = fork_count
        
    async def exec(self) -> Any:
        """执行分叉逻辑"""
        input_data = self._get_input_data()
        return {
            "__fork__": True,
            "count": self.fork_count,
            "data": input_data
        }
        
    async def post(self) -> Optional[str]:
        """分叉节点返回特殊标记"""
        # 分叉节点不返回特定路径，让执行器处理并行
        return "__fork__"


class JoinControlNode(AtomicControlNode):
    """汇聚控制节点
    
    等待所有并行路径完成并汇聚结果
    """
    
    def __init__(
        self,
        node_id: str,
        name: Optional[str] = None,
        join_func: Optional[Callable[[list], Any]] = None,
        **kwargs
    ):
        """初始化汇聚控制节点
        
        Args:
            node_id: 节点ID
            name: 节点名称
            join_func: 汇聚函数
        """
        super().__init__(node_id, name, **kwargs)
        self.join_func = join_func or (lambda x: {"joined": x})
        self.join_inputs: List[Any] = []
        self.expected_count: Optional[int] = None
        self._join_complete = False
        
    async def exec(self) -> Any:
        """执行汇聚逻辑"""
        input_data = self._get_input_data()
        
        # 处理执行器传递的列表数据（多个输入已经收集好）
        if isinstance(input_data, list):
            # 直接处理列表输入
            self._join_complete = True
            return self.join_func(input_data)
        else:
            # 收集单个输入
            self.join_inputs.append(input_data)
            
            # 确定预期输入数量
            if self.expected_count is None:
                self.expected_count = self._get_expected_count()
                
            if len(self.join_inputs) >= self.expected_count:
                # 所有输入已到达
                result = self.join_func(self.join_inputs)
                self._join_complete = True
                self.join_inputs = []  # 清空以备下次使用
                return result
            else:
                # 还在等待更多输入
                return {"__waiting__": True, "collected": len(self.join_inputs), "expected": self.expected_count}
                
    def _get_expected_count(self) -> int:
        """获取预期的输入数量"""
        if hasattr(self, 'graph') and self.graph:
            incoming_edges = self.graph.get_incoming_edges(self.node_id)
            return len(incoming_edges)
        return 2  # 默认至少等待2个输入
            
    async def post(self) -> Optional[str]:
        """汇聚完成后继续执行"""
        if self.result and isinstance(self.result, dict):
            if "__waiting__" in self.result:
                # 还在等待更多输入，不继续执行
                return "__waiting__"
        # 汇聚完成，继续执行
        return None
        
    def reset(self) -> None:
        """重置节点状态"""
        super().reset()
        self.join_inputs = []
        self.expected_count = None
        self._join_complete = False