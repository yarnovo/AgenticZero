"""
测试Schema验证器功能
"""

import pytest

from src.graph.schema import GraphConfigValidator, validate_graph_config


class TestGraphConfigValidator:
    """Schema验证器测试"""

    def setup_method(self):
        """设置测试"""
        self.validator = GraphConfigValidator()

    @pytest.mark.unit
    def test_valid_basic_config(self):
        """测试有效的基础配置"""
        config = {
            "name": "test_graph",
            "description": "测试图",
            "nodes": [
                {"id": "start", "type": "SequenceControlNode", "name": "开始节点"},
                {"id": "end", "type": "TaskNode", "name": "结束节点"},
            ],
            "edges": [{"from": "start", "to": "end"}],
            "start_node": "start",
            "end_nodes": ["end"],
        }

        valid, errors = self.validator.validate(config)
        assert valid, f"配置应该有效，但得到错误: {errors}"
        assert len(errors) == 0

    @pytest.mark.unit
    def test_valid_inline_config(self):
        """测试有效的内联节点配置"""
        config = {
            "name": "test_inline",
            "start_node": "input",
            "end_nodes": ["output"],
            "input": {
                "type": "SequenceControlNode",
                "name": "输入节点",
                "params": {"process_func": "lambda x: x * 2"},
            },
            "output": {"type": "TaskNode", "name": "输出节点"},
            "edges": [{"from": "input", "to": "output"}],
        }

        valid, errors = self.validator.validate(config)
        assert valid, f"配置应该有效，但得到错误: {errors}"

    @pytest.mark.unit
    def test_missing_required_fields(self):
        """测试缺少必需字段"""
        config = {
            "description": "测试图"
            # 缺少name, start_node, end_nodes
        }

        valid, errors = self.validator.validate(config)
        assert not valid
        assert len(errors) > 0

        # 检查是否包含必需字段的错误
        error_text = " ".join(errors)
        assert "name" in error_text
        assert "start_node" in error_text
        assert "end_nodes" in error_text

    @pytest.mark.unit
    def test_invalid_node_type(self):
        """测试无效的节点类型"""
        config = {
            "name": "test_graph",
            "nodes": [
                {
                    "id": "invalid",
                    "type": "InvalidNodeType",  # 无效类型
                    "name": "无效节点",
                }
            ],
            "start_node": "invalid",
            "end_nodes": ["invalid"],
            "edges": [],
        }

        valid, errors = self.validator.validate(config)
        assert not valid
        assert any("InvalidNodeType" in error for error in errors)

    @pytest.mark.unit
    def test_node_reference_validation(self):
        """测试节点引用验证"""
        config = {
            "name": "test_graph",
            "nodes": [{"id": "existing", "type": "TaskNode", "name": "存在的节点"}],
            "edges": [
                {
                    "from": "existing",
                    "to": "nonexistent",  # 不存在的节点
                }
            ],
            "start_node": "nonexistent_start",  # 不存在的起始节点
            "end_nodes": ["nonexistent_end"],  # 不存在的结束节点
        }

        valid, errors = self.validator.validate(config)
        assert not valid
        assert len(errors) >= 3  # 至少3个引用错误

        error_text = " ".join(errors)
        assert "nonexistent" in error_text
        assert "nonexistent_start" in error_text
        assert "nonexistent_end" in error_text

    @pytest.mark.unit
    def test_duplicate_node_ids(self):
        """测试重复节点ID"""
        config = {
            "name": "test_graph",
            "nodes": [
                {"id": "duplicate", "type": "TaskNode", "name": "节点1"},
                {
                    "id": "duplicate",  # 重复ID
                    "type": "TaskNode",
                    "name": "节点2",
                },
            ],
            "start_node": "duplicate",
            "end_nodes": ["duplicate"],
            "edges": [],
        }

        valid, errors = self.validator.validate(config)
        assert not valid
        assert any("重复" in error for error in errors)

    @pytest.mark.unit
    def test_connectivity_validation(self):
        """测试连通性验证"""
        config = {
            "name": "test_graph",
            "nodes": [
                {"id": "start", "type": "TaskNode", "name": "起始节点"},
                {"id": "isolated", "type": "TaskNode", "name": "孤立节点"},
                {"id": "unreachable_end", "type": "TaskNode", "name": "不可达结束节点"},
            ],
            "edges": [],  # 没有边连接
            "start_node": "start",
            "end_nodes": ["unreachable_end"],
        }

        valid, errors = self.validator.validate(config)
        assert not valid
        assert any("无法到达" in error for error in errors)

    @pytest.mark.unit
    def test_branch_node_parameters(self):
        """测试分支节点参数验证"""
        config = {
            "name": "test_branch",
            "nodes": [
                {
                    "id": "branch",
                    "type": "BranchControlNode",
                    "name": "分支节点",
                    # 缺少condition_func参数
                }
            ],
            "start_node": "branch",
            "end_nodes": ["branch"],
            "edges": [],
        }

        valid, errors = self.validator.validate(config)
        assert not valid
        assert any("condition_func" in error for error in errors)

    @pytest.mark.unit
    def test_retry_node_parameters(self):
        """测试重试节点参数验证"""
        config = {
            "name": "test_retry",
            "nodes": [
                {
                    "id": "retry",
                    "type": "RetryNode",
                    "name": "重试节点",
                    "params": {
                        "max_retries": -1,  # 无效值
                        "retry_delay": -0.5,  # 无效值
                    },
                }
            ],
            "start_node": "retry",
            "end_nodes": ["retry"],
            "edges": [],
        }

        valid, errors = self.validator.validate(config)
        assert not valid

        error_text = " ".join(errors)
        assert "max_retries" in error_text
        assert "retry_delay" in error_text

    @pytest.mark.unit
    def test_ai_router_parameters(self):
        """测试AI路由节点参数验证"""
        config = {
            "name": "test_ai_router",
            "nodes": [
                {
                    "id": "router",
                    "type": "AIRouter",
                    "name": "AI路由",
                    "params": {
                        "routes": ["single_route"]  # 路由数量不足
                    },
                }
            ],
            "start_node": "router",
            "end_nodes": ["router"],
            "edges": [],
        }

        valid, errors = self.validator.validate(config)
        assert not valid
        assert any("routes" in error and "至少2个" in error for error in errors)

    @pytest.mark.unit
    def test_string_length_validation(self):
        """测试字符串长度验证"""
        config = {
            "name": "",  # 空名称
            "description": "x" * 600,  # 超长描述
            "nodes": [
                {
                    "id": "a" * 100,  # 超长ID
                    "type": "TaskNode",
                    "name": "x" * 200,  # 超长名称
                }
            ],
            "start_node": "a" * 100,
            "end_nodes": ["a" * 100],
            "edges": [],
        }

        valid, errors = self.validator.validate(config)
        assert not valid

        error_text = " ".join(errors)
        assert "长度" in error_text or "超" in error_text

    @pytest.mark.unit
    def test_version_pattern_validation(self):
        """测试版本格式验证"""
        config = {
            "name": "test_graph",
            "version": "invalid_version",  # 无效版本格式
            "nodes": [{"id": "node1", "type": "TaskNode", "name": "节点1"}],
            "start_node": "node1",
            "end_nodes": ["node1"],
            "edges": [],
        }

        valid, errors = self.validator.validate(config)
        assert not valid
        assert any("version" in error or "格式" in error for error in errors)

    @pytest.mark.unit
    def test_valid_version_patterns(self):
        """测试有效的版本格式"""
        valid_versions = ["1.0", "2.1.3", "10.20.30"]

        base_config = {
            "name": "test_graph",
            "nodes": [{"id": "node1", "type": "TaskNode", "name": "节点1"}],
            "start_node": "node1",
            "end_nodes": ["node1"],
            "edges": [],
        }

        for version in valid_versions:
            config = base_config.copy()
            config["version"] = version

            valid, errors = self.validator.validate(config)
            assert valid, f"版本 {version} 应该有效，但得到错误: {errors}"


@pytest.mark.unit
def test_convenience_function():
    """测试便捷函数"""
    config = {
        "name": "test_graph",
        "nodes": [{"id": "node1", "type": "TaskNode", "name": "节点1"}],
        "start_node": "node1",
        "end_nodes": ["node1"],
        "edges": [],
    }

    valid, errors = validate_graph_config(config)
    assert valid
    assert len(errors) == 0
