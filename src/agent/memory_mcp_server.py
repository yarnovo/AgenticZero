"""记忆模块的MCP服务器实现。"""

import json
import logging
from typing import Any

from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from mcp.types import (
    Content,
    TextContent,
    Tool,
)

from .memory_manager import (
    MemoryManager,
    MemoryManagerInterface,
    MemoryQuery,
    MemoryType,
)

logger = logging.getLogger(__name__)


class MemoryMCPServer:
    """记忆模块的MCP服务器。"""

    def __init__(self, memory_manager: MemoryManagerInterface | None = None):
        """初始化MCP服务器。

        Args:
            memory_manager: 记忆管理器实例，如果不提供则创建默认的内存管理器
        """
        self.server = Server("memory-service")
        self.memory_manager = memory_manager or MemoryManager.create_memory_manager()
        self._setup_handlers()

    def _setup_handlers(self) -> None:
        """设置MCP处理器。"""

        @self.server.list_tools()
        async def handle_list_tools() -> list[Tool]:
            """列出所有可用的记忆工具。"""
            return [
                Tool(
                    name="memory_store",
                    description="存储新的记忆到记忆系统",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "记忆内容",
                            },
                            "memory_type": {
                                "type": "string",
                                "enum": [
                                    "short_term",
                                    "long_term",
                                    "episodic",
                                    "semantic",
                                ],
                                "description": "记忆类型",
                            },
                            "importance": {
                                "type": "number",
                                "minimum": 0,
                                "maximum": 1,
                                "description": "重要性分数(0-1)",
                                "default": 0.5,
                            },
                            "metadata": {
                                "type": "object",
                                "description": "额外的元数据",
                                "default": {},
                            },
                        },
                        "required": ["content", "memory_type"],
                    },
                ),
                Tool(
                    name="memory_search",
                    description="搜索相关的记忆",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "搜索查询",
                            },
                            "memory_types": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "enum": [
                                        "short_term",
                                        "long_term",
                                        "episodic",
                                        "semantic",
                                    ],
                                },
                                "description": "限定的记忆类型",
                                "default": None,
                            },
                            "limit": {
                                "type": "integer",
                                "minimum": 1,
                                "maximum": 100,
                                "description": "返回数量限制",
                                "default": 10,
                            },
                            "min_importance": {
                                "type": "number",
                                "minimum": 0,
                                "maximum": 1,
                                "description": "最小重要性阈值",
                                "default": 0.0,
                            },
                        },
                        "required": ["query"],
                    },
                ),
                Tool(
                    name="memory_get_recent",
                    description="获取最近的记忆",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "limit": {
                                "type": "integer",
                                "minimum": 1,
                                "maximum": 100,
                                "description": "返回数量限制",
                                "default": 10,
                            },
                            "memory_types": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "enum": [
                                        "short_term",
                                        "long_term",
                                        "episodic",
                                        "semantic",
                                    ],
                                },
                                "description": "限定的记忆类型",
                                "default": None,
                            },
                        },
                    },
                ),
                Tool(
                    name="memory_get_important",
                    description="获取重要的记忆",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "limit": {
                                "type": "integer",
                                "minimum": 1,
                                "maximum": 100,
                                "description": "返回数量限制",
                                "default": 10,
                            },
                            "min_importance": {
                                "type": "number",
                                "minimum": 0,
                                "maximum": 1,
                                "description": "最小重要性阈值",
                                "default": 0.7,
                            },
                            "memory_types": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "enum": [
                                        "short_term",
                                        "long_term",
                                        "episodic",
                                        "semantic",
                                    ],
                                },
                                "description": "限定的记忆类型",
                                "default": None,
                            },
                        },
                    },
                ),
                Tool(
                    name="memory_update",
                    description="更新现有的记忆",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "memory_id": {
                                "type": "string",
                                "description": "记忆ID",
                            },
                            "content": {
                                "type": "string",
                                "description": "新的记忆内容",
                            },
                            "importance": {
                                "type": "number",
                                "minimum": 0,
                                "maximum": 1,
                                "description": "新的重要性分数",
                            },
                            "metadata": {
                                "type": "object",
                                "description": "要更新的元数据",
                            },
                        },
                        "required": ["memory_id"],
                    },
                ),
                Tool(
                    name="memory_delete",
                    description="删除指定的记忆",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "memory_id": {
                                "type": "string",
                                "description": "要删除的记忆ID",
                            },
                        },
                        "required": ["memory_id"],
                    },
                ),
                Tool(
                    name="memory_consolidate",
                    description="整合记忆，将短期记忆转化为长期记忆",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                    },
                ),
                Tool(
                    name="memory_stats",
                    description="获取记忆系统的统计信息",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                    },
                ),
            ]

        @self.server.call_tool()
        async def handle_call_tool(
            name: str, arguments: dict[str, Any] | None
        ) -> list[Content]:
            """处理工具调用。"""
            try:
                if name == "memory_store":
                    return await self._handle_memory_store(arguments or {})
                elif name == "memory_search":
                    return await self._handle_memory_search(arguments or {})
                elif name == "memory_get_recent":
                    return await self._handle_memory_get_recent(arguments or {})
                elif name == "memory_get_important":
                    return await self._handle_memory_get_important(arguments or {})
                elif name == "memory_update":
                    return await self._handle_memory_update(arguments or {})
                elif name == "memory_delete":
                    return await self._handle_memory_delete(arguments or {})
                elif name == "memory_consolidate":
                    return await self._handle_memory_consolidate()
                elif name == "memory_stats":
                    return await self._handle_memory_stats()
                else:
                    return [TextContent(type="text", text=f"未知的工具: {name}")]
            except Exception as e:
                logger.error(f"工具调用失败 {name}: {e}")
                return [TextContent(type="text", text=f"错误: {str(e)}")]

    async def _handle_memory_store(self, arguments: dict[str, Any]) -> list[Content]:
        """处理存储记忆请求。"""
        content = arguments.get("content", "")
        memory_type_str = arguments.get("memory_type", "short_term")
        importance = arguments.get("importance", 0.5)
        metadata = arguments.get("metadata", {})

        # 转换记忆类型
        memory_type = MemoryType(memory_type_str)

        # 存储记忆
        memory = await self.memory_manager.store_memory(
            content=content,
            memory_type=memory_type,
            importance=importance,
            metadata=metadata,
        )

        return [
            TextContent(
                type="text",
                text=f"记忆已存储: ID={memory.id}, 类型={memory.type.value}, 重要性={memory.importance}",
            )
        ]

    async def _handle_memory_search(self, arguments: dict[str, Any]) -> list[Content]:
        """处理搜索记忆请求。"""
        query_text = arguments.get("query", "")
        memory_types_str = arguments.get("memory_types")
        limit = arguments.get("limit", 10)
        min_importance = arguments.get("min_importance", 0.0)

        # 转换记忆类型
        memory_types = None
        if memory_types_str:
            memory_types = [MemoryType(t) for t in memory_types_str]

        # 创建查询
        query = MemoryQuery(
            query=query_text,
            memory_types=memory_types,
            limit=limit,
            min_importance=min_importance,
            time_range=None,  # 明确指定为None
        )

        # 搜索记忆
        results = await self.memory_manager.search_memories(query)

        # 格式化结果
        result_texts = []
        for result in results:
            memory = result.memory
            result_texts.append(
                f"- [{memory.id}] (相关性: {result.relevance_score:.2f}, "
                f"重要性: {memory.importance:.2f}, 类型: {memory.type.value})\n"
                f"  内容: {memory.content[:100]}..."
                if len(memory.content) > 100
                else memory.content
            )

        if result_texts:
            return [
                TextContent(
                    type="text",
                    text=f"找到 {len(results)} 条相关记忆:\n" + "\n".join(result_texts),
                )
            ]
        else:
            return [TextContent(type="text", text="没有找到相关记忆")]

    async def _handle_memory_get_recent(
        self, arguments: dict[str, Any]
    ) -> list[Content]:
        """处理获取最近记忆请求。"""
        limit = arguments.get("limit", 10)
        memory_types_str = arguments.get("memory_types")

        # 转换记忆类型
        memory_types = None
        if memory_types_str:
            memory_types = [MemoryType(t) for t in memory_types_str]

        # 获取最近记忆
        memories = await self.memory_manager.get_recent_memories(limit, memory_types)

        # 格式化结果
        result_texts = []
        for memory in memories:
            result_texts.append(
                f"- [{memory.id}] (重要性: {memory.importance:.2f}, "
                f"类型: {memory.type.value}, 时间: {memory.created_at.strftime('%Y-%m-%d %H:%M')})\n"
                f"  内容: {memory.content[:100]}..."
                if len(memory.content) > 100
                else memory.content
            )

        if result_texts:
            return [
                TextContent(
                    type="text",
                    text=f"最近的 {len(memories)} 条记忆:\n" + "\n".join(result_texts),
                )
            ]
        else:
            return [TextContent(type="text", text="没有记忆")]

    async def _handle_memory_get_important(
        self, arguments: dict[str, Any]
    ) -> list[Content]:
        """处理获取重要记忆请求。"""
        limit = arguments.get("limit", 10)
        min_importance = arguments.get("min_importance", 0.7)
        memory_types_str = arguments.get("memory_types")

        # 转换记忆类型
        memory_types = None
        if memory_types_str:
            memory_types = [MemoryType(t) for t in memory_types_str]

        # 获取重要记忆
        memories = await self.memory_manager.get_important_memories(
            limit, min_importance, memory_types
        )

        # 格式化结果
        result_texts = []
        for memory in memories:
            result_texts.append(
                f"- [{memory.id}] (重要性: {memory.importance:.2f}, "
                f"访问次数: {memory.access_count}, 类型: {memory.type.value})\n"
                f"  内容: {memory.content[:100]}..."
                if len(memory.content) > 100
                else memory.content
            )

        if result_texts:
            return [
                TextContent(
                    type="text",
                    text=f"重要记忆 (最小重要性: {min_importance}):\n"
                    + "\n".join(result_texts),
                )
            ]
        else:
            return [TextContent(type="text", text="没有找到重要记忆")]

    async def _handle_memory_update(self, arguments: dict[str, Any]) -> list[Content]:
        """处理更新记忆请求。"""
        memory_id = arguments.get("memory_id", "")
        content = arguments.get("content")
        importance = arguments.get("importance")
        metadata = arguments.get("metadata")

        # 更新记忆
        memory = await self.memory_manager.update_memory(
            memory_id, content, importance, metadata
        )

        if memory:
            return [
                TextContent(
                    type="text",
                    text=f"记忆已更新: ID={memory.id}, 更新时间={memory.updated_at.strftime('%Y-%m-%d %H:%M:%S')}",
                )
            ]
        else:
            return [TextContent(type="text", text=f"记忆 {memory_id} 不存在")]

    async def _handle_memory_delete(self, arguments: dict[str, Any]) -> list[Content]:
        """处理删除记忆请求。"""
        memory_id = arguments.get("memory_id", "")

        # 删除记忆
        success = await self.memory_manager.delete_memory(memory_id)

        if success:
            return [TextContent(type="text", text=f"记忆 {memory_id} 已删除")]
        else:
            return [TextContent(type="text", text=f"记忆 {memory_id} 不存在")]

    async def _handle_memory_consolidate(self) -> list[Content]:
        """处理整合记忆请求。"""
        await self.memory_manager.consolidate_memories()
        return [
            TextContent(
                type="text", text="记忆整合完成，短期记忆已根据规则转换为长期记忆"
            )
        ]

    async def _handle_memory_stats(self) -> list[Content]:
        """处理获取统计信息请求。"""
        stats = await self.memory_manager.get_memory_stats()

        stats_text = f"""记忆系统统计:
- 总记忆数: {stats.total_memories}
- 按类型统计: {json.dumps(stats.by_type, ensure_ascii=False)}
- 平均重要性: {stats.average_importance:.2f}
- 总访问次数: {stats.total_access_count}
- 内存使用: {stats.memory_usage_bytes / 1024:.2f} KB"""

        return [TextContent(type="text", text=stats_text)]

    async def run(self) -> None:
        """运行MCP服务器。"""
        from mcp.server.stdio import stdio_server

        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="memory-service",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )


# 用于直接运行的入口
if __name__ == "__main__":
    import asyncio

    server = MemoryMCPServer()
    asyncio.run(server.run())
