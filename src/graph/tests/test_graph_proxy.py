"""
图代理测试
"""

import pytest

from src.graph import GraphProxy, TaskNode


@pytest.mark.unit
class TestGraphProxy:
    """图代理测试"""

    def test_create_proxy(self):
        """测试创建图代理"""
        proxy = GraphProxy.create("测试工作流", "测试描述")
        assert proxy.name == "测试工作流"
        assert proxy._description == "测试描述"

    def test_add_node(self):
        """测试添加节点"""
        proxy = GraphProxy.create("测试")

        # 使用字符串类型添加
        assert proxy.add_node("task1", "TaskNode", "任务1")
        assert proxy.has_node("task1")

        # 使用类添加
        assert proxy.add_node("task2", TaskNode, "任务2")
        assert proxy.has_node("task2")

    def test_remove_node(self):
        """测试删除节点"""
        proxy = GraphProxy.create("测试")
        proxy.add_node("task1", "TaskNode")
        proxy.add_node("task2", "TaskNode")
        proxy.add_edge("task1", "task2")

        assert proxy.remove_node("task2")
        assert not proxy.has_node("task2")
        # 边也应该被删除
        assert not proxy.has_edge("task1", "task2")

    def test_update_node(self):
        """测试更新节点"""
        proxy = GraphProxy.create("测试")
        proxy.add_node("task1", "TaskNode", "原名称")

        assert proxy.update_node("task1", name="新名称", priority="high")
        node = proxy.get_node("task1")
        assert node.name == "新名称"
        assert node.metadata.get("priority") == "high"

    def test_add_edge(self):
        """测试添加边"""
        proxy = GraphProxy.create("测试")
        proxy.add_node("task1", "TaskNode")
        proxy.add_node("task2", "TaskNode")

        assert proxy.add_edge("task1", "task2", weight=2.0)
        assert proxy.has_edge("task1", "task2")

        edge = proxy.get_edge("task1", "task2")
        assert edge.weight == 2.0

    def test_remove_edge(self):
        """测试删除边"""
        proxy = GraphProxy.create("测试")
        proxy.add_node("task1", "TaskNode")
        proxy.add_node("task2", "TaskNode")
        proxy.add_edge("task1", "task2")

        assert proxy.remove_edge("task1", "task2")
        assert not proxy.has_edge("task1", "task2")

    def test_start_end_nodes(self):
        """测试起始和结束节点"""
        proxy = GraphProxy.create("测试")
        proxy.add_node("start", "TaskNode")
        proxy.add_node("end", "TaskNode")

        assert proxy.set_start_node("start")
        assert proxy.start_node == "start"

        assert proxy.add_end_node("end")
        assert "end" in proxy.end_nodes

        assert proxy.remove_end_node("end")
        assert "end" not in proxy.end_nodes

    def test_graph_analysis(self):
        """测试图分析功能"""
        proxy = GraphProxy.create("测试")
        proxy.add_sequence(["n1", "n2", "n3", "n4"])

        # 测试邻居
        assert proxy.get_neighbors("n2") == ["n3"]
        assert proxy.get_predecessors("n3") == ["n2"]

        # 测试路径
        assert proxy.has_path("n1", "n4")
        paths = proxy.find_all_paths("n1", "n4")
        assert len(paths) == 1
        assert paths[0] == ["n1", "n2", "n3", "n4"]

    def test_validation(self):
        """测试验证功能"""
        proxy = GraphProxy.create("测试")

        # 空图应该无效
        assert not proxy.is_valid()

        # 添加完整的图结构
        proxy.add_node("start", "TaskNode")
        proxy.add_node("end", "TaskNode")
        proxy.add_edge("start", "end")
        proxy.set_start_node("start")
        proxy.add_end_node("end")

        assert proxy.is_valid()

    def test_serialization(self):
        """测试序列化"""
        proxy = GraphProxy.create("测试")
        proxy.add_node("task1", "TaskNode", "任务1")
        proxy.add_edge("task1", "task1")  # 自环

        # 导出为字典
        data = proxy.to_dict()
        assert data["name"] == "测试"
        assert "task1" in data["nodes"]

        # 从字典恢复
        proxy2 = GraphProxy.from_dict(data)
        assert proxy2.has_node("task1")
        assert proxy2.get_node("task1").name == "任务1"

    def test_batch_operations(self):
        """测试批量操作"""
        proxy = GraphProxy.create("测试")

        # 批量添加节点
        nodes = [
            ("n1", "TaskNode", "节点1", {}),
            ("n2", "TaskNode", "节点2", {"priority": "high"}),
            ("n3", "BranchControlNode", "分支", {"condition_func": lambda x: x > 10}),
        ]
        count = proxy.add_nodes_batch(nodes)
        assert count == 3

        # 批量添加边
        edges = [
            ("n1", "n2", "default", 1.0),
            ("n2", "n3", "default", 2.0),
        ]
        count = proxy.add_edges_batch(edges)
        assert count == 2

    def test_clone_and_merge(self):
        """测试克隆和合并"""
        proxy1 = GraphProxy.create("图1")
        proxy1.add_sequence(["a", "b", "c"])

        # 克隆
        proxy2 = proxy1.clone()
        assert proxy2.has_node("a")
        assert proxy2.has_edge("a", "b")

        # 合并
        proxy3 = GraphProxy.create("图3")
        proxy3.add_sequence(["x", "y", "z"])

        assert proxy1.merge(proxy3, prefix="p3_")
        assert proxy1.has_node("p3_x")
        assert proxy1.has_edge("p3_x", "p3_y")

    def test_statistics(self):
        """测试统计信息"""
        proxy = GraphProxy.create("测试")
        proxy.add_node("start", "TaskNode")
        proxy.add_node("branch", "BranchControlNode", condition_func=lambda x: x > 10)
        proxy.add_node("end1", "TaskNode")
        proxy.add_node("end2", "TaskNode")

        proxy.add_edge("start", "branch")
        proxy.add_edge("branch", "end1", "high")
        proxy.add_edge("branch", "end2", "low")

        proxy.set_start_node("start")
        proxy.add_end_node("end1")
        proxy.add_end_node("end2")

        stats = proxy.get_statistics()
        assert stats["node_count"] == 4
        assert stats["edge_count"] == 3
        assert stats["end_node_count"] == 2
        assert "TaskNode" in stats["node_types"]
        assert stats["node_types"]["TaskNode"] == 3

    def test_convenience_methods(self):
        """测试便捷方法"""
        proxy = GraphProxy.create("测试")

        # 添加序列
        assert proxy.add_sequence(["s1", "s2", "s3"])
        assert proxy.has_edge("s1", "s2")
        assert proxy.has_edge("s2", "s3")

        # 注册新节点类型
        class CustomNode(TaskNode):
            pass

        proxy.register_node_type("CustomNode", CustomNode)
        assert proxy.add_node("custom", "CustomNode")
        assert isinstance(proxy.get_node("custom"), CustomNode)
