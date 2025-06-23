"""Graph MCP 服务器

提供图管理功能的 MCP 服务封装
"""

import json
import traceback
from typing import Any

from src.graph import GraphManager


class GraphMCPServer:
    """Graph MCP 服务器"""

    def __init__(self, graph_manager: GraphManager | None = None):
        """初始化 Graph MCP 服务器

        Args:
            graph_manager: GraphManager 实例（如果不提供则创建新实例）
        """
        self.graph_manager = graph_manager or GraphManager()
        self.name = "graph_mcp_server"
        self.version = "1.0.0"

    async def handle_initialize(self, params: dict[str, Any]) -> dict[str, Any]:
        """处理初始化请求"""
        return {
            "capabilities": {"tools": {"available": True}},
            "serverInfo": {"name": self.name, "version": self.version},
        }

    async def handle_list_tools(self) -> list[dict[str, Any]]:
        """列出所有可用工具"""
        return [
            {
                "name": "graph_create",
                "description": "创建新的图",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "graph_id": {"type": "string", "description": "图的唯一标识符"},
                        "description": {
                            "type": "string",
                            "description": "图的描述（可选）",
                        },
                        "save_to_file": {
                            "type": "boolean",
                            "description": "是否保存到文件（默认 true）",
                        },
                    },
                    "required": ["graph_id"],
                },
            },
            {
                "name": "graph_load",
                "description": "从文件加载图",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "graph_id": {"type": "string", "description": "图的唯一标识符"}
                    },
                    "required": ["graph_id"],
                },
            },
            {
                "name": "graph_save",
                "description": "保存图到文件",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "graph_id": {"type": "string", "description": "图的唯一标识符"}
                    },
                    "required": ["graph_id"],
                },
            },
            {
                "name": "graph_delete",
                "description": "删除图",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "graph_id": {"type": "string", "description": "图的唯一标识符"},
                        "delete_file": {
                            "type": "boolean",
                            "description": "是否同时删除文件（默认 true）",
                        },
                    },
                    "required": ["graph_id"],
                },
            },
            {
                "name": "graph_list",
                "description": "列出所有图",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "source": {
                            "type": "string",
                            "enum": ["all", "memory", "file"],
                            "description": "数据源（默认 all）",
                        }
                    },
                },
            },
            {
                "name": "graph_info",
                "description": "获取图的详细信息",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "graph_id": {"type": "string", "description": "图的唯一标识符"}
                    },
                    "required": ["graph_id"],
                },
            },
            {
                "name": "graph_run",
                "description": "执行图",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "graph_id": {"type": "string", "description": "图的唯一标识符"},
                        "initial_data": {
                            "type": "object",
                            "description": "初始输入数据（可选）",
                        },
                    },
                    "required": ["graph_id"],
                },
            },
            {
                "name": "graph_node_add",
                "description": "向图中添加节点",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "graph_id": {"type": "string", "description": "图的唯一标识符"},
                        "node_type": {"type": "string", "description": "节点类型"},
                        "node_id": {"type": "string", "description": "节点ID"},
                        "config": {"type": "object", "description": "节点配置"},
                    },
                    "required": ["graph_id", "node_type", "node_id"],
                },
            },
            {
                "name": "graph_node_remove",
                "description": "从图中移除节点",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "graph_id": {"type": "string", "description": "图的唯一标识符"},
                        "node_id": {"type": "string", "description": "节点ID"},
                    },
                    "required": ["graph_id", "node_id"],
                },
            },
            {
                "name": "graph_edge_add",
                "description": "向图中添加边",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "graph_id": {"type": "string", "description": "图的唯一标识符"},
                        "from_node": {"type": "string", "description": "起始节点ID"},
                        "to_node": {"type": "string", "description": "目标节点ID"},
                        "condition": {
                            "type": "string",
                            "description": "边的条件（可选）",
                        },
                    },
                    "required": ["graph_id", "from_node", "to_node"],
                },
            },
            {
                "name": "graph_edge_remove",
                "description": "从图中移除边",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "graph_id": {"type": "string", "description": "图的唯一标识符"},
                        "from_node": {"type": "string", "description": "起始节点ID"},
                        "to_node": {"type": "string", "description": "目标节点ID"},
                    },
                    "required": ["graph_id", "from_node", "to_node"],
                },
            },
            {
                "name": "graph_validate",
                "description": "验证图的结构",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "graph_id": {"type": "string", "description": "图的唯一标识符"}
                    },
                    "required": ["graph_id"],
                },
            },
        ]

    async def handle_call_tool(
        self, name: str, arguments: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """处理工具调用"""
        if arguments is None:
            arguments = {}

        try:
            # 图的基本操作
            if name == "graph_create":
                graph_id = arguments["graph_id"]
                description = arguments.get("description", "")
                save_to_file = arguments.get("save_to_file", True)

                # 创建图
                proxy = self.graph_manager.create(
                    name=graph_id, description=description, auto_load=save_to_file
                )

                return [{"type": "text", "text": f"图 '{graph_id}' 创建成功"}]

            elif name == "graph_load":
                graph_id = arguments["graph_id"]
                proxy = self.graph_manager.load(graph_id)
                graph = proxy.graph

                return [
                    {
                        "type": "text",
                        "text": f"图 '{graph_id}' 加载成功\n"
                        f"节点数: {len(graph.nodes)}\n"
                        f"边数: {len(graph.edges)}",
                    }
                ]

            elif name == "graph_save":
                graph_id = arguments["graph_id"]
                self.graph_manager.save(graph_id)

                return [{"type": "text", "text": f"图 '{graph_id}' 保存成功"}]

            elif name == "graph_delete":
                graph_id = arguments["graph_id"]
                delete_file = arguments.get("delete_file", True)

                self.graph_manager.delete(graph_id, force=delete_file)

                return [{"type": "text", "text": f"图 '{graph_id}' 删除成功"}]

            elif name == "graph_list":
                source = arguments.get("source", "all")

                if source == "all":
                    all_graphs = self.graph_manager.list_all()
                    graph_list = []
                    for graph_name, info in all_graphs.items():
                        status = info["status"]
                        graph_list.append(f"- {graph_name} ({status})")
                elif source == "memory":
                    graphs = self.graph_manager.memory_manager.list_loaded()
                    graph_list = [f"- {g} (已加载)" for g in graphs]
                elif source == "file":
                    graphs = self.graph_manager.file_manager.list()
                    graph_list = [f"- {g}" for g in graphs]
                else:
                    graph_list = []

                if not graph_list:
                    return [{"type": "text", "text": "没有找到任何图"}]

                return [
                    {
                        "type": "text",
                        "text": f"找到 {len(graph_list)} 个图:\n"
                        + "\n".join(graph_list),
                    }
                ]

            elif name == "graph_info":
                graph_id = arguments["graph_id"]

                # 获取图
                if self.graph_manager.memory_manager.is_loaded(graph_id):
                    proxy = self.graph_manager.get_proxy(graph_id)
                    if proxy:
                        graph = proxy.graph
                    else:
                        proxy = self.graph_manager.load(graph_id)
                        graph = proxy.graph
                    source = "内存"
                else:
                    proxy = self.graph_manager.load(graph_id)
                    graph = proxy.graph
                    source = "文件"

                # 获取节点信息
                node_types = {}
                for node in graph.nodes.values():
                    node_type = type(node).__name__
                    node_types[node_type] = node_types.get(node_type, 0) + 1

                node_info = "\n".join(
                    [f"  - {t}: {c} 个" for t, c in node_types.items()]
                )

                return [
                    {
                        "type": "text",
                        "text": f"图 '{graph_id}' 信息:\n"
                        f"来源: {source}\n"
                        f"描述: {getattr(graph, 'description', '无描述')}\n"
                        f"节点数: {len(graph.nodes)}\n"
                        f"节点类型:\n{node_info}\n"
                        f"边数: {len(graph.edges)}",
                    }
                ]

            elif name == "graph_run":
                graph_id = arguments["graph_id"]
                initial_data = arguments.get("initial_data", {})

                # 执行图
                result = await self.graph_manager.run(graph_id, initial_data)

                # 格式化输出
                output = f"图 '{graph_id}' 执行完成\n"

                # 显示执行结果
                if isinstance(result, dict):
                    output += "执行结果:\n"
                    for key, value in result.items():
                        output += f"  {key}: {json.dumps(value, ensure_ascii=False, indent=2)}\n"
                else:
                    output += f"执行结果: {result}"

                return [{"type": "text", "text": output}]

            # 图结构操作
            elif name == "graph_node_add":
                graph_id = arguments["graph_id"]
                node_type = arguments["node_type"]
                node_id = arguments["node_id"]
                config = arguments.get("config", {})

                # 获取图代理
                proxy = self.graph_manager.get_proxy(graph_id)
                if not proxy:
                    proxy = self.graph_manager.load(graph_id)

                # 添加节点
                proxy.add_node(node_id, node_type, **config)

                # 保存更改
                self.graph_manager.save(graph_id)

                return [
                    {
                        "type": "text",
                        "text": f"节点 '{node_id}' (类型: {node_type}) 已添加到图 '{graph_id}'",
                    }
                ]

            elif name == "graph_node_remove":
                graph_id = arguments["graph_id"]
                node_id = arguments["node_id"]

                # 获取图代理
                proxy = self.graph_manager.get_proxy(graph_id)
                if not proxy:
                    proxy = self.graph_manager.load(graph_id)

                # 移除节点
                proxy.remove_node(node_id)

                # 保存更改
                self.graph_manager.save(graph_id)

                return [
                    {
                        "type": "text",
                        "text": f"节点 '{node_id}' 已从图 '{graph_id}' 中移除",
                    }
                ]

            elif name == "graph_edge_add":
                graph_id = arguments["graph_id"]
                from_node = arguments["from_node"]
                to_node = arguments["to_node"]
                condition = arguments.get("condition")

                # 获取图代理
                proxy = self.graph_manager.get_proxy(graph_id)
                if not proxy:
                    proxy = self.graph_manager.load(graph_id)

                # 添加边
                if condition:
                    proxy.add_edge(from_node, to_node, condition)
                else:
                    proxy.add_edge(from_node, to_node)

                # 保存更改
                self.graph_manager.save(graph_id)

                edge_desc = f"'{from_node}' -> '{to_node}'"
                if condition:
                    edge_desc += f" (条件: {condition})"

                return [
                    {"type": "text", "text": f"边 {edge_desc} 已添加到图 '{graph_id}'"}
                ]

            elif name == "graph_edge_remove":
                graph_id = arguments["graph_id"]
                from_node = arguments["from_node"]
                to_node = arguments["to_node"]

                # 获取图代理
                proxy = self.graph_manager.get_proxy(graph_id)
                if not proxy:
                    proxy = self.graph_manager.load(graph_id)

                # 移除边
                proxy.remove_edge(from_node, to_node)

                # 保存更改
                self.graph_manager.save(graph_id)

                return [
                    {
                        "type": "text",
                        "text": f"边 '{from_node}' -> '{to_node}' 已从图 '{graph_id}' 中移除",
                    }
                ]

            elif name == "graph_validate":
                graph_id = arguments["graph_id"]

                # 获取图代理
                proxy = self.graph_manager.get_proxy(graph_id)
                if not proxy:
                    proxy = self.graph_manager.load(graph_id)

                # 验证图
                is_valid, errors = proxy.validate()

                if is_valid:
                    return [{"type": "text", "text": f"图 '{graph_id}' 结构验证通过"}]
                else:
                    error_list = "\n".join([f"  - {error}" for error in errors])
                    return [
                        {
                            "type": "text",
                            "text": f"图 '{graph_id}' 结构验证失败:\n{error_list}",
                        }
                    ]

            else:
                return [{"type": "text", "text": f"未知的工具: {name}"}]

        except Exception as e:
            error_details = traceback.format_exc()
            return [
                {
                    "type": "text",
                    "text": f"执行工具 '{name}' 时出错:\n{str(e)}\n\n详细信息:\n{error_details}",
                }
            ]
