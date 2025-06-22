"""
测试增强图功能

测试序列化、快照和恢复功能
"""

import pytest
import json
import asyncio
from pathlib import Path
from src.graph import (
    EnhancedGraph,
    GraphSnapshot,
    ResumableExecutor,
    SequenceControlNode,
    BranchControlNode,
    TaskNode,
    NodeStatus
)


@pytest.mark.unit
class TestGraphSnapshot:
    """测试图快照"""
    
    def test_snapshot_creation(self):
        """测试快照创建"""
        snapshot = GraphSnapshot("test_graph")
        
        assert snapshot.graph_id == "test_graph"
        assert snapshot.timestamp is not None
        assert snapshot.graph_structure == {}
        assert snapshot.execution_state == {}
        assert snapshot.node_states == {}
        assert snapshot.context_data == {}
        
    def test_capture_graph(self):
        """测试捕获图结构"""
        graph = EnhancedGraph("test")
        node1 = SequenceControlNode("n1", "节点1")
        node2 = SequenceControlNode("n2", "节点2")
        
        graph.add_node(node1)
        graph.add_node(node2)
        graph.add_edge("n1", "n2")
        graph.set_start("n1")
        graph.add_end("n2")
        
        snapshot = GraphSnapshot("test")
        snapshot.capture_graph(graph)
        
        assert snapshot.graph_structure["name"] == "test"
        assert len(snapshot.graph_structure["nodes"]) == 2
        assert len(snapshot.graph_structure["edges"]) == 1
        assert snapshot.graph_structure["start_node"] == "n1"
        assert "n2" in snapshot.graph_structure["end_nodes"]
        
    def test_snapshot_to_dict(self):
        """测试快照转字典"""
        snapshot = GraphSnapshot("test")
        snapshot.context_data = {"key": "value"}
        
        data = snapshot.to_dict()
        
        assert data["graph_id"] == "test"
        assert "timestamp" in data
        assert data["context_data"] == {"key": "value"}
        
    def test_snapshot_from_dict(self):
        """测试从字典创建快照"""
        data = {
            "graph_id": "restored",
            "timestamp": "2024-01-01T10:00:00",
            "graph_structure": {"name": "test"},
            "execution_state": {"current_node": "n1"},
            "node_states": {},
            "context_data": {"test": True}
        }
        
        snapshot = GraphSnapshot.from_dict(data)
        
        assert snapshot.graph_id == "restored"
        assert snapshot.timestamp == "2024-01-01T10:00:00"
        assert snapshot.context_data["test"] is True


@pytest.mark.unit
class TestEnhancedGraph:
    """测试增强图"""
    
    def test_enhanced_graph_creation(self):
        """测试增强图创建"""
        graph = EnhancedGraph("enhanced")
        
        assert graph.name == "enhanced"
        assert graph.checkpoints == []
        assert graph.is_resumable is True
        assert graph.auto_checkpoint is True
        assert graph.checkpoint_interval == 5
        
    def test_create_snapshot(self):
        """测试创建快照"""
        graph = EnhancedGraph("test")
        node = SequenceControlNode("n1", "测试节点")
        graph.add_node(node)
        
        snapshot = graph.create_snapshot()
        
        assert snapshot.graph_id == "test"
        assert "n1" in snapshot.graph_structure["nodes"]
        
    def test_save_load_snapshot(self, tmp_path):
        """测试保存和加载快照"""
        graph = EnhancedGraph("test")
        snapshot = graph.create_snapshot()
        snapshot.context_data = {"test": "data"}
        
        # 保存快照
        file_path = tmp_path / "test_snapshot.json"
        graph.save_snapshot(snapshot, file_path)
        
        assert file_path.exists()
        
        # 加载快照
        loaded = graph.load_snapshot(file_path)
        
        assert loaded.graph_id == "test"
        assert loaded.context_data["test"] == "data"
        
    def test_graph_serialization(self):
        """测试图序列化"""
        graph = EnhancedGraph("serialize_test")
        
        # 添加节点
        node1 = SequenceControlNode("seq1", "顺序1", lambda x: x + 1)
        node2 = BranchControlNode("branch1", "分支1", lambda x: "high" if x > 5 else "low")
        
        graph.add_node(node1)
        graph.add_node(node2)
        graph.add_edge("seq1", "branch1")
        graph.set_start("seq1")
        
        # 序列化
        serialized = graph.serialize()
        
        assert serialized["name"] == "serialize_test"
        assert len(serialized["nodes"]) == 2
        assert serialized["nodes"]["seq1"]["type"] == "SequenceControlNode"
        assert serialized["metadata"]["is_resumable"] is True
        
    def test_graph_deserialization(self):
        """测试图反序列化"""
        data = {
            "name": "restored_graph",
            "nodes": {
                "n1": {
                    "type": "SequenceControlNode",
                    "module": "src.graph.atomic_control_nodes",
                    "name": "节点1",
                    "status": "pending"
                },
                "n2": {
                    "type": "SequenceControlNode",
                    "module": "src.graph.atomic_control_nodes",
                    "name": "节点2",
                    "status": "pending"
                }
            },
            "edges": [{"from": "n1", "to": "n2"}],
            "start_node": "n1",
            "end_nodes": ["n2"],
            "metadata": {
                "is_resumable": True,
                "checkpoint_interval": 10
            }
        }
        
        # 提供节点工厂
        node_factory = {
            "SequenceControlNode": SequenceControlNode
        }
        
        graph = EnhancedGraph.deserialize(data, node_factory)
        
        assert graph.name == "restored_graph"
        assert graph.checkpoint_interval == 10
        assert "n1" in graph.nodes


