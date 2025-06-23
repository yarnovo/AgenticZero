"""Python MCP 服务器

提供 Python 代码管理和执行的 MCP 服务
"""

from typing import Any

from .python_file_manager import PythonFileManager
from .python_memory_manager import PythonMemoryManager


class PythonMCPServer:
    """Python MCP 服务器"""

    def __init__(self, base_dir: str = "python_scripts"):
        """初始化 Python MCP 服务器

        Args:
            base_dir: Python 文件存储的基础目录
        """
        self.file_manager = PythonFileManager(base_dir)
        self.memory_manager = PythonMemoryManager()
        self.name = "python_mcp_server"
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
                "name": "python_create",
                "description": "创建新的 Python 文件",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "文件名（不含 .py 后缀）",
                        },
                        "code": {"type": "string", "description": "Python 代码内容"},
                        "description": {
                            "type": "string",
                            "description": "文件描述（可选）",
                        },
                    },
                    "required": ["name", "code"],
                },
            },
            {
                "name": "python_read",
                "description": "读取 Python 文件内容",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "文件名（不含 .py 后缀）",
                        }
                    },
                    "required": ["name"],
                },
            },
            {
                "name": "python_update",
                "description": "更新 Python 文件内容",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "文件名（不含 .py 后缀）",
                        },
                        "code": {
                            "type": "string",
                            "description": "新的 Python 代码内容",
                        },
                    },
                    "required": ["name", "code"],
                },
            },
            {
                "name": "python_delete",
                "description": "删除 Python 文件",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "文件名（不含 .py 后缀）",
                        }
                    },
                    "required": ["name"],
                },
            },
            {
                "name": "python_list",
                "description": "列出所有 Python 文件",
                "inputSchema": {"type": "object", "properties": {}},
            },
            {
                "name": "python_search",
                "description": "搜索 Python 文件",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "keyword": {"type": "string", "description": "搜索关键词"}
                    },
                    "required": ["keyword"],
                },
            },
            {
                "name": "python_execute",
                "description": "在沙盒中执行 Python 代码",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "要执行的 Python 代码",
                        },
                        "sandbox_id": {
                            "type": "string",
                            "description": "沙盒标识符（可选，None 表示临时沙盒）",
                        },
                        "timeout": {
                            "type": "integer",
                            "description": "超时时间（秒，默认 5）",
                        },
                        "use_process": {
                            "type": "boolean",
                            "description": "是否使用独立进程（默认 true）",
                        },
                    },
                    "required": ["code"],
                },
            },
            {
                "name": "python_execute_file",
                "description": "执行 Python 文件",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "文件名（不含 .py 后缀）",
                        },
                        "sandbox_id": {
                            "type": "string",
                            "description": "沙盒标识符（可选）",
                        },
                        "timeout": {
                            "type": "integer",
                            "description": "超时时间（秒，默认 5）",
                        },
                    },
                    "required": ["name"],
                },
            },
            {
                "name": "python_sandbox_create",
                "description": "创建持久沙盒环境",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "sandbox_id": {"type": "string", "description": "沙盒标识符"}
                    },
                    "required": ["sandbox_id"],
                },
            },
            {
                "name": "python_sandbox_delete",
                "description": "删除沙盒环境",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "sandbox_id": {"type": "string", "description": "沙盒标识符"}
                    },
                    "required": ["sandbox_id"],
                },
            },
            {
                "name": "python_sandbox_status",
                "description": "获取沙盒状态",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "sandbox_id": {"type": "string", "description": "沙盒标识符"}
                    },
                    "required": ["sandbox_id"],
                },
            },
            {
                "name": "python_sandbox_list",
                "description": "列出所有沙盒",
                "inputSchema": {"type": "object", "properties": {}},
            },
        ]

    async def handle_call_tool(
        self, name: str, arguments: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """处理工具调用"""
        if arguments is None:
            arguments = {}

        try:
            # 文件管理相关工具
            if name == "python_create":
                result = self.file_manager.create(
                    name=arguments["name"],
                    code=arguments["code"],
                    description=arguments.get("description", ""),
                )
                return [
                    {
                        "type": "text",
                        "text": f"Python 文件 '{arguments['name']}.py' 创建成功\n"
                        f"路径: {result['path']}\n"
                        f"行数: {result['lines']}",
                    }
                ]

            elif name == "python_read":
                result = self.file_manager.read(arguments["name"])
                return [
                    {
                        "type": "text",
                        "text": f"文件: {result['name']}.py\n"
                        f"创建时间: {result['metadata']['created_at']}\n"
                        f"更新时间: {result['metadata']['updated_at']}\n"
                        f"代码:\n```python\n{result['code']}\n```",
                    }
                ]

            elif name == "python_update":
                result = self.file_manager.update(
                    name=arguments["name"], code=arguments["code"]
                )
                return [
                    {
                        "type": "text",
                        "text": f"Python 文件 '{arguments['name']}.py' 更新成功\n"
                        f"更新时间: {result['updated_at']}",
                    }
                ]

            elif name == "python_delete":
                self.file_manager.delete(arguments["name"])
                return [
                    {
                        "type": "text",
                        "text": f"Python 文件 '{arguments['name']}.py' 删除成功",
                    }
                ]

            elif name == "python_list":
                files = self.file_manager.list()
                if not files:
                    return [{"type": "text", "text": "没有找到任何 Python 文件"}]

                file_list = []
                for f in files:
                    file_list.append(
                        f"- {f['name']}.py ({f['lines']} 行) - {f.get('description', '无描述')}"
                    )

                return [
                    {
                        "type": "text",
                        "text": f"找到 {len(files)} 个 Python 文件:\n"
                        + "\n".join(file_list),
                    }
                ]

            elif name == "python_search":
                results = self.file_manager.search(arguments["keyword"])
                if not results:
                    return [
                        {
                            "type": "text",
                            "text": f"没有找到包含 '{arguments['keyword']}' 的文件",
                        }
                    ]

                file_list = []
                for f in results:
                    file_list.append(
                        f"- {f['name']}.py - {f.get('description', '无描述')}"
                    )

                return [
                    {
                        "type": "text",
                        "text": f"找到 {len(results)} 个匹配的文件:\n"
                        + "\n".join(file_list),
                    }
                ]

            # 代码执行相关工具
            elif name == "python_execute":
                result = self.memory_manager.execute_code(
                    code=arguments["code"],
                    sandbox_id=arguments.get("sandbox_id"),
                    timeout=arguments.get("timeout", 5),
                    use_process=arguments.get("use_process", True),
                )

                if result["success"]:
                    return [
                        {
                            "type": "text",
                            "text": f"执行成功（耗时: {result['execution_time']:.3f}秒）\n"
                            f"输出:\n{result['output']}",
                        }
                    ]
                else:
                    return [
                        {"type": "text", "text": f"执行失败\n错误:\n{result['error']}"}
                    ]

            elif name == "python_execute_file":
                # 先读取文件
                file_data = self.file_manager.read(arguments["name"])

                # 执行代码
                result = self.memory_manager.execute_code(
                    code=file_data["code"],
                    sandbox_id=arguments.get("sandbox_id"),
                    timeout=arguments.get("timeout", 5),
                    use_process=True,
                )

                if result["success"]:
                    return [
                        {
                            "type": "text",
                            "text": f"文件 '{arguments['name']}.py' 执行成功（耗时: {result['execution_time']:.3f}秒）\n"
                            f"输出:\n{result['output']}",
                        }
                    ]
                else:
                    return [
                        {
                            "type": "text",
                            "text": f"文件 '{arguments['name']}.py' 执行失败\n"
                            f"错误:\n{result['error']}",
                        }
                    ]

            # 沙盒管理相关工具
            elif name == "python_sandbox_create":
                self.memory_manager.create_sandbox(arguments["sandbox_id"])
                return [
                    {
                        "type": "text",
                        "text": f"沙盒 '{arguments['sandbox_id']}' 创建成功",
                    }
                ]

            elif name == "python_sandbox_delete":
                self.memory_manager.delete_sandbox(arguments["sandbox_id"])
                return [
                    {
                        "type": "text",
                        "text": f"沙盒 '{arguments['sandbox_id']}' 删除成功",
                    }
                ]

            elif name == "python_sandbox_status":
                status = self.memory_manager.get_sandbox_status(arguments["sandbox_id"])

                var_list = []
                for name, info in status["variables"].items():
                    var_list.append(f"  - {name}: {info['type']} = {info['value']}")

                return [
                    {
                        "type": "text",
                        "text": f"沙盒 '{status['sandbox_id']}' 状态:\n"
                        f"变量数量: {status['variable_count']}\n"
                        f"变量列表:\n" + "\n".join(var_list),
                    }
                ]

            elif name == "python_sandbox_list":
                sandboxes = self.memory_manager.list_sandboxes()
                if not sandboxes:
                    return [{"type": "text", "text": "没有活动的沙盒"}]

                return [
                    {
                        "type": "text",
                        "text": f"活动沙盒 ({len(sandboxes)} 个):\n"
                        + "\n".join([f"- {sid}" for sid in sandboxes]),
                    }
                ]

            else:
                return [{"type": "text", "text": f"未知的工具: {name}"}]

        except Exception as e:
            return [{"type": "text", "text": f"执行工具 '{name}' 时出错: {str(e)}"}]
