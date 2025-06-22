"""当前会话上下文管理模块，负责管理当前会话的上下文状态。"""

import logging
from typing import Any

from .message_history_manager import MessageHistory, MessageHistoryManagerInterface

logger = logging.getLogger(__name__)


class SessionContext:
    """会话上下文，封装当前会话的状态信息。"""

    def __init__(
        self,
        conversation_id: str,
        system_instruction: str | None = None,
        max_context_length: int = 8000,
    ):
        """初始化会话上下文。

        Args:
            conversation_id: 对话ID
            system_instruction: 系统指令
            max_context_length: 最大上下文长度（token数）
        """
        self.conversation_id = conversation_id
        self.system_instruction = system_instruction
        self.max_context_length = max_context_length
        self.message_history: MessageHistory | None = None
        self.metadata: dict[str, Any] = {}

    def set_message_history(self, history: MessageHistory) -> None:
        """设置消息历史。

        Args:
            history: 消息历史对象
        """
        self.message_history = history

    def get_current_messages(self) -> list[dict[str, str]]:
        """获取当前会话的消息列表。

        Returns:
            消息列表，适用于LLM
        """
        if not self.message_history:
            messages = []
            if self.system_instruction:
                messages.append({"role": "system", "content": self.system_instruction})
            return messages

        messages = self.message_history.get_messages_for_llm()

        # 检查是否需要截断上下文
        if self._estimate_context_length(messages) > self.max_context_length:
            messages = self._truncate_context(messages)

        return messages

    def add_message(
        self,
        role: str,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """添加消息到当前上下文。

        Args:
            role: 消息角色
            content: 消息内容
            metadata: 消息元数据
        """
        if not self.message_history:
            logger.warning("消息历史未设置，无法添加消息")
            return

        self.message_history.add_message(role, content, metadata)

    def clear_history(self, keep_system: bool = True) -> None:
        """清除消息历史。

        Args:
            keep_system: 是否保留系统消息
        """
        if self.message_history:
            self.message_history.clear_messages(keep_system)

    def get_message_count(self) -> int:
        """获取消息数量。"""
        if not self.message_history:
            return 0
        return self.message_history.get_message_count()

    def get_token_estimate(self) -> int:
        """获取当前上下文的token估算。"""
        if not self.message_history:
            return 0
        return self.message_history.get_token_estimate()

    def set_metadata(self, key: str, value: Any) -> None:
        """设置上下文元数据。

        Args:
            key: 元数据键
            value: 元数据值
        """
        self.metadata[key] = value

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """获取上下文元数据。

        Args:
            key: 元数据键
            default: 默认值

        Returns:
            元数据值
        """
        return self.metadata.get(key, default)

    def _estimate_context_length(self, messages: list[dict[str, str]]) -> int:
        """估算上下文长度。

        Args:
            messages: 消息列表

        Returns:
            估算的token数
        """
        total_chars = sum(len(msg["content"]) for msg in messages)
        return total_chars // 4  # 粗略估算

    def _truncate_context(self, messages: list[dict[str, str]]) -> list[dict[str, str]]:
        """截断上下文以适应长度限制。

        Args:
            messages: 原始消息列表

        Returns:
            截断后的消息列表
        """
        # 保留系统消息
        system_messages = [msg for msg in messages if msg["role"] == "system"]
        other_messages = [msg for msg in messages if msg["role"] != "system"]

        # 从最新消息开始保留
        truncated_messages = system_messages.copy()
        current_length = self._estimate_context_length(system_messages)

        for msg in reversed(other_messages):
            msg_length = self._estimate_context_length([msg])
            if current_length + msg_length > self.max_context_length:
                break
            truncated_messages.insert(
                -len(system_messages) if system_messages else 0, msg
            )
            current_length += msg_length

        logger.info(
            f"上下文截断：从 {len(messages)} 条消息截断为 {len(truncated_messages)} 条"
        )
        return truncated_messages


class SessionContextManager:
    """会话上下文管理器，协调消息历史管理器和当前会话状态。"""

    def __init__(self, history_manager: MessageHistoryManagerInterface):
        """初始化会话上下文管理器。

        Args:
            history_manager: 消息历史管理器
        """
        self.history_manager = history_manager
        self.current_contexts: dict[str, SessionContext] = {}

    async def create_context(
        self,
        conversation_id: str,
        system_instruction: str | None = None,
        max_context_length: int = 8000,
    ) -> SessionContext:
        """创建新的会话上下文。

        Args:
            conversation_id: 对话ID
            system_instruction: 系统指令
            max_context_length: 最大上下文长度

        Returns:
            会话上下文对象
        """
        # 创建或获取消息历史
        history = await self.history_manager.get_history(conversation_id)
        if not history:
            history = await self.history_manager.create_history(conversation_id)
            if system_instruction:
                history.add_message("system", system_instruction)

        # 创建会话上下文
        context = SessionContext(
            conversation_id, system_instruction, max_context_length
        )
        context.set_message_history(history)

        self.current_contexts[conversation_id] = context
        logger.info(f"创建会话上下文 {conversation_id}")
        return context

    async def get_context(self, conversation_id: str) -> SessionContext | None:
        """获取会话上下文。

        Args:
            conversation_id: 对话ID

        Returns:
            会话上下文对象，如果不存在则返回None
        """
        # 先检查当前上下文
        if conversation_id in self.current_contexts:
            return self.current_contexts[conversation_id]

        # 尝试从历史记录加载
        history = await self.history_manager.get_history(conversation_id)
        if not history:
            return None

        # 创建上下文
        context = SessionContext(conversation_id)
        context.set_message_history(history)
        self.current_contexts[conversation_id] = context
        return context

    async def update_context(self, context: SessionContext) -> None:
        """更新会话上下文。

        Args:
            context: 会话上下文对象
        """
        if context.message_history:
            await self.history_manager.save_history(context.message_history)

        self.current_contexts[context.conversation_id] = context
        logger.debug(f"更新会话上下文 {context.conversation_id}")

    async def delete_context(self, conversation_id: str) -> None:
        """删除会话上下文。

        Args:
            conversation_id: 对话ID
        """
        # 删除历史记录
        await self.history_manager.delete_history(conversation_id)

        # 删除当前上下文
        if conversation_id in self.current_contexts:
            del self.current_contexts[conversation_id]

        logger.info(f"删除会话上下文 {conversation_id}")

    async def list_contexts(self) -> list[str]:
        """列出所有会话上下文ID。

        Returns:
            会话ID列表
        """
        return await self.history_manager.list_conversations()

    async def save_all_contexts(self) -> None:
        """保存所有当前会话上下文。"""
        for context in self.current_contexts.values():
            await self.update_context(context)
        logger.info("保存所有会话上下文")

    def get_current_context_stats(self) -> dict[str, Any]:
        """获取当前会话上下文统计信息。

        Returns:
            统计信息字典
        """
        stats = {"active_contexts": len(self.current_contexts), "contexts": {}}

        for conv_id, context in self.current_contexts.items():
            stats["contexts"][conv_id] = {
                "message_count": context.get_message_count(),
                "token_estimate": context.get_token_estimate(),
                "max_context_length": context.max_context_length,
            }

        return stats
