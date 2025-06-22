"""
复合控制节点

基于子图的复合控制节点实现
"""

from abc import abstractmethod
from typing import Any, Optional

from .node_types import ControlNode
from .core import Graph
from .executor import GraphExecutor


class CompositeControlNode(ControlNode):
    """复合控制节点基类
    
    使用内部子图实现复杂的控制逻辑
    """
    
    def __init__(self, node_id: str, name: Optional[str] = None, **kwargs):
        """初始化复合控制节点"""
        super().__init__(node_id, name, **kwargs)
        self.is_composite = True
        self.sub_graph = Graph(f"{node_id}_subgraph")
        self.sub_executor: Optional[GraphExecutor] = None
        self._setup_sub_graph()
        
    @abstractmethod
    def _setup_sub_graph(self):
        """设置子图结构 - 子类必须实现"""
        pass
        
    async def exec(self) -> Any:
        """执行子图"""
        # 创建子图执行器
        self.sub_executor = GraphExecutor(self.sub_graph)
        
        # 获取输入数据
        initial_input = self._input_data if hasattr(self, '_input_data') else None
        
        # 执行子图
        context = await self.sub_executor.execute(initial_input=initial_input)
        
        # 获取子图的输出
        end_nodes = list(self.sub_graph.end_node_ids)
        if end_nodes:
            # 返回第一个结束节点的输出
            return context.node_outputs.get(end_nodes[0])
        else:
            # 如果没有明确的结束节点，返回所有节点的输出
            return context.node_outputs
            
    async def post(self) -> Optional[str]:
        """根据子图执行结果决定下一步"""
        # 默认行为：如果子图成功执行，继续
        if self.sub_executor and self.sub_executor.context:
            # 检查是否有特殊的控制标记
            if isinstance(self.result, dict):
                # 处理特殊的控制流标记
                if "__branch__" in self.result:
                    return self.result["__branch__"]
                elif "__exit__" in self.result:
                    return "exit"
                elif "__error__" in self.result:
                    return "error"
        return None
        
    def add_node_to_subgraph(self, node: Any):
        """向子图添加节点"""
        self.sub_graph.add_node(node)
        
    def add_edge_to_subgraph(self, from_id: str, to_id: str, condition: Optional[str] = None):
        """向子图添加边"""
        self.sub_graph.add_edge(from_id, to_id, condition)
        
    def set_subgraph_start(self, node_id: str):
        """设置子图起始节点"""
        self.sub_graph.set_start(node_id)
        
    def add_subgraph_end(self, node_id: str):
        """添加子图结束节点"""
        self.sub_graph.add_end(node_id)