@pytest.mark.unit
class TestResumableExecutor:
    """测试可恢复执行器"""
    
    def test_resumable_executor_creation(self):
        """测试执行器创建"""
        graph = EnhancedGraph("test")
        executor = ResumableExecutor(graph)
        
        assert executor.graph is graph
        assert executor.snapshots == []
        assert executor.is_paused is False
        assert executor.checkpoint_counter == 0
        assert len(executor._on_node_start_hooks) == 0
        
    def test_register_hooks(self):
        """测试注册钩子"""
        graph = EnhancedGraph("test")
        executor = ResumableExecutor(graph)
        
        def node_start_hook(node):
            pass
            
        def node_complete_hook(node):
            pass
            
        executor.register_hook("node_start", node_start_hook)
        executor.register_hook("node_complete", node_complete_hook)
        
        assert len(executor._on_node_start_hooks) == 1
        assert len(executor._on_node_complete_hooks) == 1
        
    @pytest.mark.asyncio
    async def test_execute_with_checkpoints(self):
        """测试带检查点的执行"""
        graph = EnhancedGraph("checkpoint_test")
        
        # 创建简单流程
        node1 = TaskNode("task1", "任务1", lambda x: x + 1)
        node2 = TaskNode("task2", "任务2", lambda x: x * 2)
        
        graph.add_node(node1)
        graph.add_node(node2)
        graph.add_edge("task1", "task2")
        graph.set_start("task1")
        graph.add_end("task2")
        
        executor = ResumableExecutor(graph)
        
        # 记录检查点
        checkpoints = []
        
        def checkpoint_callback(snapshot):
            checkpoints.append(snapshot)
            
        context = await executor.execute_with_checkpoints(
            initial_input=5,
            checkpoint_callback=checkpoint_callback
        )
        
        assert context.graph_output == 12  # (5 + 1) * 2
        assert len(checkpoints) >= 2  # 至少初始和最终检查点
        
    @pytest.mark.asyncio
    async def test_pause_resume(self):
        """测试暂停和恢复"""
        graph = EnhancedGraph("pause_test")
        executor = ResumableExecutor(graph)
        
        assert executor.is_paused is False
        
        executor.pause()
        assert executor.is_paused is True
        
        executor.resume()
        assert executor.is_paused is False
        
    @pytest.mark.asyncio
    async def test_resume_from_snapshot(self):
        """测试从快照恢复"""
        graph = EnhancedGraph("resume_test")
        
        # 创建会失败的节点
        class FailingTask(TaskNode):
            def __init__(self, node_id, name):
                super().__init__(node_id, name)
                self.attempt = 0
                
            async def _execute_task(self, input_data):
                self.attempt += 1
                if self.attempt == 1:
                    raise Exception("第一次失败")
                return {"result": input_data}
                
        # 构建图
        task1 = TaskNode("task1", "任务1", lambda x: {"step1": x})
        task2 = FailingTask("task2", "会失败的任务")
        task3 = TaskNode("task3", "任务3", lambda x: {"final": x})
        
        graph.add_node(task1)
        graph.add_node(task2)
        graph.add_node(task3)
        
        graph.add_edge("task1", "task2")
        graph.add_edge("task2", "task3")
        
        graph.set_start("task1")
        graph.add_end("task3")
        
        executor = ResumableExecutor(graph)
        
        # 第一次执行（会失败）
        try:
            await executor.execute_with_checkpoints(initial_input="test")
            assert False, "应该失败"
        except Exception as e:
            assert "第一次失败" in str(e)
            
        # 获取最后的快照
        assert len(executor.snapshots) > 0
        last_snapshot = executor.snapshots[-1]
        
        # 从快照恢复（第二次会成功）
        context = await executor.resume_from_snapshot(last_snapshot)
        
        # 验证执行完成
        assert "task3" in context.visited_nodes
        assert context.graph_output["final"]["result"]["step1"] == "test"
        
    @pytest.mark.asyncio
    async def test_hook_execution(self):
        """测试钩子执行"""
        graph = EnhancedGraph("hook_test")
        node = TaskNode("task1", "测试任务", lambda x: x)
        graph.add_node(node)
        graph.set_start("task1")
        graph.add_end("task1")
        
        executor = ResumableExecutor(graph)
        
        # 记录钩子调用
        hook_calls = []
        
        async def async_hook(node):
            hook_calls.append(("async", node.node_id))
            
        def sync_hook(node):
            hook_calls.append(("sync", node.node_id))
            
        executor.register_hook("node_start", async_hook)
        executor.register_hook("node_complete", sync_hook)
        
        await executor.execute_with_checkpoints(initial_input="test")
        
        assert ("async", "task1") in hook_calls
        assert ("sync", "task1") in hook_calls
        
    @pytest.mark.asyncio
    async def test_error_checkpoint(self):
        """测试错误时的检查点"""
        graph = EnhancedGraph("error_test")
        
        def error_func(x):
            raise ValueError("测试错误")
            
        node = TaskNode("error_task", "错误任务", error_func)
        graph.add_node(node)
        graph.set_start("error_task")
        graph.add_end("error_task")
        
        executor = ResumableExecutor(graph)
        
        checkpoints = []
        
        def checkpoint_callback(snapshot):
            checkpoints.append(snapshot)
            
        try:
            await executor.execute_with_checkpoints(
                initial_input="test",
                checkpoint_callback=checkpoint_callback
            )
        except ValueError:
            pass
            
        # 验证错误检查点
        assert len(checkpoints) > 0
        error_checkpoint = checkpoints[-1]
        assert error_checkpoint.context_data["error"] == "测试错误"
        assert error_checkpoint.context_data["error_type"] == "ValueError"