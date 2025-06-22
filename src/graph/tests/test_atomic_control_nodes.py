"""
测试原子控制节点

测试各种原子控制节点的功能
"""

import pytest
from src.graph import (
    SequenceControlNode,
    BranchControlNode,
    MergeControlNode,
    ForkControlNode,
    JoinControlNode,
    Graph
)


@pytest.mark.unit
class TestSequenceControlNode:
    """测试顺序控制节点"""
    
    def test_sequence_node_creation(self):
        """测试顺序节点创建"""
        node = SequenceControlNode("seq1", "顺序节点")
        assert node.node_id == "seq1"
        assert node.is_atomic is True
        
    def test_sequence_node_with_func(self):
        """测试带处理函数的顺序节点"""
        node = SequenceControlNode(
            "seq2", 
            "处理节点",
            process_func=lambda x: x * 2
        )
        assert node.process_func is not None
        
    @pytest.mark.asyncio
    async def test_sequence_node_execution(self):
        """测试顺序节点执行"""
        node = SequenceControlNode(
            "seq3",
            "执行节点",
            process_func=lambda x: {"processed": x}
        )
        node._input_data = "test_data"
        
        result = await node.exec()
        assert result == {"processed": "test_data"}
        
    @pytest.mark.asyncio
    async def test_sequence_node_post(self):
        """测试顺序节点后处理"""
        node = SequenceControlNode("seq4", "后处理节点")
        next_node = await node.post()
        assert next_node is None  # 顺序节点默认继续执行


@pytest.mark.unit
class TestBranchControlNode:
    """测试分支控制节点"""
    
    def test_branch_node_creation(self):
        """测试分支节点创建"""
        node = BranchControlNode("branch1", "分支节点")
        assert node.condition_func is not None
        
    def test_branch_node_with_condition(self):
        """测试带条件函数的分支节点"""
        def condition(x):
            return "high" if x > 10 else "low"
            
        node = BranchControlNode(
            "branch2",
            "条件分支",
            condition_func=condition
        )
        assert node.condition_func is condition
        
    @pytest.mark.asyncio
    async def test_branch_node_execution(self):
        """测试分支节点执行"""
        node = BranchControlNode(
            "branch3",
            "执行分支",
            condition_func=lambda x: "path_a" if x > 5 else "path_b"
        )
        node._input_data = 10
        
        result = await node.exec()
        assert result == {"branch": "path_a", "data": 10}
        
    @pytest.mark.asyncio
    async def test_branch_node_post(self):
        """测试分支节点后处理"""
        node = BranchControlNode("branch4", "后处理分支")
        node.result = {"branch": "custom_path", "data": "test"}
        
        next_node = await node.post()
        assert next_node == "custom_path"
        assert node._control_result == "custom_path"


@pytest.mark.unit
class TestMergeControlNode:
    """测试合并控制节点"""
    
    def test_merge_node_creation(self):
        """测试合并节点创建"""
        node = MergeControlNode("merge1", "合并节点")
        assert node.merge_inputs == []
        assert node._waiting_for_inputs is False
        
    def test_merge_node_with_func(self):
        """测试带合并函数的节点"""
        def merge_func(inputs):
            return {"merged": inputs, "count": len(inputs)}
            
        node = MergeControlNode(
            "merge2",
            "自定义合并",
            merge_func=merge_func
        )
        assert node.merge_func is merge_func
        
    @pytest.mark.asyncio
    async def test_merge_node_single_input(self):
        """测试合并节点单输入"""
        node = MergeControlNode("merge3", "单输入合并")
        node._input_data = "single_input"
        
        # 创建模拟图结构
        graph = Graph()
        graph.add_node(node)
        node.graph = graph
        
        result = await node.exec()
        # 由于只有一个输入且没有入边，应该立即返回
        assert result == "single_input"  # 默认函数返回最后一个输入
        
    @pytest.mark.asyncio
    async def test_merge_node_list_input(self):
        """测试合并节点列表输入"""
        node = MergeControlNode("merge4", "列表合并")
        node._input_data = ["input1", "input2", "input3"]
        
        result = await node.exec()
        assert result == "input3"  # 默认函数返回最后一个
        
    @pytest.mark.asyncio
    async def test_merge_node_special_format(self):
        """测试合并节点特殊格式"""
        node = MergeControlNode(
            "merge5",
            "特殊合并",
            merge_func=lambda x: {"all": x}
        )
        node._input_data = {"__merge__": ["a", "b", "c"]}
        
        result = await node.exec()
        assert result == {"all": ["a", "b", "c"]}


