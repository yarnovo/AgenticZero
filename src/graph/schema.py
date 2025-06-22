"""
图配置YAML的JSON Schema定义和验证器 - 版本2

支持两种配置格式：
1. 数组格式：nodes数组定义
2. 内联格式：直接节点定义
"""

from typing import Any

import jsonschema
from jsonschema import ValidationError


class GraphConfigSchema:
    """图配置Schema定义"""

    # 节点类型枚举
    NODE_TYPES = [
        # 基础节点类型
        "TaskNode",
        "ControlNode",
        "ExceptionNode",
        # 原子控制节点
        "SequenceControlNode",
        "BranchControlNode",
        "MergeControlNode",
        "ForkControlNode",
        "JoinControlNode",
        # 异常处理节点
        "TryCatchNode",
        "RetryNode",
        "TimeoutNode",
        "CircuitBreakerNode",
        # 复合控制节点
        "CompositeControlNode",
        # AI控制节点
        "AIRouter",
        "AIPlanner",
        # AI任务节点
        "AIAnalyzer",
        "AIGenerator",
        "AIEvaluator",
        # 兼容性别名
        "SequenceNode",
        "BranchNode",
        "MergeNode",
        "ForkNode",
        "JoinNode",
        "IntentRouterNode",
    ]

    @classmethod
    def get_array_format_schema(cls) -> dict[str, Any]:
        """获取数组格式的Schema（nodes数组）"""
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "title": "AgenticZero图配置Schema (数组格式)",
            "description": "使用nodes数组定义节点的配置格式",
            "required": ["name", "start_node", "end_nodes", "nodes"],
            "properties": {
                "name": {
                    "type": "string",
                    "description": "图的名称",
                    "minLength": 1,
                    "maxLength": 100,
                },
                "description": {
                    "type": "string",
                    "description": "图的描述信息",
                    "maxLength": 500,
                },
                "version": {
                    "type": "string",
                    "description": "配置版本",
                    "pattern": r"^\d+\.\d+(\.\d+)?$",
                },
                "nodes": {
                    "type": "array",
                    "description": "节点数组",
                    "items": cls._get_node_schema(),
                    "minItems": 1,
                },
                "edges": {
                    "type": "array",
                    "description": "边的定义",
                    "items": cls._get_edge_schema(),
                    "default": [],
                },
                "start_node": {
                    "type": "string",
                    "description": "起始节点ID",
                    "minLength": 1,
                },
                "end_nodes": {
                    "type": "array",
                    "description": "结束节点ID列表",
                    "items": {"type": "string", "minLength": 1},
                    "minItems": 1,
                    "uniqueItems": True,
                },
                "custom_nodes": {
                    "type": "object",
                    "description": "自定义节点类型定义",
                    "patternProperties": {
                        "^[a-zA-Z][a-zA-Z0-9_]*$": {
                            "type": "string",
                            "description": "模块路径",
                        }
                    },
                    "additionalProperties": False,
                },
                "metadata": {
                    "type": "object",
                    "description": "元数据信息",
                    "additionalProperties": True,
                },
            },
            "additionalProperties": False,
        }

    @classmethod
    def get_inline_format_schema(cls) -> dict[str, Any]:
        """获取内联格式的Schema（直接节点定义）"""
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "title": "AgenticZero图配置Schema (内联格式)",
            "description": "直接定义节点的配置格式",
            "required": ["name", "start_node", "end_nodes"],
            "properties": {
                "name": {
                    "type": "string",
                    "description": "图的名称",
                    "minLength": 1,
                    "maxLength": 100,
                },
                "description": {
                    "type": "string",
                    "description": "图的描述信息",
                    "maxLength": 500,
                },
                "version": {
                    "type": "string",
                    "description": "配置版本",
                    "pattern": r"^\d+\.\d+(\.\d+)?$",
                },
                "edges": {
                    "type": "array",
                    "description": "边的定义",
                    "items": cls._get_edge_schema(),
                    "default": [],
                },
                "start_node": {
                    "type": "string",
                    "description": "起始节点ID",
                    "minLength": 1,
                },
                "end_nodes": {
                    "type": "array",
                    "description": "结束节点ID列表",
                    "items": {"type": "string", "minLength": 1},
                    "minItems": 1,
                    "uniqueItems": True,
                },
                "custom_nodes": {
                    "type": "object",
                    "description": "自定义节点类型定义",
                    "patternProperties": {
                        "^[a-zA-Z][a-zA-Z0-9_]*$": {
                            "type": "string",
                            "description": "模块路径",
                        }
                    },
                    "additionalProperties": False,
                },
                "metadata": {
                    "type": "object",
                    "description": "元数据信息",
                    "additionalProperties": True,
                },
            },
            # 支持节点直接定义，但排除预定义字段
            "patternProperties": {
                "^(?!name$|description$|version$|edges$|start_node$|end_nodes$|custom_nodes$|metadata$)[a-zA-Z][a-zA-Z0-9_]*$": cls._get_inline_node_schema()
            },
            "additionalProperties": False,
        }

    @classmethod
    def _get_node_schema(cls) -> dict[str, Any]:
        """获取节点的Schema定义（数组方式）"""
        return {
            "type": "object",
            "required": ["id", "type", "name"],
            "properties": {
                "id": {
                    "type": "string",
                    "description": "节点唯一标识符",
                    "pattern": "^[a-zA-Z][a-zA-Z0-9_]*$",
                    "minLength": 1,
                    "maxLength": 50,
                },
                "type": {
                    "type": "string",
                    "description": "节点类型",
                    "enum": cls.NODE_TYPES,
                },
                "name": {
                    "type": "string",
                    "description": "节点显示名称",
                    "minLength": 1,
                    "maxLength": 100,
                },
                "description": {
                    "type": "string",
                    "description": "节点描述",
                    "maxLength": 200,
                },
                "params": {
                    "type": "object",
                    "description": "节点参数",
                    "additionalProperties": True,
                },
                "metadata": {
                    "type": "object",
                    "description": "节点元数据",
                    "additionalProperties": True,
                },
            },
            "additionalProperties": False,
        }

    @classmethod
    def _get_inline_node_schema(cls) -> dict[str, Any]:
        """获取内联节点的Schema定义"""
        return {
            "type": "object",
            "required": ["type", "name"],
            "properties": {
                "type": {
                    "type": "string",
                    "description": "节点类型",
                    "enum": cls.NODE_TYPES,
                },
                "name": {
                    "type": "string",
                    "description": "节点显示名称",
                    "minLength": 1,
                    "maxLength": 100,
                },
                "description": {
                    "type": "string",
                    "description": "节点描述",
                    "maxLength": 200,
                },
                "params": {
                    "type": "object",
                    "description": "节点参数",
                    "additionalProperties": True,
                },
                "metadata": {
                    "type": "object",
                    "description": "节点元数据",
                    "additionalProperties": True,
                },
            },
            "additionalProperties": False,
        }

    @classmethod
    def _get_edge_schema(cls) -> dict[str, Any]:
        """获取边的Schema定义"""
        return {
            "type": "object",
            "required": ["from", "to"],
            "properties": {
                "from": {"type": "string", "description": "源节点ID", "minLength": 1},
                "to": {"type": "string", "description": "目标节点ID", "minLength": 1},
                "action": {
                    "type": "string",
                    "description": "边的动作/条件",
                    "default": "default",
                },
                "condition": {
                    "type": "string",
                    "description": "边的条件（兼容性字段）",
                },
                "weight": {
                    "type": "number",
                    "description": "边的权重",
                    "default": 1.0,
                    "minimum": 0,
                },
                "metadata": {
                    "type": "object",
                    "description": "边的元数据",
                    "additionalProperties": True,
                },
            },
            "additionalProperties": False,
        }


