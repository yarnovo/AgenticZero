"""上下文管理器，负责管理对话历史、会话状态和上下文信息。"""

import json
import logging
from abc import ABC, abstractmethod
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class Message(BaseModel):
    """对话消息模型。"""

    role: str = Field(..., description="消息角色：system, user, assistant")
    content: str = Field(..., description="消息内容")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = Field(default_factory=dict, description="消息元数据")

    class Config:
        extra = "allow"


class ConversationContext(BaseModel):
    """对话上下文模型。"""

    conversation_id: str = Field(..., description="对话ID")
    messages: list[Message] = Field(default_factory=list, description="消息列表")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = Field(default_factory=dict, description="对话元数据")
    max_history_length: int = Field(default=1000, description="最大历史消息数量")

    class Config:
        extra = "allow"

    def add_message(
        self, role: str, content: str, metadata: dict[str, Any] | None = None
    ) -> None:
        """添加消息到对话历史。"""
        message = Message(role=role, content=content, metadata=metadata or {})
        self.messages.append(message)
        self.updated_at = datetime.now(UTC)

        # 限制历史长度
        if len(self.messages) > self.max_history_length:
            # 保留系统消息和最近的消息
            system_messages = [msg for msg in self.messages if msg.role == "system"]
            recent_messages = [msg for msg in self.messages if msg.role != "system"][
                -self.max_history_length + len(system_messages) :
            ]
            self.messages = system_messages + recent_messages

    def get_messages_for_llm(self) -> list[dict[str, str]]:
        """获取适用于 LLM 的消息格式。"""
        return [{"role": msg.role, "content": msg.content} for msg in self.messages]

    def clear_history(self, keep_system: bool = True) -> None:
        """清除对话历史。"""
        if keep_system:
            system_messages = [msg for msg in self.messages if msg.role == "system"]
            self.messages = system_messages
        else:
            self.messages = []
        self.updated_at = datetime.now(UTC)

    def get_message_count(self) -> int:
        """获取消息数量。"""
        return len(self.messages)

    def get_token_estimate(self) -> int:
        """估算消息的 token 数量（粗略估算）。"""
        total_chars = sum(len(msg.content) for msg in self.messages)
        return total_chars // 4  # 粗略估算：4个字符约等于1个token


class ContextManagerInterface(ABC):
    """上下文管理器抽象接口。"""

    @abstractmethod
    async def create_context(
        self, conversation_id: str, system_instruction: str | None = None
    ) -> ConversationContext:
        """创建新的对话上下文。

        Args:
            conversation_id: 对话ID
            system_instruction: 系统指令

        Returns:
            对话上下文对象
        """

    @abstractmethod
    async def get_context(self, conversation_id: str) -> ConversationContext | None:
        """获取对话上下文。

        Args:
            conversation_id: 对话ID

        Returns:
            对话上下文对象，如果不存在则返回None
        """

    @abstractmethod
    async def update_context(self, context: ConversationContext) -> None:
        """更新对话上下文。

        Args:
            context: 对话上下文对象
        """

    @abstractmethod
    async def delete_context(self, conversation_id: str) -> None:
        """删除对话上下文。

        Args:
            conversation_id: 对话ID
        """

    @abstractmethod
    async def list_contexts(self) -> list[str]:
        """列出所有对话ID。

        Returns:
            对话ID列表
        """


class InMemoryContextManager(ContextManagerInterface):
    """基于内存的上下文管理器实现。"""

    def __init__(self):
        self.contexts: dict[str, ConversationContext] = {}

    async def create_context(
        self, conversation_id: str, system_instruction: str | None = None
    ) -> ConversationContext:
        """创建新的对话上下文。"""
        if conversation_id in self.contexts:
            logger.warning(f"对话上下文 {conversation_id} 已存在，将被覆盖")

        context = ConversationContext(conversation_id=conversation_id)

        if system_instruction:
            context.add_message("system", system_instruction)

        self.contexts[conversation_id] = context
        logger.info(f"创建对话上下文 {conversation_id}")
        return context

    async def get_context(self, conversation_id: str) -> ConversationContext | None:
        """获取对话上下文。"""
        return self.contexts.get(conversation_id)

    async def update_context(self, context: ConversationContext) -> None:
        """更新对话上下文。"""
        context.updated_at = datetime.now(UTC)
        self.contexts[context.conversation_id] = context

    async def delete_context(self, conversation_id: str) -> None:
        """删除对话上下文。"""
        if conversation_id in self.contexts:
            del self.contexts[conversation_id]
            logger.info(f"删除对话上下文 {conversation_id}")

    async def list_contexts(self) -> list[str]:
        """列出所有对话ID。"""
        return list(self.contexts.keys())


class PersistentContextManager(ContextManagerInterface):
    """支持持久化的上下文管理器。"""

    def __init__(self, storage_path: str):
        self.storage_path = storage_path
        self.contexts: dict[str, ConversationContext] = {}
        self._load_contexts()

    def _load_contexts(self) -> None:
        """从存储加载上下文。"""
        try:
            import os

            if os.path.exists(self.storage_path):
                with open(self.storage_path, encoding="utf-8") as f:
                    data = json.load(f)
                    for conv_id, context_data in data.items():
                        self.contexts[conv_id] = ConversationContext(**context_data)
                logger.info(
                    f"从 {self.storage_path} 加载了 {len(self.contexts)} 个对话上下文"
                )
        except Exception as e:
            logger.error(f"加载上下文时出错: {e}")

    def _save_contexts(self) -> None:
        """保存上下文到存储。"""
        try:
            import os

            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            data = {
                conv_id: context.dict() for conv_id, context in self.contexts.items()
            }
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
            logger.debug(
                f"保存了 {len(self.contexts)} 个对话上下文到 {self.storage_path}"
            )
        except Exception as e:
            logger.error(f"保存上下文时出错: {e}")

    async def create_context(
        self, conversation_id: str, system_instruction: str | None = None
    ) -> ConversationContext:
        """创建新的对话上下文。"""
        context = ConversationContext(conversation_id=conversation_id)

        if system_instruction:
            context.add_message("system", system_instruction)

        self.contexts[conversation_id] = context
        self._save_contexts()
        logger.info(f"创建并保存对话上下文 {conversation_id}")
        return context

    async def get_context(self, conversation_id: str) -> ConversationContext | None:
        """获取对话上下文。"""
        return self.contexts.get(conversation_id)

    async def update_context(self, context: ConversationContext) -> None:
        """更新对话上下文。"""
        context.updated_at = datetime.now(UTC)
        self.contexts[context.conversation_id] = context
        self._save_contexts()

    async def delete_context(self, conversation_id: str) -> None:
        """删除对话上下文。"""
        if conversation_id in self.contexts:
            del self.contexts[conversation_id]
            self._save_contexts()
            logger.info(f"删除对话上下文 {conversation_id}")

    async def list_contexts(self) -> list[str]:
        """列出所有对话ID。"""
        return list(self.contexts.keys())


class ContextManager:
    """上下文管理器工厂和便捷接口。"""

    @staticmethod
    def create_memory_manager() -> InMemoryContextManager:
        """创建内存管理器。"""
        return InMemoryContextManager()

    @staticmethod
    def create_persistent_manager(storage_path: str) -> PersistentContextManager:
        """创建持久化管理器。"""
        return PersistentContextManager(storage_path)