@pytest.mark.unit
class TestForkControlNode:
    """测试分叉控制节点"""
    
    def test_fork_node_creation(self):
        """测试分叉节点创建"""
        node = ForkControlNode("fork1", "分叉节点")
        assert node.fork_count == 2
        
    def test_fork_node_custom_count(self):
        """测试自定义分叉数量"""
        node = ForkControlNode("fork2", "多分叉", fork_count=5)
        assert node.fork_count == 5
        
    @pytest.mark.asyncio
    async def test_fork_node_execution(self):
        """测试分叉节点执行"""
        node = ForkControlNode("fork3", "执行分叉", fork_count=3)
        node._input_data = {"test": "data"}
        
        result = await node.exec()
        assert result == {
            "__fork__": True,
            "count": 3,
            "data": {"test": "data"}
        }
        
    @pytest.mark.asyncio
    async def test_fork_node_post(self):
        """测试分叉节点后处理"""
        node = ForkControlNode("fork4", "后处理分叉")
        next_action = await node.post()
        assert next_action == "__fork__"


@pytest.mark.unit
class TestJoinControlNode:
    """测试汇聚控制节点"""
    
    def test_join_node_creation(self):
        """测试汇聚节点创建"""
        node = JoinControlNode("join1", "汇聚节点")
        assert node.join_inputs == []
        assert node.expected_count is None
        assert node._join_complete is False
        
    def test_join_node_with_func(self):
        """测试带汇聚函数的节点"""
        def join_func(inputs):
            return {
                "joined": True,
                "inputs": inputs,
                "average": sum(inputs) / len(inputs) if inputs else 0
            }
            
        node = JoinControlNode(
            "join2",
            "自定义汇聚",
            join_func=join_func
        )
        assert node.join_func is join_func
        
    @pytest.mark.asyncio
    async def test_join_node_collect_inputs(self):
        """测试汇聚节点收集输入"""
        node = JoinControlNode("join3", "收集汇聚")
        node.expected_count = 3
        
        # 第一个输入
        node._input_data = "input1"
        result1 = await node.exec()
        assert result1["__waiting__"] is True
        assert result1["collected"] == 1
        
        # 第二个输入
        node._input_data = "input2"
        result2 = await node.exec()
        assert result2["__waiting__"] is True
        assert result2["collected"] == 2
        
        # 第三个输入（完成）
        node._input_data = "input3"
        result3 = await node.exec()
        assert "joined" in result3
        assert node._join_complete is True
        
    @pytest.mark.asyncio
    async def test_join_node_special_format(self):
        """测试汇聚节点特殊格式"""
        node = JoinControlNode("join4", "特殊汇聚")
        node._input_data = {
            "__join__": ["result1", "result2", "result3"]
        }
        
        result = await node.exec()
        assert result["joined"] == ["result1", "result2", "result3"]
        assert node._join_complete is True
        
    @pytest.mark.asyncio
    async def test_join_node_post(self):
        """测试汇聚节点后处理"""
        node = JoinControlNode("join5", "后处理汇聚")
        
        # 等待中
        node.result = {"__waiting__": True}
        next_action = await node.post()
        assert next_action == "__waiting__"
        
        # 完成
        node.result = {"joined": ["a", "b"]}
        next_action = await node.post()
        assert next_action is None
        
    def test_join_node_reset(self):
        """测试汇聚节点重置"""
        node = JoinControlNode("join6", "重置汇聚")
        node.join_inputs = ["a", "b"]
        node.expected_count = 2
        node._join_complete = True
        
        node.reset()
        
        assert node.join_inputs == []
        assert node.expected_count is None
        assert node._join_complete is False