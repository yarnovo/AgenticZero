"""
测试图配置解析功能
"""

from pathlib import Path

import pytest

from src.graph import GraphExecutor, load_graph_from_dict, load_graph_from_yaml


class TestGraphConfig:
    """测试图配置解析"""

    def test_load_from_dict(self):
        """测试从字典加载图配置"""
        config = {
            "name": "测试图",
            "nodes": [
                {"id": "start", "type": "SequenceControlNode", "name": "开始"},
                {"id": "end", "type": "SequenceControlNode", "name": "结束"},
            ],
            "edges": [{"from": "start", "to": "end"}],
            "start_node": "start",
            "end_nodes": ["end"],
        }

        graph = load_graph_from_dict(config)
        assert graph.name == "测试图"
        assert len(graph.nodes) == 2
        assert graph.start_node_id == "start"
        assert "end" in graph.end_node_ids

    def test_load_from_yaml(self):
        """测试从YAML文件加载图配置"""
        yaml_file = Path("examples/graph_configs/composite_nodes_flow.yaml")
        if yaml_file.exists():
            graph = load_graph_from_yaml(str(yaml_file))
            assert graph.name == "复合节点工作流示例"
            assert graph.start_node_id == "data_validator"
            assert len(graph.nodes) == 4

    @pytest.mark.asyncio
    async def test_execute_simple_graph(self):
        """测试执行简单图"""
        config = {
            "name": "简单测试",
            "nodes": [
                {"id": "n1", "type": "SequenceControlNode"},
                {
                    "id": "n2",
                    "type": "SequenceControlNode",
                    "params": {"func": "lambda x: f'处理: {x}'"},
                },
                {"id": "n3", "type": "SequenceControlNode"},
            ],
            "edges": [{"from": "n1", "to": "n2"}, {"from": "n2", "to": "n3"}],
            "start_node": "n1",
            "end_nodes": ["n3"],
        }

        graph = load_graph_from_dict(config)
        executor = GraphExecutor(graph)

        result = await executor.execute(initial_input="测试数据")
        assert len(result.execution_history) == 3
        assert result.execution_history[0]["node_id"] == "n1"
        assert result.execution_history[-1]["node_id"] == "n3"


@pytest.mark.asyncio
async def test_conditional_execution():
    """测试条件执行"""
    # 使用新的节点类型
    from src.graph import BranchControlNode, Graph, GraphExecutor, MergeControlNode, SequenceControlNode, TaskNode

    graph = Graph("条件测试")

    # 创建节点
    start = SequenceControlNode("start", "开始", lambda x: x)
    check = BranchControlNode("check", "条件检查", lambda x: "true" if x > 50 else "false")
    true_path = TaskNode("true_path", "真路径", lambda x: f"大值: {x}")
    false_path = TaskNode("false_path", "假路径", lambda x: f"小值: {x}")
    end = MergeControlNode("end", "结束")

    # 添加节点
    graph.add_node(start)
    graph.add_node(check)
    graph.add_node(true_path)
    graph.add_node(false_path)
    graph.add_node(end)

    # 添加边
    graph.add_edge("start", "check")
    graph.add_edge("check", "true_path", "true")
    graph.add_edge("check", "false_path", "false")
    graph.add_edge("true_path", "end")
    graph.add_edge("false_path", "end")

    # 设置起始和结束节点
    graph.set_start("start")
    graph.add_end("end")

    executor = GraphExecutor(graph)
    result = await executor.execute(initial_input=75)

    # 验证走了正确的路径
    node_ids = [h["node_id"] for h in result.execution_history]
    assert "check" in node_ids
    assert "true_path" in node_ids
    assert "false_path" not in node_ids
