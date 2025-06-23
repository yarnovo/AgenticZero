"""MCP 服务管理器

统一管理所有 MCP 服务的生命周期
"""

import json
from datetime import datetime
from typing import Any

from src.graph import GraphManager

from .graph_mcp import GraphMCPServer
from .python_mcp import PythonMCPServer


class MCPServiceManager:
    """MCP 服务管理器

    提供统一的 MCP 服务池管理功能
    """

    def __init__(self, graph_manager: GraphManager | None = None):
        """初始化 MCP 服务管理器

        Args:
            graph_manager: GraphManager 实例（用于 Graph MCP 服务）
        """
        self.name = "mcp_service_manager"
        self.version = "1.0.0"
        self.services: dict[str, Any] = {}
        self.service_types = {
            "python": {
                "class": PythonMCPServer,
                "description": "Python 代码管理和执行服务",
                "config_schema": {
                    "base_dir": {
                        "type": "string",
                        "description": "Python 文件存储目录",
                        "default": "python_scripts",
                    }
                },
            },
            "graph": {
                "class": GraphMCPServer,
                "description": "图管理和执行服务",
                "config_schema": {},
                "requires_graph_manager": True,
            },
        }
        self.graph_manager = graph_manager

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
                "name": "service_list",
                "description": "列出所有可用的 MCP 服务类型和实例",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "show_instances": {
                            "type": "boolean",
                            "description": "是否显示服务实例（默认 true）",
                        }
                    },
                },
            },
            {
                "name": "service_create",
                "description": "创建新的 MCP 服务实例",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "service_type": {
                            "type": "string",
                            "enum": list(self.service_types.keys()),
                            "description": "服务类型",
                        },
                        "service_id": {
                            "type": "string",
                            "description": "服务实例的唯一标识符",
                        },
                        "config": {"type": "object", "description": "服务配置（可选）"},
                    },
                    "required": ["service_type", "service_id"],
                },
            },
            {
                "name": "service_delete",
                "description": "删除 MCP 服务实例",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "service_id": {
                            "type": "string",
                            "description": "服务实例的唯一标识符",
                        }
                    },
                    "required": ["service_id"],
                },
            },
            {
                "name": "service_info",
                "description": "获取服务实例的详细信息",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "service_id": {
                            "type": "string",
                            "description": "服务实例的唯一标识符",
                        }
                    },
                    "required": ["service_id"],
                },
            },
            {
                "name": "service_call",
                "description": "调用特定服务的工具",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "service_id": {
                            "type": "string",
                            "description": "服务实例的唯一标识符",
                        },
                        "tool_name": {
                            "type": "string",
                            "description": "要调用的工具名称",
                        },
                        "arguments": {"type": "object", "description": "工具参数"},
                    },
                    "required": ["service_id", "tool_name"],
                },
            },
            {
                "name": "service_list_tools",
                "description": "列出特定服务的所有可用工具",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "service_id": {
                            "type": "string",
                            "description": "服务实例的唯一标识符",
                        }
                    },
                    "required": ["service_id"],
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
            if name == "service_list":
                show_instances = arguments.get("show_instances", True)

                # 列出服务类型
                output = "可用的 MCP 服务类型:\n"
                for stype, info in self.service_types.items():
                    output += f"\n- {stype}: {info['description']}"
                    if info.get("config_schema"):
                        output += "\n  配置参数:"
                        for param, schema in info["config_schema"].items():
                            output += f"\n    - {param}: {schema['description']}"

                # 列出服务实例
                if show_instances:
                    output += "\n\n活动的服务实例:"
                    if self.services:
                        for sid, sinfo in self.services.items():
                            output += f"\n- {sid} (类型: {sinfo['type']}, 创建时间: {sinfo['created_at']})"
                    else:
                        output += "\n（无活动实例）"

                return [{"type": "text", "text": output}]

            elif name == "service_create":
                service_type = arguments["service_type"]
                service_id = arguments["service_id"]
                config = arguments.get("config", {})

                # 检查服务类型
                if service_type not in self.service_types:
                    return [{"type": "text", "text": f"未知的服务类型: {service_type}"}]

                # 检查服务ID是否已存在
                if service_id in self.services:
                    return [{"type": "text", "text": f"服务实例 '{service_id}' 已存在"}]

                # 创建服务实例
                service_info = self.service_types[service_type]

                # 检查是否需要 graph_manager
                if (
                    service_info.get("requires_graph_manager")
                    and not self.graph_manager
                ):
                    return [
                        {
                            "type": "text",
                            "text": f"服务类型 '{service_type}' 需要 GraphManager 实例",
                        }
                    ]

                # 创建实例
                if service_type == "python":
                    base_dir = config.get("base_dir", "python_scripts")
                    instance = PythonMCPServer(base_dir=base_dir)
                elif service_type == "graph":
                    instance = GraphMCPServer(graph_manager=self.graph_manager)

                # 保存实例信息
                self.services[service_id] = {
                    "type": service_type,
                    "instance": instance,
                    "config": config,
                    "created_at": datetime.now().isoformat(),
                }

                return [
                    {
                        "type": "text",
                        "text": f"服务实例 '{service_id}' (类型: {service_type}) 创建成功",
                    }
                ]

            elif name == "service_delete":
                service_id = arguments["service_id"]

                if service_id not in self.services:
                    return [{"type": "text", "text": f"服务实例 '{service_id}' 不存在"}]

                # 删除服务实例
                service_type = self.services[service_id]["type"]
                del self.services[service_id]

                return [
                    {
                        "type": "text",
                        "text": f"服务实例 '{service_id}' (类型: {service_type}) 删除成功",
                    }
                ]

            elif name == "service_info":
                service_id = arguments["service_id"]

                if service_id not in self.services:
                    return [{"type": "text", "text": f"服务实例 '{service_id}' 不存在"}]

                info = self.services[service_id]

                output = f"服务实例: {service_id}\n"
                output += f"类型: {info['type']}\n"
                output += f"创建时间: {info['created_at']}\n"
                if info["config"]:
                    output += f"配置: {json.dumps(info['config'], ensure_ascii=False, indent=2)}"

                return [{"type": "text", "text": output}]

            elif name == "service_call":
                service_id = arguments["service_id"]
                tool_name = arguments["tool_name"]
                tool_args = arguments.get("arguments", {})

                if service_id not in self.services:
                    return [{"type": "text", "text": f"服务实例 '{service_id}' 不存在"}]

                # 获取服务实例
                instance = self.services[service_id]["instance"]

                # 调用工具
                result = await instance.handle_call_tool(tool_name, tool_args)

                # 添加服务标识
                for item in result:
                    if item["type"] == "text":
                        item["text"] = f"[{service_id}] {item['text']}"

                return result

            elif name == "service_list_tools":
                service_id = arguments["service_id"]

                if service_id not in self.services:
                    return [{"type": "text", "text": f"服务实例 '{service_id}' 不存在"}]

                # 获取服务实例
                instance = self.services[service_id]["instance"]

                # 获取工具列表
                tools = await instance.handle_list_tools()

                output = f"服务 '{service_id}' 的可用工具:\n"
                for tool in tools:
                    output += f"\n- {tool['name']}: {tool['description']}"
                    if "inputSchema" in tool and "properties" in tool["inputSchema"]:
                        output += "\n  参数:"
                        for param, schema in tool["inputSchema"]["properties"].items():
                            required = param in tool["inputSchema"].get("required", [])
                            req_mark = " (必需)" if required else " (可选)"
                            output += f"\n    - {param}: {schema.get('description', '无描述')}{req_mark}"

                return [{"type": "text", "text": output}]

            else:
                return [{"type": "text", "text": f"未知的工具: {name}"}]

        except Exception as e:
            import traceback

            error_details = traceback.format_exc()
            return [
                {
                    "type": "text",
                    "text": f"执行工具 '{name}' 时出错:\n{str(e)}\n\n详细信息:\n{error_details}",
                }
            ]
