"""自驱动核心程序，负责协调各个组件实现智能体的自主决策和执行。"""

import json
import logging
import re
from typing import Any

from .llm_session_manager import LLMSessionManager
from .mcp_session_manager import MCPSessionManager
from .session_context_manager import SessionContextManager

logger = logging.getLogger(__name__)


class ToolCall:
    """工具调用模型。"""

    def __init__(self, name: str, arguments: dict[str, Any] | None = None):
        """初始化工具调用。

        Args:
            name: 工具名称
            arguments: 工具参数
        """
        self.name = name
        self.arguments = arguments or {}

    def __repr__(self) -> str:
        return f"ToolCall(name='{self.name}', arguments={self.arguments})"


class LLMResponse:
    """LLM响应模型。"""

    def __init__(self, content: str, tool_calls: list[ToolCall] | None = None):
        """初始化LLM响应。

        Args:
            content: 响应内容
            tool_calls: 工具调用列表
        """
        self.content = content
        self.tool_calls = tool_calls or []

    def has_tool_calls(self) -> bool:
        """检查是否包含工具调用。"""
        return len(self.tool_calls) > 0

    def __repr__(self) -> str:
        return f"LLMResponse(content='{self.content[:50]}...', tool_calls={len(self.tool_calls)})"


class CoreEngine:
    """自驱动核心程序，协调所有组件实现智能体的自主行为。"""

    def __init__(
        self,
        llm_session_manager: LLMSessionManager,
        mcp_session_manager: MCPSessionManager,
        context_manager: SessionContextManager,
        max_iterations: int = 10,
    ):
        """初始化核心引擎。

        Args:
            llm_session_manager: 大模型会话管理器
            mcp_session_manager: MCP会话管理器
            context_manager: 会话上下文管理器
            max_iterations: 最大迭代次数
        """
        self.llm_session_manager = llm_session_manager
        self.mcp_session_manager = mcp_session_manager
        self.context_manager = context_manager
        self.max_iterations = max_iterations
        self._initialized = False

    async def initialize(self) -> None:
        """初始化核心引擎。"""
        if self._initialized:
            return

        await self.llm_session_manager.initialize()
        logger.info("核心引擎已初始化")
        self._initialized = True

    async def close(self) -> None:
        """关闭核心引擎。"""
        await self.llm_session_manager.close()
        await self.mcp_session_manager.close_all()
        await self.context_manager.save_all_contexts()
        self._initialized = False
        logger.info("核心引擎已关闭")

    async def process_input(
        self,
        user_input: str,
        conversation_id: str,
        max_iterations: int | None = None,
    ) -> str:
        """处理用户输入，自驱动执行直到完成。

        Args:
            user_input: 用户输入
            conversation_id: 对话ID
            max_iterations: 最大迭代次数（覆盖默认值）

        Returns:
            最终响应

        Raises:
            RuntimeError: 引擎未初始化时抛出
        """
        if not self._initialized:
            raise RuntimeError("核心引擎未初始化，请先调用 initialize() 方法")

        max_iterations = max_iterations or self.max_iterations
        logger.info(
            f"开始处理用户输入，对话ID: {conversation_id}，最大迭代: {max_iterations}"
        )

        # 获取或创建会话上下文
        context = await self.context_manager.get_context(conversation_id)
        if not context:
            context = await self.context_manager.create_context(conversation_id)

        # 添加用户消息到上下文
        context.add_message("user", user_input)

        # 获取可用工具
        available_tools = await self.mcp_session_manager.list_all_tools()
        formatted_tools = self._format_tools_for_llm(available_tools)

        # 自驱动循环
        iteration = 0
        final_response = ""

        while iteration < max_iterations:
            iteration += 1
            logger.debug(f"自驱动迭代 {iteration}/{max_iterations}")

            # 获取当前上下文消息
            messages = context.get_current_messages()

            # 调用大模型
            llm_response = await self._call_llm(messages, formatted_tools)

            # 添加助手响应到上下文
            context.add_message("assistant", llm_response.content)
            final_response = llm_response.content

            # 检查是否有工具调用
            if not llm_response.has_tool_calls():
                logger.debug("无工具调用，自驱动结束")
                break

            # 执行工具调用
            tool_results = await self._execute_tool_calls(llm_response.tool_calls)

            # 将工具结果添加到上下文
            if tool_results:
                tool_results_message = self._format_tool_results(tool_results)
                context.add_message("tool", tool_results_message)

        if iteration >= max_iterations:
            logger.warning(f"达到最大迭代次数 ({max_iterations})")

        # 保存上下文
        await self.context_manager.update_context(context)

        logger.info(f"处理完成，共执行 {iteration} 次迭代")
        return final_response

    async def _call_llm(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
    ) -> LLMResponse:
        """调用大模型。

        Args:
            messages: 消息列表
            tools: 可用工具列表

        Returns:
            LLM响应对象
        """
        logger.debug(f"调用大模型，消息数: {len(messages)}")

        # 调用大模型会话管理器
        response = await self.llm_session_manager.chat(messages, tools)

        # 解析响应
        content = response.get("content", "")
        tool_calls = self._parse_tool_calls(response)

        return LLMResponse(content, tool_calls)

    def _parse_tool_calls(self, llm_response: dict[str, Any]) -> list[ToolCall]:
        """解析LLM响应中的工具调用。

        Args:
            llm_response: LLM原始响应

        Returns:
            工具调用列表
        """
        tool_calls = []

        # 检查是否有标准的tool_calls字段
        if "tool_calls" in llm_response and llm_response["tool_calls"]:
            for tc in llm_response["tool_calls"]:
                if tc.get("type") == "function":
                    function = tc.get("function", {})
                    name = function.get("name", "")
                    arguments_str = function.get("arguments", "{}")

                    try:
                        arguments = (
                            json.loads(arguments_str)
                            if isinstance(arguments_str, str)
                            else arguments_str
                        )
                    except json.JSONDecodeError:
                        logger.warning(f"无法解析工具参数: {arguments_str}")
                        arguments = {}

                    tool_calls.append(ToolCall(name, arguments))

        # 如果没有标准格式，尝试从内容中解析（备用方案）
        if not tool_calls:
            content = llm_response.get("content", "")
            parsed_calls = self._parse_tool_calls_from_content(content)
            tool_calls.extend(parsed_calls)

        return tool_calls

    def _parse_tool_calls_from_content(self, content: str) -> list[ToolCall]:
        """从内容中解析工具调用（备用解析方案）。

        Args:
            content: 响应内容

        Returns:
            工具调用列表
        """
        tool_calls = []

        # 使用正则表达式匹配工具调用模式
        # 匹配类似：tool_name(arg1="value1", arg2="value2") 的模式
        pattern = r"(\w+)\((.*?)\)"
        matches = re.findall(pattern, content)

        for tool_name, args_str in matches:
            try:
                # 尝试解析参数
                if args_str.strip():
                    # 简单的参数解析（这里可以根据需要改进）
                    arguments = {}
                    # 这是一个简化的解析，实际使用中可能需要更复杂的逻辑
                    logger.debug(f"从内容解析到可能的工具调用: {tool_name}")
                else:
                    arguments = {}

                tool_calls.append(ToolCall(tool_name, arguments))
            except Exception as e:
                logger.warning(f"解析工具调用失败: {tool_name}, {e}")

        return tool_calls

    async def _execute_tool_calls(
        self, tool_calls: list[ToolCall]
    ) -> list[dict[str, Any]]:
        """执行工具调用。

        Args:
            tool_calls: 工具调用列表

        Returns:
            工具执行结果列表
        """
        results = []

        for tool_call in tool_calls:
            logger.info(f"执行工具调用: {tool_call.name}，参数: {tool_call.arguments}")

            try:
                result = await self.mcp_session_manager.call_tool(
                    tool_call.name, tool_call.arguments
                )
                results.append(
                    {"tool": tool_call.name, "success": True, "result": result}
                )
                logger.debug(f"工具 {tool_call.name} 执行成功")

            except Exception as e:
                error_msg = f"工具 {tool_call.name} 执行失败: {e}"
                logger.error(error_msg)
                results.append(
                    {"tool": tool_call.name, "success": False, "error": str(e)}
                )

        return results

    def _format_tools_for_llm(
        self, tools: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """为LLM格式化工具列表。

        Args:
            tools: 原始工具列表

        Returns:
            格式化后的工具列表
        """
        formatted_tools = []

        for tool in tools:
            formatted_tool = {
                "type": "function",
                "function": {
                    "name": tool.get("_namespaced_name", tool.get("name", "unknown")),
                    "description": tool.get("description", ""),
                    "parameters": tool.get("inputSchema", {}),
                },
            }
            formatted_tools.append(formatted_tool)

        logger.debug(f"格式化 {len(formatted_tools)} 个工具供LLM使用")
        return formatted_tools

    def _format_tool_results(self, results: list[dict[str, Any]]) -> str:
        """格式化工具执行结果。

        Args:
            results: 工具执行结果列表

        Returns:
            格式化后的结果字符串
        """
        formatted_results = []

        for result in results:
            tool_name = result["tool"]
            if result["success"]:
                # 格式化成功结果
                tool_result = result["result"]
                if isinstance(tool_result, dict) and "content" in tool_result:
                    # 处理MCP标准内容格式
                    content_items = tool_result["content"]
                    if isinstance(content_items, list):
                        text_parts = []
                        for item in content_items:
                            if isinstance(item, dict) and item.get("type") == "text":
                                text_parts.append(item.get("text", ""))
                        result_text = "\n".join(text_parts)
                    else:
                        result_text = str(content_items)
                else:
                    result_text = str(tool_result)

                formatted_results.append(f"工具 {tool_name} 执行成功:\n{result_text}")
            else:
                # 格式化错误结果
                error_msg = result["error"]
                formatted_results.append(f"工具 {tool_name} 执行失败: {error_msg}")

        return "\n\n".join(formatted_results)

    async def get_engine_status(self) -> dict[str, Any]:
        """获取引擎状态信息。

        Returns:
            状态信息字典
        """
        llm_status = {"initialized": self.llm_session_manager.is_initialized}

        mcp_status = await self.mcp_session_manager.get_server_status()
        context_stats = self.context_manager.get_current_context_stats()

        return {
            "initialized": self._initialized,
            "max_iterations": self.max_iterations,
            "llm_session": llm_status,
            "mcp_sessions": mcp_status,
            "contexts": context_stats,
        }
