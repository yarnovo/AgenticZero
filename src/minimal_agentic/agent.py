"""最小化智能体实现。"""

import logging
from contextlib import asynccontextmanager
from typing import Any

from .config import AgentConfig
from .llm import LLMProvider, LLMResponse, create_llm_provider
from .mcp_client import DefaultMCPClient
from .mcp_interface import MCPClientInterface

logger = logging.getLogger(__name__)


class MinimalAgent:
    """最小化智能体实现，可以与 MCP 服务器和 LLM 交互。"""

    def __init__(
        self,
        config: AgentConfig | dict[str, Any],
        mcp_client: MCPClientInterface | None = None,
        llm_provider: LLMProvider | None = None,
    ) -> None:
        """初始化智能体。

        Args:
            config: 智能体配置
            mcp_client: MCP 客户端实例(可选,用于依赖注入)
            llm_provider: LLM 提供商实例(可选,用于依赖注入)
        """
        if isinstance(config, dict):
            config = AgentConfig.from_dict(config)

        self.config = config
        self.name = config.name
        self.instruction = config.instruction

        # 依赖注入或创建默认实例
        self.mcp_client = mcp_client or self._create_default_mcp_client()
        self.llm_provider = llm_provider or self._create_default_llm_provider()

        self.conversation_history: list[dict[str, str]] = []

        if config.debug:
            logging.basicConfig(level=logging.DEBUG)

    def _create_default_mcp_client(self) -> MCPClientInterface:
        """创建默认的 MCP 客户端。"""
        return DefaultMCPClient()

    def _create_default_llm_provider(self) -> LLMProvider:
        """创建默认的 LLM 提供商。"""
        return create_llm_provider(
            provider_type=self.config.llm_config.provider,
            api_key=self.config.llm_config.api_key,
            model=self.config.llm_config.model,
            temperature=self.config.llm_config.temperature,
            max_tokens=self.config.llm_config.max_tokens,
        )

    async def initialize(self) -> None:
        """初始化智能体，连接到 MCP 服务器。"""
        logger.info(f"正在初始化智能体: {self.name}")

        # 如果使用默认客户端，连接到所有配置的 MCP 服务器
        if isinstance(self.mcp_client, DefaultMCPClient):
            for server_name, server_config in self.config.mcp_servers.items():
                await self.mcp_client.add_server(server_name, server_config)
        else:
            # 对于自定义客户端，只调用初始化方法
            await self.mcp_client.initialize()

        # 添加系统指令到对话历史
        self.conversation_history.append(
            {"role": "system", "content": self.instruction},
        )

        logger.info(
            f"智能体 {self.name} 已初始化，配置了 {len(self.config.mcp_servers)} 个 MCP 服务器",
        )

    async def close(self) -> None:
        """关闭所有连接并清理资源。"""
        await self.mcp_client.close()
        logger.info(f"智能体 {self.name} 已关闭")

    @asynccontextmanager
    async def connect(self):  # type: ignore[misc]
        """智能体生命周期的上下文管理器。"""
        try:
            await self.initialize()
            yield self
        finally:
            await self.close()

    def _format_tools_for_llm(
        self,
        tools: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """为 LLM 格式化 MCP 工具。"""
        formatted_tools = []
        for tool in tools:
            formatted_tool = {
                "type": "function",
                "function": {
                    "name": tool["_namespaced_name"],
                    "description": tool.get("description", ""),
                    "parameters": tool.get("inputSchema", {}),
                },
            }
            formatted_tools.append(formatted_tool)
        return formatted_tools

    def _format_tool_result(self, result: dict[str, Any]) -> str:
        """格式化工具调用结果以供对话使用。"""
        if "content" in result:
            # 处理 MCP 内容格式
            content_items = result["content"]
            if isinstance(content_items, list):
                text_parts = []
                for item in content_items:
                    if isinstance(item, dict) and item.get("type") == "text":
                        text_parts.append(item.get("text", ""))
                return "\n".join(text_parts)
            return str(content_items)
        return str(result)

    async def run(self, user_input: str, max_iterations: int | None = None) -> str:
        """运行智能体处理用户输入，自动处理工具调用。

        Args:
            user_input: 用户输入消息
            max_iterations: 最大 LLM 迭代次数(覆盖配置)

        Returns:
            智能体的最终响应
        """
        max_iterations = max_iterations or self.config.max_iterations

        # 添加用户消息到历史
        self.conversation_history.append({"role": "user", "content": user_input})

        # 获取可用工具
        tools = await self.mcp_client.list_tools()
        formatted_tools = self._format_tools_for_llm(tools)

        iteration = 0
        final_response = ""

        while iteration < max_iterations:
            iteration += 1
            logger.debug(f"迭代 {iteration}/{max_iterations}")

            # 生成 LLM 响应
            llm_response: LLMResponse = await self.llm_provider.generate(
                messages=self.conversation_history,
                tools=formatted_tools if formatted_tools else None,
            )

            # 添加助手响应到历史
            self.conversation_history.append(
                {"role": "assistant", "content": llm_response.content},
            )

            final_response = llm_response.content

            # 检查是否有工具调用
            if not llm_response.has_tool_calls():
                logger.debug("未检测到工具调用，结束迭代")
                break

            # 执行工具调用
            tool_results = []
            for tool_call in llm_response.tool_calls:
                logger.info(f"调用工具: {tool_call.name}，参数: {tool_call.arguments}")

                try:
                    result = await self.mcp_client.call_tool(
                        tool_name=tool_call.name,
                        arguments=tool_call.arguments,
                    )

                    formatted_result = self._format_tool_result(result)
                    tool_results.append(
                        {"tool": tool_call.name, "result": formatted_result},
                    )

                    logger.debug(f"工具结果: {formatted_result}")

                except Exception as e:
                    error_msg = f"调用工具 {tool_call.name} 时出错: {e!s}"
                    logger.error(error_msg)
                    tool_results.append({"tool": tool_call.name, "error": error_msg})

            # 将工具结果添加到对话中
            if tool_results:
                tool_results_msg = "工具结果:\n"
                for tr in tool_results:
                    if "error" in tr:
                        tool_results_msg += f"- {tr['tool']}: 错误 - {tr['error']}\n"
                    else:
                        tool_results_msg += f"- {tr['tool']}: {tr['result']}\n"

                self.conversation_history.append(
                    {"role": "user", "content": tool_results_msg},
                )

        if iteration >= max_iterations:
            logger.warning(f"达到最大迭代次数 ({max_iterations})")

        return final_response

    def clear_history(self) -> None:
        """清除对话历史，保留系统指令。"""
        self.conversation_history = [{"role": "system", "content": self.instruction}]
        logger.debug("对话历史已清除")

    def get_history(self) -> list[dict[str, str]]:
        """获取当前对话历史。"""
        return self.conversation_history.copy()
