"""
测试图配置代理对象功能
"""

import os
import tempfile

import pytest

from src.graph.config_proxy import GraphConfigProxy


class TestGraphConfigProxy:
    """图配置代理测试"""

    @pytest.mark.unit
    def test_create_empty_graph(self):
        """测试创建空图"""
        proxy = GraphConfigProxy.create_empty("test_graph", "测试图")

        assert proxy.name == "test_graph"
        assert proxy.description == "测试图"
        assert proxy.start_node == ""
        assert len(proxy.end_nodes) == 0
        assert len(proxy.get_node_ids()) == 0
        assert len(proxy.list_edges()) == 0

    @pytest.mark.unit
    def test_basic_properties(self):
        """测试基础属性操作"""
        proxy = GraphConfigProxy.create_empty("test")

        # 测试名称
        proxy.name = "新名称"
        assert proxy.name == "新名称"

        # 测试描述
        proxy.description = "新描述"
        assert proxy.description == "新描述"

        # 测试元数据
        proxy.set_metadata("author", "测试者")
        proxy.set_metadata("version", "1.0")

        assert proxy.get_metadata("author") == "测试者"
        assert proxy.get_metadata("version") == "1.0"
        assert proxy.get_metadata("nonexistent", "default") == "default"

        metadata = proxy.metadata
        assert metadata["author"] == "测试者"
        assert metadata["version"] == "1.0"

    @pytest.mark.unit
    def test_add_remove_nodes(self):
        """测试节点添加和删除"""
        proxy = GraphConfigProxy.create_empty("test")

        # 添加节点
        success = proxy.add_node(
            "node1",
            "TaskNode",
            "任务节点1",
            "第一个任务节点",
            {"param1": "value1"},
            {"meta1": "metavalue1"},
        )
        assert success
        assert proxy.has_node("node1")

        # 获取节点
        node = proxy.get_node("node1")
        assert node is not None
        assert node["id"] == "node1"
        assert node["type"] == "TaskNode"
        assert node["name"] == "任务节点1"
        assert node["description"] == "第一个任务节点"
        assert node["params"]["param1"] == "value1"
        assert node["metadata"]["meta1"] == "metavalue1"

        # 测试重复添加
        with pytest.raises(ValueError, match="已存在"):
            proxy.add_node("node1", "TaskNode", "重复节点")

        # 删除节点
        success = proxy.remove_node("node1")
        assert success
        assert not proxy.has_node("node1")

        # 删除不存在的节点
        success = proxy.remove_node("nonexistent")
        assert not success

    @pytest.mark.unit
    def test_update_node(self):
        """测试节点更新"""
        proxy = GraphConfigProxy.create_empty("test")

        # 添加节点
        proxy.add_node("node1", "TaskNode", "原名称", "原描述")

        # 更新节点
        success = proxy.update_node(
            "node1",
            name="新名称",
            description="新描述",
            params={"new_param": "new_value"},
            metadata={"new_meta": "meta_value"},
        )
        assert success

        # 验证更新
        node = proxy.get_node("node1")
        assert node["name"] == "新名称"
        assert node["description"] == "新描述"
        assert node["params"]["new_param"] == "new_value"
        assert node["metadata"]["new_meta"] == "meta_value"

        # 更新不存在的节点
        success = proxy.update_node("nonexistent", name="新名称")
        assert not success

    @pytest.mark.unit
    def test_node_listing_and_filtering(self):
        """测试节点列表和过滤"""
        proxy = GraphConfigProxy.create_empty("test")

        # 添加不同类型的节点
        proxy.add_node("task1", "TaskNode", "任务1")
        proxy.add_node("task2", "TaskNode", "任务2")
        proxy.add_node("control1", "SequenceControlNode", "控制1")

        # 测试列表功能
        all_nodes = proxy.list_nodes()
        assert len(all_nodes) == 3

        node_ids = proxy.get_node_ids()
        assert set(node_ids) == {"task1", "task2", "control1"}

        # 测试过滤
        task_nodes = proxy.filter_nodes("TaskNode")
        assert len(task_nodes) == 2
        assert all(node["type"] == "TaskNode" for node in task_nodes)

        control_nodes = proxy.filter_nodes("SequenceControlNode")
        assert len(control_nodes) == 1
        assert control_nodes[0]["id"] == "control1"

    @pytest.mark.unit
    def test_add_remove_edges(self):
        """测试边的添加和删除"""
        proxy = GraphConfigProxy.create_empty("test")

        # 添加节点
        proxy.add_node("node1", "TaskNode", "节点1")
        proxy.add_node("node2", "TaskNode", "节点2")

        # 添加边
        success = proxy.add_edge(
            "node1", "node2", "default", 1.5, {"edge_meta": "value"}
        )
        assert success
        assert proxy.has_edge("node1", "node2", "default")

        # 获取边
        edge = proxy.get_edge("node1", "node2", "default")
        assert edge is not None
        assert edge["from"] == "node1"
        assert edge["to"] == "node2"
        assert edge["action"] == "default"
        assert edge["weight"] == 1.5
        assert edge["metadata"]["edge_meta"] == "value"

        # 测试重复添加
        success = proxy.add_edge("node1", "node2", "default")
        assert not success  # 已存在

        # 添加不同动作的边
        success = proxy.add_edge("node1", "node2", "custom")
        assert success
        assert proxy.has_edge("node1", "node2", "custom")

        # 删除边
        success = proxy.remove_edge("node1", "node2", "default")
        assert success
        assert not proxy.has_edge("node1", "node2", "default")
        assert proxy.has_edge("node1", "node2", "custom")  # 其他边保留

        # 删除不存在的边
        success = proxy.remove_edge("node1", "node2", "nonexistent")
        assert not success

    @pytest.mark.unit
    def test_edge_validation(self):
        """测试边的验证"""
        proxy = GraphConfigProxy.create_empty("test")
        proxy.add_node("existing", "TaskNode", "存在的节点")

        # 测试源节点不存在
        with pytest.raises(ValueError, match="源节点.*不存在"):
            proxy.add_edge("nonexistent", "existing")

        # 测试目标节点不存在
        with pytest.raises(ValueError, match="目标节点.*不存在"):
            proxy.add_edge("existing", "nonexistent")

    @pytest.mark.unit
    def test_node_edges(self):
        """测试获取节点的边"""
        proxy = GraphConfigProxy.create_empty("test")

        # 添加节点
        proxy.add_node("center", "TaskNode", "中心节点")
        proxy.add_node("input", "TaskNode", "输入节点")
        proxy.add_node("output", "TaskNode", "输出节点")

        # 添加边
        proxy.add_edge("input", "center")
        proxy.add_edge("center", "output")

        # 获取中心节点的边
        edges = proxy.get_node_edges("center")

        assert len(edges["incoming"]) == 1
        assert edges["incoming"][0]["from"] == "input"

        assert len(edges["outgoing"]) == 1
        assert edges["outgoing"][0]["to"] == "output"

    @pytest.mark.unit
    def test_start_end_nodes(self):
        """测试起始和结束节点"""
        proxy = GraphConfigProxy.create_empty("test")

        # 添加节点
        proxy.add_node("start", "TaskNode", "起始节点")
        proxy.add_node("end1", "TaskNode", "结束节点1")
        proxy.add_node("end2", "TaskNode", "结束节点2")

        # 设置起始节点
        proxy.start_node = "start"
        assert proxy.start_node == "start"

        # 测试设置不存在的起始节点
        with pytest.raises(ValueError, match="不存在"):
            proxy.start_node = "nonexistent"

        # 添加结束节点
        success = proxy.add_end_node("end1")
        assert success
        assert proxy.is_end_node("end1")
        assert "end1" in proxy.end_nodes

        success = proxy.add_end_node("end2")
        assert success
        assert len(proxy.end_nodes) == 2

        # 测试添加不存在的结束节点
        with pytest.raises(ValueError, match="不存在"):
            proxy.add_end_node("nonexistent")

        # 删除结束节点
        success = proxy.remove_end_node("end1")
        assert success
        assert not proxy.is_end_node("end1")
        assert "end1" not in proxy.end_nodes

        # 删除不存在的结束节点
        success = proxy.remove_end_node("nonexistent")
        assert not success

    @pytest.mark.unit
    def test_validation(self):
        """测试验证功能"""
        proxy = GraphConfigProxy.create_empty("test")

        # 空图无效（没有节点）
        assert not proxy.is_valid()
        errors = proxy.get_validation_errors()
        assert len(errors) > 0

        # 添加基本结构
        proxy.add_node("start", "TaskNode", "起始节点")
        proxy.add_node("end", "TaskNode", "结束节点")
        proxy.add_edge("start", "end")
        proxy.start_node = "start"
        proxy.add_end_node("end")

        # 现在应该有效
        valid, errors = proxy.validate()
        assert valid, f"配置应该有效，但得到错误: {errors}"
        assert proxy.is_valid()

    @pytest.mark.unit
    def test_serialization(self):
        """测试序列化"""
        proxy = GraphConfigProxy.create_empty("test_graph")
        proxy.description = "测试图"

        # 添加内容
        proxy.add_node("node1", "TaskNode", "节点1")
        proxy.add_node("node2", "TaskNode", "节点2")
        proxy.add_edge("node1", "node2")
        proxy.start_node = "node1"
        proxy.add_end_node("node2")
        proxy.set_metadata("author", "测试者")

        # 导出为字典
        config_dict = proxy.to_dict()
        assert config_dict["name"] == "test_graph"
        assert config_dict["description"] == "测试图"
        assert len(config_dict["nodes"]) == 2
        assert len(config_dict["edges"]) == 1
        assert config_dict["metadata"]["author"] == "测试者"

        # 导出为YAML
        yaml_str = proxy.to_yaml()
        assert "test_graph" in yaml_str
        assert "节点1" in yaml_str

        # 从字典重新创建
        new_proxy = GraphConfigProxy.from_dict(config_dict)
        assert new_proxy.name == proxy.name
        assert new_proxy.description == proxy.description
        assert len(new_proxy.get_node_ids()) == len(proxy.get_node_ids())

    @pytest.mark.unit
    def test_file_operations(self):
        """测试文件操作"""
        proxy = GraphConfigProxy.create_empty("test_graph")

        # 添加有效配置
        proxy.add_node("start", "TaskNode", "起始节点")
        proxy.add_node("end", "TaskNode", "结束节点")
        proxy.add_edge("start", "end")
        proxy.start_node = "start"
        proxy.add_end_node("end")

        # 保存到临时文件
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            temp_file = f.name

        try:
            proxy.save_to_file(temp_file)

            # 从文件加载
            loaded_proxy = GraphConfigProxy.from_file(temp_file)

            assert loaded_proxy.name == proxy.name
            assert len(loaded_proxy.get_node_ids()) == len(proxy.get_node_ids())
            assert loaded_proxy.start_node == proxy.start_node

        finally:
            os.unlink(temp_file)

    @pytest.mark.unit
    def test_invalid_save(self):
        """测试保存无效配置"""
        proxy = GraphConfigProxy.create_empty("test")
        # 不添加任何内容，保持无效状态

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            temp_file = f.name

        try:
            with pytest.raises(ValueError, match="配置无效"):
                proxy.save_to_file(temp_file)
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    @pytest.mark.unit
    def test_clone(self):
        """测试克隆"""
        proxy = GraphConfigProxy.create_empty("original")
        proxy.add_node("node1", "TaskNode", "节点1")
        proxy.set_metadata("key", "value")

        # 克隆
        cloned = proxy.clone()

        # 验证克隆独立性
        assert cloned.name == proxy.name
        assert len(cloned.get_node_ids()) == len(proxy.get_node_ids())
        assert cloned.get_metadata("key") == proxy.get_metadata("key")

        # 修改原对象不影响克隆
        proxy.name = "modified"
        assert cloned.name == "original"

    @pytest.mark.unit
    def test_merge_configs(self):
        """测试配置合并"""
        proxy1 = GraphConfigProxy.create_empty("graph1")
        proxy1.add_node("node1", "TaskNode", "节点1")
        proxy1.add_node("node2", "TaskNode", "节点2")
        proxy1.add_edge("node1", "node2")

        proxy2 = GraphConfigProxy.create_empty("graph2")
        proxy2.add_node("node3", "TaskNode", "节点3")
        proxy2.add_node("node4", "TaskNode", "节点4")
        proxy2.add_edge("node3", "node4")

        # 合并（无冲突）
        merged = proxy1.merge(proxy2, "error")

        assert len(merged.get_node_ids()) == 4
        assert len(merged.list_edges()) == 2
        assert merged.has_node("node1")
        assert merged.has_node("node3")

    @pytest.mark.unit
    def test_merge_conflict_error(self):
        """测试合并冲突（错误策略）"""
        proxy1 = GraphConfigProxy.create_empty("graph1")
        proxy1.add_node("conflict", "TaskNode", "节点1")

        proxy2 = GraphConfigProxy.create_empty("graph2")
        proxy2.add_node("conflict", "TaskNode", "节点2")  # 冲突节点

        # 应该抛出错误
        with pytest.raises(ValueError, match="节点冲突"):
            proxy1.merge(proxy2, "error")

    @pytest.mark.unit
    def test_merge_conflict_strategies(self):
        """测试合并冲突处理策略"""
        proxy1 = GraphConfigProxy.create_empty("graph1")
        proxy1.add_node("conflict", "TaskNode", "原节点")

        proxy2 = GraphConfigProxy.create_empty("graph2")
        proxy2.add_node("conflict", "SequenceControlNode", "新节点")

        # keep策略：保留原节点
        merged_keep = proxy1.merge(proxy2, "keep")
        node = merged_keep.get_node("conflict")
        assert node["type"] == "TaskNode"  # 保留原类型
        assert node["name"] == "原节点"

        # override策略：覆盖为新节点
        merged_override = proxy1.merge(proxy2, "override")
        node = merged_override.get_node("conflict")
        assert node["type"] == "SequenceControlNode"  # 新类型
        assert node["name"] == "新节点"

    @pytest.mark.unit
    def test_statistics(self):
        """测试统计信息"""
        proxy = GraphConfigProxy.create_empty("test")

        # 添加各种节点
        proxy.add_node("task1", "TaskNode", "任务1")
        proxy.add_node("task2", "TaskNode", "任务2")
        proxy.add_node("control1", "SequenceControlNode", "控制1")
        proxy.add_node("isolated", "TaskNode", "孤立节点")

        # 添加边
        proxy.add_edge("task1", "control1")
        proxy.add_edge("control1", "task2")

        # 设置起始和结束节点
        proxy.start_node = "task1"
        proxy.add_end_node("task2")

        stats = proxy.get_statistics()

        assert stats["node_count"] == 4
        assert stats["edge_count"] == 2
        assert stats["node_types"]["TaskNode"] == 3
        assert stats["node_types"]["SequenceControlNode"] == 1
        assert stats["has_start_node"]
        assert stats["end_node_count"] == 1
        assert stats["max_in_degree"] == 1
        assert stats["max_out_degree"] == 1
        assert "isolated" in stats["isolated_nodes"]

    @pytest.mark.unit
    def test_string_representation(self):
        """测试字符串表示"""
        proxy = GraphConfigProxy.create_empty("test_graph")
        proxy.add_node("node1", "TaskNode", "节点1")

        str_repr = str(proxy)
        assert "test_graph" in str_repr
        assert "nodes=1" in str_repr
        assert "edges=0" in str_repr
        assert "valid=" in str_repr

    @pytest.mark.unit
    def test_node_parameter_validation(self):
        """测试节点参数验证"""
        proxy = GraphConfigProxy.create_empty("test")

        # 测试分支节点参数验证
        with pytest.raises(ValueError, match="condition_func"):
            proxy.add_node("branch", "BranchControlNode", "分支节点", params={})

        # 测试重试节点参数验证
        with pytest.raises(ValueError, match="max_retries"):
            proxy.add_node("retry", "RetryNode", "重试节点", params={"max_retries": -1})

    @pytest.mark.unit
    def test_remove_node_cleanup(self):
        """测试删除节点时的清理"""
        proxy = GraphConfigProxy.create_empty("test")

        # 创建图结构
        proxy.add_node("start", "TaskNode", "起始节点")
        proxy.add_node("middle", "TaskNode", "中间节点")
        proxy.add_node("end", "TaskNode", "结束节点")

        proxy.add_edge("start", "middle")
        proxy.add_edge("middle", "end")

        proxy.start_node = "start"
        proxy.add_end_node("middle")
        proxy.add_end_node("end")

        # 删除中间节点
        proxy.remove_node("middle")

        # 验证清理
        assert not proxy.has_node("middle")
        assert not proxy.has_edge("start", "middle")
        assert not proxy.has_edge("middle", "end")
        assert "middle" not in proxy.end_nodes

        # 起始节点未受影响
        assert proxy.start_node == "start"

    @pytest.mark.unit
    def test_update_edge(self):
        """测试边更新"""
        proxy = GraphConfigProxy.create_empty("test")

        proxy.add_node("node1", "TaskNode", "节点1")
        proxy.add_node("node2", "TaskNode", "节点2")
        proxy.add_edge("node1", "node2", "default", 1.0, {"old": "value"})

        # 更新边
        success = proxy.update_edge(
            "node1", "node2", "default", new_weight=2.0, new_metadata={"new": "value"}
        )
        assert success

        edge = proxy.get_edge("node1", "node2", "default")
        assert edge["weight"] == 2.0
        assert edge["metadata"]["new"] == "value"
        assert "old" not in edge["metadata"]

        # 更新不存在的边
        success = proxy.update_edge("node1", "node2", "nonexistent")
        assert not success
