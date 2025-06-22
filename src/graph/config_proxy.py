"""
图配置代理对象

提供操作图结构的高级API，内部维护图的内存表示，
支持增删节点和边，并实时验证配置的有效性。
"""

import copy
from typing import Any

import yaml

from .schema import GraphConfigValidator


class GraphConfigProxy:
    """
    图配置代理对象

    维护图的内存表示，提供操作API，确保配置始终有效。
    """

    def __init__(self, initial_config: dict[str, Any] | None = None):
        """
        初始化图配置代理

        Args:
            initial_config: 初始配置，如果为None则创建空图
        """
        self.validator = GraphConfigValidator()

        if initial_config:
            # 验证初始配置
            valid, errors = self.validator.validate(initial_config)
            if not valid:
                raise ValueError(f"初始配置无效: {'; '.join(errors)}")
            self._config = copy.deepcopy(initial_config)
        else:
            # 创建空图配置
            self._config = {
                "name": "unnamed_graph",
                "description": "",
                "nodes": [],
                "edges": [],
                "start_node": "",
                "end_nodes": [],
                "metadata": {},
            }

    @classmethod
    def from_file(cls, config_file: str) -> "GraphConfigProxy":
        """从YAML文件创建代理对象"""
        with open(config_file, encoding="utf-8") as f:
            config = yaml.safe_load(f)
        return cls(config)

    @classmethod
    def from_dict(cls, config: dict[str, Any]) -> "GraphConfigProxy":
        """从字典创建代理对象"""
        return cls(config)

    @classmethod
    def create_empty(cls, name: str, description: str = "") -> "GraphConfigProxy":
        """创建空图"""
        # 创建实例但跳过初始验证
        instance = cls.__new__(cls)
        instance.validator = GraphConfigValidator()
        instance._config = {
            "name": name,
            "description": description,
            "nodes": [],
            "edges": [],
            "start_node": "",
            "end_nodes": [],
            "metadata": {},
        }
        return instance

    # ========== 基础属性操作 ==========

    @property
    def name(self) -> str:
        """图名称"""
        return self._config.get("name", "")

    @name.setter
    def name(self, value: str):
        """设置图名称"""
        if not value or not isinstance(value, str):
            raise ValueError("图名称不能为空")
        self._config["name"] = value

    @property
    def description(self) -> str:
        """图描述"""
        return self._config.get("description", "")

    @description.setter
    def description(self, value: str):
        """设置图描述"""
        self._config["description"] = value or ""

    @property
    def start_node(self) -> str:
        """起始节点ID"""
        return self._config.get("start_node", "")

    @start_node.setter
    def start_node(self, node_id: str):
        """设置起始节点"""
        if node_id and not self.has_node(node_id):
            raise ValueError(f"起始节点 '{node_id}' 不存在")
        self._config["start_node"] = node_id

    @property
    def end_nodes(self) -> list[str]:
        """结束节点ID列表"""
        return self._config.get("end_nodes", []).copy()

    @property
    def metadata(self) -> dict[str, Any]:
        """元数据"""
        return self._config.get("metadata", {}).copy()

    def set_metadata(self, key: str, value: Any):
        """设置元数据"""
        if "metadata" not in self._config:
            self._config["metadata"] = {}
        self._config["metadata"][key] = value

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """获取元数据"""
        return self._config.get("metadata", {}).get(key, default)

    # ========== 节点操作 ==========

    def add_node(
        self,
        node_id: str,
        node_type: str,
        name: str,
        description: str = "",
        params: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """
        添加节点

        Args:
            node_id: 节点ID
            node_type: 节点类型
            name: 节点名称
            description: 节点描述
            params: 节点参数
            metadata: 节点元数据

        Returns:
            bool: 是否成功添加
        """
        if self.has_node(node_id):
            raise ValueError(f"节点 '{node_id}' 已存在")

        node_config = {"id": node_id, "type": node_type, "name": name}

        if description:
            node_config["description"] = description

        if params:
            node_config["params"] = params

        if metadata:
            node_config["metadata"] = metadata

        # 创建临时配置进行验证
        temp_config = copy.deepcopy(self._config)
        temp_config["nodes"].append(node_config)

        # 只验证节点本身，不验证整体连通性
        temp_validator = GraphConfigValidator()
        temp_errors = temp_validator._validate_single_node_parameters(
            node_id, node_type, params or {}
        )

        if temp_errors:
            raise ValueError(f"节点参数无效: {'; '.join(temp_errors)}")

        # 添加节点
        self._config["nodes"].append(node_config)
        return True

    def remove_node(self, node_id: str) -> bool:
        """
        删除节点

        Args:
            node_id: 节点ID

        Returns:
            bool: 是否成功删除
        """
        if not self.has_node(node_id):
            return False

        # 删除相关的边
        self._config["edges"] = [
            edge
            for edge in self._config["edges"]
            if edge.get("from") != node_id and edge.get("to") != node_id
        ]

        # 删除节点
        self._config["nodes"] = [
            node for node in self._config["nodes"] if node.get("id") != node_id
        ]

        # 更新起始节点
        if self._config.get("start_node") == node_id:
            self._config["start_node"] = ""

        # 更新结束节点
        if node_id in self._config.get("end_nodes", []):
            self._config["end_nodes"].remove(node_id)

        return True

    def update_node(
        self,
        node_id: str,
        name: str | None = None,
        description: str | None = None,
        params: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """
        更新节点

        Args:
            node_id: 节点ID
            name: 新名称
            description: 新描述
            params: 新参数
            metadata: 新元数据

        Returns:
            bool: 是否成功更新
        """
        node = self.get_node(node_id)
        if not node:
            return False

        # 更新字段
        if name is not None:
            node["name"] = name

        if description is not None:
            if description:
                node["description"] = description
            elif "description" in node:
                del node["description"]

        if params is not None:
            if params:
                node["params"] = params
            elif "params" in node:
                del node["params"]

            # 验证新参数
            temp_errors = self.validator._validate_single_node_parameters(
                node_id, node.get("type", ""), params or {}
            )
            if temp_errors:
                raise ValueError(f"节点参数无效: {'; '.join(temp_errors)}")

        if metadata is not None:
            if metadata:
                node["metadata"] = metadata
            elif "metadata" in node:
                del node["metadata"]

        return True

    def get_node(self, node_id: str) -> dict[str, Any] | None:
        """获取节点配置"""
        for node in self._config.get("nodes", []):
            if node.get("id") == node_id:
                return node
        return None

    def has_node(self, node_id: str) -> bool:
        """检查节点是否存在"""
        return self.get_node(node_id) is not None

    def list_nodes(self) -> list[dict[str, Any]]:
        """列出所有节点"""
        return copy.deepcopy(self._config.get("nodes", []))

    def get_node_ids(self) -> list[str]:
        """获取所有节点ID"""
        return [node.get("id", "") for node in self._config.get("nodes", [])]

    def filter_nodes(self, node_type: str | None = None) -> list[dict[str, Any]]:
        """按类型过滤节点"""
        nodes = self._config.get("nodes", [])
        if node_type:
            nodes = [node for node in nodes if node.get("type") == node_type]
        return copy.deepcopy(nodes)

    # ========== 边操作 ==========

    def add_edge(
        self,
        from_node: str,
        to_node: str,
        action: str = "default",
        weight: float = 1.0,
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """
        添加边

        Args:
            from_node: 源节点ID
            to_node: 目标节点ID
            action: 边的动作/条件
            weight: 边的权重
            metadata: 边的元数据

        Returns:
            bool: 是否成功添加
        """
        # 检查节点存在
        if not self.has_node(from_node):
            raise ValueError(f"源节点 '{from_node}' 不存在")

        if not self.has_node(to_node):
            raise ValueError(f"目标节点 '{to_node}' 不存在")

        # 检查边是否已存在
        if self.has_edge(from_node, to_node, action):
            return False

        edge_config = {
            "from": from_node,
            "to": to_node,
            "action": action,
            "weight": weight,
        }

        if metadata:
            edge_config["metadata"] = metadata

        self._config["edges"].append(edge_config)
        return True

    def remove_edge(
        self, from_node: str, to_node: str, action: str = "default"
    ) -> bool:
        """
        删除边

        Args:
            from_node: 源节点ID
            to_node: 目标节点ID
            action: 边的动作

        Returns:
            bool: 是否成功删除
        """
        original_count = len(self._config["edges"])

        self._config["edges"] = [
            edge
            for edge in self._config["edges"]
            if not (
                edge.get("from") == from_node
                and edge.get("to") == to_node
                and edge.get("action", "default") == action
            )
        ]

        return len(self._config["edges"]) < original_count

    def update_edge(
        self,
        from_node: str,
        to_node: str,
        action: str = "default",
        new_weight: float | None = None,
        new_metadata: dict[str, Any] | None = None,
    ) -> bool:
        """
        更新边

        Args:
            from_node: 源节点ID
            to_node: 目标节点ID
            action: 边的动作
            new_weight: 新权重
            new_metadata: 新元数据

        Returns:
            bool: 是否成功更新
        """
        edge = self.get_edge(from_node, to_node, action)
        if not edge:
            return False

        if new_weight is not None:
            edge["weight"] = new_weight

        if new_metadata is not None:
            if new_metadata:
                edge["metadata"] = new_metadata
            elif "metadata" in edge:
                del edge["metadata"]

        return True

    def get_edge(
        self, from_node: str, to_node: str, action: str = "default"
    ) -> dict[str, Any] | None:
        """获取边配置"""
        for edge in self._config.get("edges", []):
            if (
                edge.get("from") == from_node
                and edge.get("to") == to_node
                and edge.get("action", "default") == action
            ):
                return edge
        return None

    def has_edge(self, from_node: str, to_node: str, action: str = "default") -> bool:
        """检查边是否存在"""
        return self.get_edge(from_node, to_node, action) is not None

    def list_edges(self) -> list[dict[str, Any]]:
        """列出所有边"""
        return copy.deepcopy(self._config.get("edges", []))

    def get_node_edges(self, node_id: str) -> dict[str, list[dict[str, Any]]]:
        """获取节点的所有边"""
        incoming = []
        outgoing = []

        for edge in self._config.get("edges", []):
            if edge.get("to") == node_id:
                incoming.append(copy.deepcopy(edge))
            if edge.get("from") == node_id:
                outgoing.append(copy.deepcopy(edge))

        return {"incoming": incoming, "outgoing": outgoing}

    # ========== 结束节点操作 ==========

    def add_end_node(self, node_id: str) -> bool:
        """添加结束节点"""
        if not self.has_node(node_id):
            raise ValueError(f"节点 '{node_id}' 不存在")

        if node_id not in self._config.get("end_nodes", []):
            if "end_nodes" not in self._config:
                self._config["end_nodes"] = []
            self._config["end_nodes"].append(node_id)
            return True
        return False

    def remove_end_node(self, node_id: str) -> bool:
        """删除结束节点"""
        end_nodes = self._config.get("end_nodes", [])
        if node_id in end_nodes:
            end_nodes.remove(node_id)
            return True
        return False

    def is_end_node(self, node_id: str) -> bool:
        """检查是否为结束节点"""
        return node_id in self._config.get("end_nodes", [])

    # ========== 验证和导出 ==========

    def validate(self) -> tuple[bool, list[str]]:
        """验证当前配置"""
        return self.validator.validate(self._config)

    def is_valid(self) -> bool:
        """检查配置是否有效"""
        valid, _ = self.validate()
        return valid

    def get_validation_errors(self) -> list[str]:
        """获取验证错误"""
        _, errors = self.validate()
        return errors

    def to_dict(self) -> dict[str, Any]:
        """导出为字典"""
        return copy.deepcopy(self._config)

    def to_yaml(self, indent: int = 2) -> str:
        """导出为YAML字符串"""
        return yaml.dump(
            self._config, default_flow_style=False, indent=indent, allow_unicode=True
        )

    def save_to_file(self, file_path: str):
        """保存到文件"""
        # 验证配置
        valid, errors = self.validate()
        if not valid:
            raise ValueError(f"配置无效，无法保存: {'; '.join(errors)}")

        with open(file_path, "w", encoding="utf-8") as f:
            yaml.dump(
                self._config, f, default_flow_style=False, indent=2, allow_unicode=True
            )

    # ========== 高级操作 ==========

    def clone(self) -> "GraphConfigProxy":
        """克隆代理对象"""
        # 创建新实例但跳过初始验证（类似create_empty）
        instance = GraphConfigProxy.__new__(GraphConfigProxy)
        instance.validator = GraphConfigValidator()
        instance._config = copy.deepcopy(self._config)
        return instance

    def merge(
        self, other: "GraphConfigProxy", conflict_strategy: str = "error"
    ) -> "GraphConfigProxy":
        """
        合并另一个配置

        Args:
            other: 另一个配置代理
            conflict_strategy: 冲突处理策略 ("error", "keep", "override")

        Returns:
            GraphConfigProxy: 合并后的新代理对象
        """
        if conflict_strategy not in ["error", "keep", "override"]:
            raise ValueError("conflict_strategy必须是'error', 'keep', 或'override'之一")

        # 创建新的配置
        merged_config = copy.deepcopy(self._config)
        other_config = other.to_dict()

        # 合并节点
        existing_node_ids = {node.get("id") for node in merged_config.get("nodes", [])}

        for node in other_config.get("nodes", []):
            node_id = node.get("id")
            if node_id in existing_node_ids:
                if conflict_strategy == "error":
                    raise ValueError(f"节点冲突: '{node_id}' 在两个配置中都存在")
                elif conflict_strategy == "override":
                    # 删除旧节点，添加新节点
                    merged_config["nodes"] = [
                        n for n in merged_config["nodes"] if n.get("id") != node_id
                    ]
                    merged_config["nodes"].append(copy.deepcopy(node))
                # "keep"策略不做任何操作
            else:
                merged_config["nodes"].append(copy.deepcopy(node))

        # 合并边
        existing_edges = {
            (edge.get("from"), edge.get("to"), edge.get("action", "default"))
            for edge in merged_config.get("edges", [])
        }

        for edge in other_config.get("edges", []):
            edge_key = (edge.get("from"), edge.get("to"), edge.get("action", "default"))
            if edge_key not in existing_edges:
                merged_config["edges"].append(copy.deepcopy(edge))

        # 创建新实例但跳过初始验证
        instance = GraphConfigProxy.__new__(GraphConfigProxy)
        instance.validator = GraphConfigValidator()
        instance._config = merged_config
        return instance

    def get_statistics(self) -> dict[str, Any]:
        """获取图统计信息"""
        nodes = self._config.get("nodes", [])
        edges = self._config.get("edges", [])

        # 按类型统计节点
        node_type_counts = {}
        for node in nodes:
            node_type = node.get("type", "unknown")
            node_type_counts[node_type] = node_type_counts.get(node_type, 0) + 1

        # 计算节点度数
        in_degree = {}
        out_degree = {}

        for node in nodes:
            node_id = node.get("id", "")
            in_degree[node_id] = 0
            out_degree[node_id] = 0

        for edge in edges:
            from_node = edge.get("from", "")
            to_node = edge.get("to", "")

            if from_node in out_degree:
                out_degree[from_node] += 1
            if to_node in in_degree:
                in_degree[to_node] += 1

        return {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "node_types": node_type_counts,
            "has_start_node": bool(self._config.get("start_node")),
            "end_node_count": len(self._config.get("end_nodes", [])),
            "max_in_degree": max(in_degree.values()) if in_degree else 0,
            "max_out_degree": max(out_degree.values()) if out_degree else 0,
            "isolated_nodes": [
                node_id
                for node_id, degree in in_degree.items()
                if degree == 0 and out_degree.get(node_id, 0) == 0
            ],
        }

    def __str__(self) -> str:
        """字符串表示"""
        stats = self.get_statistics()
        return (
            f"GraphConfigProxy(name='{self.name}', "
            f"nodes={stats['node_count']}, "
            f"edges={stats['edge_count']}, "
            f"valid={self.is_valid()})"
        )

    def __repr__(self) -> str:
        """调试表示"""
        return self.__str__()
