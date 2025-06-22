"""
YAML配置文件的JSON Schema定义

提供完整的JSON Schema用于验证YAML配置文件的语法和结构。
支持两种配置格式：数组格式和内联格式。
"""

from typing import Any


class YAMLConfigSchema:
    """YAML配置文件的JSON Schema定义"""

    # 支持的节点类型
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
    ]

    @classmethod
    def get_schema(cls) -> dict[str, Any]:
        """
        获取完整的JSON Schema

        这个Schema可以用于：
        1. YAML编辑器的语法提示和验证
        2. 配置文件的静态验证
        3. 生成配置文件模板
        """
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "$id": "https://github.com/yourusername/agenticzero/graph-config.schema.json",
            "title": "AgenticZero Graph Configuration",
            "description": "Configuration schema for AgenticZero graph workflows",
            "type": "object",
            "required": ["name", "start_node", "end_nodes"],
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name of the graph/workflow",
                    "minLength": 1,
                    "maxLength": 100,
                    "examples": ["数据处理工作流", "AI决策流程"],
                },
                "description": {
                    "type": "string",
                    "description": "Description of the graph/workflow",
                    "maxLength": 500,
                    "examples": ["处理用户数据并生成报告", "智能路由和任务分配"],
                },
                "version": {
                    "type": "string",
                    "description": "Version of the configuration",
                    "pattern": "^\\d+\\.\\d+(\\.\\d+)?$",
                    "examples": ["1.0", "2.1.0"],
                },
                "metadata": {
                    "type": "object",
                    "description": "Additional metadata for the graph",
                    "additionalProperties": True,
                    "examples": [
                        {"author": "张三", "team": "数据团队"},
                        {"category": "ETL", "priority": "high"},
                    ],
                },
                "start_node": {
                    "type": "string",
                    "description": "ID of the starting node",
                    "minLength": 1,
                    "pattern": "^[a-zA-Z][a-zA-Z0-9_]*$",
                    "examples": ["start", "input_processor"],
                },
                "end_nodes": {
                    "type": "array",
                    "description": "IDs of the ending nodes",
                    "items": {
                        "type": "string",
                        "minLength": 1,
                        "pattern": "^[a-zA-Z][a-zA-Z0-9_]*$",
                    },
                    "minItems": 1,
                    "uniqueItems": True,
                    "examples": [["end"], ["success", "failure"]],
                },
                "nodes": {
                    "type": "array",
                    "description": "List of nodes (array format)",
                    "items": cls._get_node_schema(),
                    "minItems": 1,
                    "examples": [
                        [
                            {
                                "id": "start",
                                "type": "TaskNode",
                                "name": "开始处理",
                                "description": "初始化处理流程",
                                "params": {"timeout": 30},
                            }
                        ]
                    ],
                },
                "edges": {
                    "type": "array",
                    "description": "List of edges connecting nodes",
                    "items": cls._get_edge_schema(),
                    "default": [],
                    "examples": [
                        [
                            {
                                "from": "start",
                                "to": "process",
                                "action": "default",
                                "weight": 1.0,
                            }
                        ]
                    ],
                },
                "custom_nodes": {
                    "type": "object",
                    "description": "Custom node type definitions",
                    "patternProperties": {
                        "^[a-zA-Z][a-zA-Z0-9_]*$": {
                            "type": "string",
                            "description": "Module path for custom node type",
                            "pattern": "^[a-zA-Z_][a-zA-Z0-9_.]*$",
                            "examples": ["mypackage.nodes.CustomProcessor"],
                        }
                    },
                    "additionalProperties": False,
                    "examples": [
                        {
                            "DataProcessor": "myapp.nodes.DataProcessor",
                            "MLPredictor": "myapp.ai.MLPredictor",
                        }
                    ],
                },
            },
            # 支持内联节点定义
            "patternProperties": {
                "^(?!name$|description$|version$|metadata$|start_node$|end_nodes$|nodes$|edges$|custom_nodes$)[a-zA-Z][a-zA-Z0-9_]*$": cls._get_inline_node_schema()
            },
            "additionalProperties": False,
            "examples": [
                {
                    "name": "简单工作流",
                    "start_node": "input",
                    "end_nodes": ["output"],
                    "nodes": [
                        {"id": "input", "type": "TaskNode", "name": "输入"},
                        {"id": "output", "type": "TaskNode", "name": "输出"},
                    ],
                    "edges": [{"from": "input", "to": "output"}],
                }
            ],
        }

    @classmethod
    def _get_node_schema(cls) -> dict[str, Any]:
        """获取节点的Schema（数组格式）"""
        return {
            "type": "object",
            "required": ["id", "type", "name"],
            "properties": {
                "id": {
                    "type": "string",
                    "description": "Unique identifier for the node",
                    "pattern": "^[a-zA-Z][a-zA-Z0-9_]*$",
                    "minLength": 1,
                    "maxLength": 50,
                    "examples": ["start", "process_data", "branch_1"],
                },
                "type": {
                    "type": "string",
                    "description": "Type of the node",
                    "enum": cls.NODE_TYPES,
                    "examples": ["TaskNode", "BranchControlNode"],
                },
                "name": {
                    "type": "string",
                    "description": "Display name of the node",
                    "minLength": 1,
                    "maxLength": 100,
                    "examples": ["数据处理", "条件判断"],
                },
                "description": {
                    "type": "string",
                    "description": "Description of what the node does",
                    "maxLength": 200,
                    "examples": ["处理输入数据并转换格式", "根据条件选择执行路径"],
                },
                "params": {
                    "type": "object",
                    "description": "Parameters specific to the node type",
                    "additionalProperties": True,
                    "examples": [
                        {"timeout": 30, "retry_count": 3},
                        {"condition_func": "lambda x: x > 10"},
                    ],
                },
                "metadata": {
                    "type": "object",
                    "description": "Additional metadata for the node",
                    "additionalProperties": True,
                    "examples": [
                        {"category": "processing", "author": "system"},
                        {"priority": "high", "version": "2.0"},
                    ],
                },
            },
            "additionalProperties": False,
        }

    @classmethod
    def _get_inline_node_schema(cls) -> dict[str, Any]:
        """获取内联节点的Schema"""
        return {
            "type": "object",
            "required": ["type", "name"],
            "properties": {
                "type": {
                    "type": "string",
                    "description": "Type of the node",
                    "enum": cls.NODE_TYPES,
                },
                "name": {
                    "type": "string",
                    "description": "Display name of the node",
                    "minLength": 1,
                    "maxLength": 100,
                },
                "description": {
                    "type": "string",
                    "description": "Description of what the node does",
                    "maxLength": 200,
                },
                "params": {
                    "type": "object",
                    "description": "Parameters specific to the node type",
                    "additionalProperties": True,
                },
                "metadata": {
                    "type": "object",
                    "description": "Additional metadata for the node",
                    "additionalProperties": True,
                },
            },
            "additionalProperties": False,
        }

    @classmethod
    def _get_edge_schema(cls) -> dict[str, Any]:
        """获取边的Schema"""
        return {
            "type": "object",
            "required": ["from", "to"],
            "properties": {
                "from": {
                    "type": "string",
                    "description": "ID of the source node",
                    "minLength": 1,
                    "pattern": "^[a-zA-Z][a-zA-Z0-9_]*$",
                    "examples": ["start", "branch_node"],
                },
                "to": {
                    "type": "string",
                    "description": "ID of the target node",
                    "minLength": 1,
                    "pattern": "^[a-zA-Z][a-zA-Z0-9_]*$",
                    "examples": ["process", "end"],
                },
                "action": {
                    "type": "string",
                    "description": "Action or condition for the edge",
                    "default": "default",
                    "examples": ["default", "success", "failure", "high", "low"],
                },
                "condition": {
                    "type": "string",
                    "description": "Condition expression (compatibility field)",
                    "examples": ["x > 10", "status == 'success'"],
                },
                "weight": {
                    "type": "number",
                    "description": "Weight of the edge",
                    "default": 1.0,
                    "minimum": 0,
                    "examples": [1.0, 0.5, 2.0],
                },
                "metadata": {
                    "type": "object",
                    "description": "Additional metadata for the edge",
                    "additionalProperties": True,
                    "examples": [{"priority": "high"}, {"description": "主要路径"}],
                },
            },
            "additionalProperties": False,
        }

    @classmethod
    def get_node_param_schema(cls, node_type: str) -> dict[str, Any]:
        """
        获取特定节点类型的参数Schema

        Args:
            node_type: 节点类型

        Returns:
            参数Schema
        """
        schemas = {
            "BranchControlNode": {
                "type": "object",
                "required": ["condition_func"],
                "properties": {
                    "condition_func": {
                        "type": "string",
                        "description": "Condition function as string (e.g., lambda expression)",
                        "examples": [
                            "lambda x: x > 10",
                            "lambda data: data['status'] == 'ok'",
                        ],
                    }
                },
                "additionalProperties": True,
            },
            "ForkControlNode": {
                "type": "object",
                "properties": {
                    "fork_count": {
                        "type": "integer",
                        "description": "Number of parallel branches",
                        "minimum": 2,
                        "default": 2,
                        "examples": [2, 3, 5],
                    }
                },
                "additionalProperties": True,
            },
            "RetryNode": {
                "type": "object",
                "properties": {
                    "max_retries": {
                        "type": "integer",
                        "description": "Maximum number of retry attempts",
                        "minimum": 1,
                        "default": 3,
                        "examples": [3, 5, 10],
                    },
                    "retry_delay": {
                        "type": "number",
                        "description": "Delay between retries in seconds",
                        "minimum": 0,
                        "default": 1.0,
                        "examples": [1.0, 2.5, 5.0],
                    },
                },
                "additionalProperties": True,
            },
            "TimeoutNode": {
                "type": "object",
                "required": ["timeout_seconds"],
                "properties": {
                    "timeout_seconds": {
                        "type": "number",
                        "description": "Timeout duration in seconds",
                        "minimum": 0.1,
                        "examples": [30.0, 60.0, 120.0],
                    }
                },
                "additionalProperties": True,
            },
            "AIRouter": {
                "type": "object",
                "required": ["routes"],
                "properties": {
                    "routes": {
                        "type": "array",
                        "description": "List of possible routes",
                        "items": {"type": "string"},
                        "minItems": 2,
                        "examples": [
                            ["route_a", "route_b"],
                            ["high_priority", "normal", "low_priority"],
                        ],
                    }
                },
                "additionalProperties": True,
            },
        }

        return schemas.get(
            node_type,
            {
                "type": "object",
                "description": f"Parameters for {node_type}",
                "additionalProperties": True,
            },
        )

    @classmethod
    def save_schema_file(cls, filepath: str = "graph-config.schema.json") -> None:
        """
        保存Schema到文件

        Args:
            filepath: 保存路径
        """
        import json

        schema = cls.get_schema()
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(schema, f, indent=2, ensure_ascii=False)

    @classmethod
    def get_yaml_header(cls) -> str:
        """
        获取YAML文件头部，包含Schema引用

        Returns:
            YAML头部字符串
        """
        return """# yaml-language-server: $schema=./graph-config.schema.json
# 上面这行告诉YAML编辑器使用JSON Schema进行验证和提示

"""