class GraphConfigValidator:
    """图配置验证器"""

    def __init__(self):
        """初始化验证器"""
        self.array_schema = GraphConfigSchema.get_array_format_schema()
        self.inline_schema = GraphConfigSchema.get_inline_format_schema()
        self.array_validator = jsonschema.Draft7Validator(self.array_schema)
        self.inline_validator = jsonschema.Draft7Validator(self.inline_schema)

    def detect_format(self, config: dict[str, Any]) -> str:
        """检测配置格式"""
        if "nodes" in config and isinstance(config["nodes"], list):
            return "array"
        else:
            return "inline"

    def validate(self, config: dict[str, Any]) -> tuple[bool, list[str]]:
        """
        验证配置

        Args:
            config: 要验证的配置字典

        Returns:
            Tuple[bool, List[str]]: (是否有效, 错误信息列表)
        """
        errors = []

        # 检测格式并选择对应的验证器
        format_type = self.detect_format(config)

        if format_type == "array":
            validator = self.array_validator
        else:
            validator = self.inline_validator

        # 基础JSON Schema验证
        schema_errors = list(validator.iter_errors(config))
        for error in schema_errors:
            errors.append(self._format_schema_error(error))

        # 语义验证
        semantic_errors = self._validate_semantics(config)
        errors.extend(semantic_errors)

        return len(errors) == 0, errors

    def _format_schema_error(self, error: ValidationError) -> str:
        """格式化Schema验证错误"""
        path = (
            " -> ".join(str(p) for p in error.absolute_path)
            if error.absolute_path
            else "根级"
        )

        # 针对不同错误类型提供友好的错误信息
        if error.validator == "required":
            missing_props = ", ".join(f"'{prop}'" for prop in error.validator_value)
            return f"[{path}] 缺少必需字段: {missing_props}"

        elif error.validator == "type":
            expected_type = error.validator_value
            actual_value = error.instance
            return f"[{path}] 类型错误: 期望 {expected_type}，实际值为 {type(actual_value).__name__}: {actual_value}"

        elif error.validator == "enum":
            valid_values = ", ".join(f"'{v}'" for v in error.validator_value)
            return f"[{path}] 无效值 '{error.instance}'，有效值为: {valid_values}"

        elif error.validator == "minLength":
            return f"[{path}] 长度不足: '{error.instance}' 长度应至少为 {error.validator_value}"

        elif error.validator == "maxLength":
            return f"[{path}] 长度超限: '{error.instance}' 长度不应超过 {error.validator_value}"

        elif error.validator == "pattern":
            return f"[{path}] 格式错误: '{error.instance}' 不符合模式 {error.validator_value}"

        elif error.validator == "minimum":
            return (
                f"[{path}] 数值过小: {error.instance} 应不小于 {error.validator_value}"
            )

        elif error.validator == "uniqueItems":
            return f"[{path}] 包含重复项: {error.instance}"

        elif error.validator == "additionalProperties":
            return f"[{path}] 包含未知属性: {error.validator_value}"

        else:
            return f"[{path}] {error.message}"

    def _validate_semantics(self, config: dict[str, Any]) -> list[str]:
        """语义验证"""
        errors = []

        # 收集所有节点ID
        node_ids = self._collect_node_ids(config)

        # 验证起始节点存在
        start_node = config.get("start_node")
        if start_node and start_node not in node_ids:
            errors.append(f"起始节点 '{start_node}' 不存在")

        # 验证结束节点存在
        end_nodes = config.get("end_nodes", [])
        for end_node in end_nodes:
            if end_node not in node_ids:
                errors.append(f"结束节点 '{end_node}' 不存在")

        # 验证边的节点引用
        edges = config.get("edges", [])
        for i, edge in enumerate(edges):
            from_node = edge.get("from")
            to_node = edge.get("to")

            if from_node and from_node not in node_ids:
                errors.append(f"边 #{i + 1} 的源节点 '{from_node}' 不存在")

            if to_node and to_node not in node_ids:
                errors.append(f"边 #{i + 1} 的目标节点 '{to_node}' 不存在")

        # 验证节点ID唯一性
        node_id_counts = {}
        for node_id in node_ids:
            node_id_counts[node_id] = node_id_counts.get(node_id, 0) + 1

        for node_id, count in node_id_counts.items():
            if count > 1:
                errors.append(f"节点ID '{node_id}' 重复定义了 {count} 次")

        # 验证图连通性
        connectivity_errors = self._validate_connectivity(config, node_ids)
        errors.extend(connectivity_errors)

        # 验证节点类型特定的参数
        node_errors = self._validate_node_parameters(config)
        errors.extend(node_errors)

        return errors

    def _collect_node_ids(self, config: dict[str, Any]) -> list[str]:
        """收集所有节点ID"""
        node_ids = []

        # 从nodes数组收集
        nodes = config.get("nodes", [])
        for node in nodes:
            if "id" in node:
                node_ids.append(node["id"])

        # 从直接定义的节点收集
        reserved_keys = {
            "name",
            "description",
            "version",
            "nodes",
            "edges",
            "start_node",
            "end_nodes",
            "custom_nodes",
            "metadata",
        }

        for key, value in config.items():
            if key not in reserved_keys and isinstance(value, dict) and "type" in value:
                node_ids.append(key)

        return node_ids

    def _validate_connectivity(
        self, config: dict[str, Any], node_ids: list[str]
    ) -> list[str]:
        """验证图连通性"""
        errors = []

        if not node_ids:
            return ["图中没有定义任何节点"]

        start_node = config.get("start_node")
        end_nodes = config.get("end_nodes", [])
        edges = config.get("edges", [])

        if not start_node:
            return errors  # 基础验证已经处理

        # 构建邻接表
        graph = {node_id: [] for node_id in node_ids}
        for edge in edges:
            from_node = edge.get("from")
            to_node = edge.get("to")
            if from_node in graph and to_node in graph:
                graph[from_node].append(to_node)

        # 检查从起始节点是否能到达所有结束节点
        reachable = self._get_reachable_nodes(graph, start_node)

        for end_node in end_nodes:
            if end_node not in reachable:
                errors.append(
                    f"从起始节点 '{start_node}' 无法到达结束节点 '{end_node}'"
                )

        return errors

    def _get_reachable_nodes(self, graph: dict[str, list[str]], start: str) -> set[str]:
        """获取从起始节点可达的所有节点"""
        visited = set()
        stack = [start]

        while stack:
            node = stack.pop()
            if node not in visited:
                visited.add(node)
                stack.extend(graph.get(node, []))

        return visited

    def _validate_node_parameters(self, config: dict[str, Any]) -> list[str]:
        """验证节点类型特定的参数"""
        errors = []

        # 获取所有节点
        all_nodes = []

        # 从nodes数组获取
        nodes = config.get("nodes", [])
        for node in nodes:
            all_nodes.append((node.get("id", "unknown"), node))

        # 从直接定义获取
        reserved_keys = {
            "name",
            "description",
            "version",
            "nodes",
            "edges",
            "start_node",
            "end_nodes",
            "custom_nodes",
            "metadata",
        }

        for key, value in config.items():
            if key not in reserved_keys and isinstance(value, dict) and "type" in value:
                all_nodes.append((key, value))

        # 验证每个节点的参数
        for node_id, node_config in all_nodes:
            node_type = node_config.get("type")
            params = node_config.get("params", {})

            node_errors = self._validate_single_node_parameters(
                node_id, node_type, params
            )
            errors.extend(node_errors)

        return errors

    def _validate_single_node_parameters(
        self, node_id: str, node_type: str, params: dict[str, Any]
    ) -> list[str]:
        """验证单个节点的参数"""
        errors = []

        # BranchControlNode特定验证
        if node_type in ["BranchControlNode", "BranchNode"]:
            if "condition_func" not in params:
                errors.append(f"分支节点 '{node_id}' 缺少必需参数 'condition_func'")

        # ForkControlNode特定验证
        elif node_type in ["ForkControlNode", "ForkNode"]:
            if "fork_count" in params:
                fork_count = params["fork_count"]
                if not isinstance(fork_count, int) or fork_count < 2:
                    errors.append(
                        f"分叉节点 '{node_id}' 的 'fork_count' 必须是大于等于2的整数"
                    )

        # RetryNode特定验证
        elif node_type == "RetryNode":
            if "max_retries" in params:
                max_retries = params["max_retries"]
                if not isinstance(max_retries, int) or max_retries < 1:
                    errors.append(f"重试节点 '{node_id}' 的 'max_retries' 必须是正整数")

            if "retry_delay" in params:
                retry_delay = params["retry_delay"]
                if not isinstance(retry_delay, int | float) or retry_delay < 0:
                    errors.append(f"重试节点 '{node_id}' 的 'retry_delay' 必须是非负数")

        # TimeoutNode特定验证
        elif node_type == "TimeoutNode":
            if "timeout_seconds" in params:
                timeout_seconds = params["timeout_seconds"]
                if (
                    not isinstance(timeout_seconds, int | float)
                    or timeout_seconds <= 0
                ):
                    errors.append(
                        f"超时节点 '{node_id}' 的 'timeout_seconds' 必须是正数"
                    )

        # AIRouter特定验证
        elif node_type == "AIRouter":
            if "routes" not in params:
                errors.append(f"AI路由节点 '{node_id}' 缺少必需参数 'routes'")
            elif not isinstance(params["routes"], list) or len(params["routes"]) < 2:
                errors.append(
                    f"AI路由节点 '{node_id}' 的 'routes' 必须是包含至少2个元素的列表"
                )

        return errors


def validate_graph_config(config: dict[str, Any]) -> tuple[bool, list[str]]:
    """
    便捷函数：验证图配置

    Args:
        config: 配置字典

    Returns:
        Tuple[bool, List[str]]: (是否有效, 错误信息列表)
    """
    validator = GraphConfigValidator()
    return validator.validate(config)


def validate_graph_config_file(config_file: str) -> tuple[bool, list[str]]:
    """
    便捷函数：验证图配置文件

    Args:
        config_file: YAML配置文件路径

    Returns:
        Tuple[bool, List[str]]: (是否有效, 错误信息列表)
    """
    try:
        import yaml

        with open(config_file, encoding="utf-8") as f:
            config = yaml.safe_load(f)

        return validate_graph_config(config)

    except FileNotFoundError:
        return False, [f"配置文件不存在: {config_file}"]
    except yaml.YAMLError as e:
        return False, [f"YAML格式错误: {e}"]
    except Exception as e:
        return False, [f"验证失败: {e}"]
