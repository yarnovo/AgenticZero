"""
测试图配置解析功能
"""
import pytest
from pathlib import Path

from src.graph import load_graph_from_yaml, load_graph_from_dict, GraphExecutor


class TestGraphConfig:
    """测试图配置解析"""
    
    def test_load_from_dict(self):
        """测试从字典加载图配置"""
        config = {
            "name": "测试图",
            "nodes": [
                {"id": "start", "type": "SimpleNode", "name": "开始"},
                {"id": "end", "type": "SimpleNode", "name": "结束"}
            ],
            "edges": [
                {"from": "start", "to": "end"}
            ],
            "start_node": "start",
            "end_nodes": ["end"]
        }
        
        graph = load_graph_from_dict(config)
        assert graph.name == "测试图"
        assert len(graph.nodes) == 2
        assert graph.start_node_id == "start"
        assert "end" in graph.end_node_ids
    
    def test_load_from_yaml(self):
        """测试从YAML文件加载图配置"""
        yaml_file = Path("examples/graph_configs/simple_flow.yaml")
        if yaml_file.exists():
            graph = load_graph_from_yaml(str(yaml_file))
            assert graph.name == "简单顺序流程"
            assert graph.start_node_id == "start"
            assert len(graph.nodes) == 4
    
    @pytest.mark.asyncio
    async def test_execute_simple_graph(self):
        """测试执行简单图"""
        config = {
            "name": "简单测试",
            "nodes": [
                {"id": "n1", "type": "SimpleNode"},
                {"id": "n2", "type": "LoggingNode", "params": {"log_message": "测试"}},
                {"id": "n3", "type": "SimpleNode"}
            ],
            "edges": [
                {"from": "n1", "to": "n2"},
                {"from": "n2", "to": "n3"}
            ],
            "start_node": "n1",
            "end_nodes": ["n3"]
        }
        
        graph = load_graph_from_dict(config)
        executor = GraphExecutor(graph)
        
        result = await executor.execute()
        assert len(result.execution_history) == 3
        assert result.execution_history[0]["node_id"] == "n1"
        assert result.execution_history[-1]["node_id"] == "n3"


@pytest.mark.asyncio
async def test_conditional_execution():
    """测试条件执行"""
    config = {
        "name": "条件测试",
        "nodes": [
            {"id": "start", "type": "SimpleNode"},
            {"id": "check", "type": "ConditionalNode", "params": {"condition": lambda: True}},
            {"id": "true_path", "type": "SimpleNode"},
            {"id": "false_path", "type": "SimpleNode"},
            {"id": "end", "type": "SimpleNode"}
        ],
        "edges": [
            {"from": "start", "to": "check"},
            {"from": "check", "to": "true_path", "action": "true"},
            {"from": "check", "to": "false_path", "action": "false"},
            {"from": "true_path", "to": "end"},
            {"from": "false_path", "to": "end"}
        ],
        "start_node": "start",
        "end_nodes": ["end"]
    }
    
    graph = load_graph_from_dict(config)
    executor = GraphExecutor(graph)
    
    result = await executor.execute()
    
    # 验证走了正确的路径
    node_ids = [h["node_id"] for h in result.execution_history]
    assert "check" in node_ids
    assert "true_path" in node_ids
    assert "false_path" not in node_ids