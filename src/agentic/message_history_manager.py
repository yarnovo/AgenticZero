"""历史消息记录管理模块，负责管理对话历史的存储和检索。"""

import json
import logging
from abc import ABC, abstractmethod
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class Message(BaseModel):
    """消息模型。"""

    role: str = Field(..., description="消息角色：system, user, assistant, tool")
    content: str = Field(..., description="消息内容")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = Field(default_factory=dict, description="消息元数据")

    class Config:
        extra = "allow"


class MessageHistory(BaseModel):
    """消息历史模型。"""

    conversation_id: str = Field(..., description="对话ID")
    messages: list[Message] = Field(default_factory=list, description="消息列表")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    max_messages: int = Field(default=1000, description="最大消息数量")

    class Config:
        extra = "allow"

    def add_message(
        self,
        role: str,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """添加消息到历史记录。

        Args:
            role: 消息角色
            content: 消息内容
            metadata: 消息元数据
        """
        message = Message(role=role, content=content, metadata=metadata or {})
        self.messages.append(message)
        self.updated_at = datetime.now(UTC)

        # 限制消息数量，保留系统消息
        if len(self.messages) > self.max_messages:
            system_messages = [msg for msg in self.messages if msg.role == "system"]
            other_messages = [msg for msg in self.messages if msg.role != "system"]

            # 保留最近的消息
            keep_count = self.max_messages - len(system_messages)
            if keep_count > 0:
                other_messages = other_messages[-keep_count:]

            self.messages = system_messages + other_messages

    def get_messages_for_llm(self) -> list[dict[str, str]]:
        """获取适用于LLM的消息格式。

        Returns:
            消息列表，包含role和content字段
        """
        return [{"role": msg.role, "content": msg.content} for msg in self.messages]

    def clear_messages(self, keep_system: bool = True) -> None:
        """清除消息历史。

        Args:
            keep_system: 是否保留系统消息
        """
        if keep_system:
            self.messages = [msg for msg in self.messages if msg.role == "system"]
        else:
            self.messages = []
        self.updated_at = datetime.now(UTC)

    def get_message_count(self) -> int:
        """获取消息数量。"""
        return len(self.messages)

    def get_token_estimate(self) -> int:
        """估算消息的token数量（粗略估算）。"""
        total_chars = sum(len(msg.content) for msg in self.messages)
        return total_chars // 4  # 粗略估算：4个字符约等于1个token


class MessageHistoryManagerInterface(ABC):
    """消息历史管理器抽象接口。"""

    @abstractmethod
    async def create_history(self, conversation_id: str) -> MessageHistory:
        """创建新的消息历史。

        Args:
            conversation_id: 对话ID

        Returns:
            消息历史对象
        """

    @abstractmethod
    async def get_history(self, conversation_id: str) -> MessageHistory | None:
        """获取消息历史。

        Args:
            conversation_id: 对话ID

        Returns:
            消息历史对象，如果不存在则返回None
        """

    @abstractmethod
    async def save_history(self, history: MessageHistory) -> None:
        """保存消息历史。

        Args:
            history: 消息历史对象
        """

    @abstractmethod
    async def delete_history(self, conversation_id: str) -> None:
        """删除消息历史。

        Args:
            conversation_id: 对话ID
        """

    @abstractmethod
    async def list_conversations(self) -> list[str]:
        """列出所有对话ID。

        Returns:
            对话ID列表
        """


class InMemoryMessageHistoryManager(MessageHistoryManagerInterface):
    """基于内存的消息历史管理器。"""

    def __init__(self):
        """初始化内存消息历史管理器。"""
        self.histories: dict[str, MessageHistory] = {}

    async def create_history(self, conversation_id: str) -> MessageHistory:
        """创建新的消息历史。"""
        if conversation_id in self.histories:
            logger.warning(f"对话历史 {conversation_id} 已存在，将被覆盖")

        history = MessageHistory(conversation_id=conversation_id)
        self.histories[conversation_id] = history
        logger.info(f"创建消息历史 {conversation_id}")
        return history

    async def get_history(self, conversation_id: str) -> MessageHistory | None:
        """获取消息历史。"""
        return self.histories.get(conversation_id)

    async def save_history(self, history: MessageHistory) -> None:
        """保存消息历史。"""
        history.updated_at = datetime.now(UTC)
        self.histories[history.conversation_id] = history
        logger.debug(f"保存消息历史 {history.conversation_id}")

    async def delete_history(self, conversation_id: str) -> None:
        """删除消息历史。"""
        if conversation_id in self.histories:
            del self.histories[conversation_id]
            logger.info(f"删除消息历史 {conversation_id}")

    async def list_conversations(self) -> list[str]:
        """列出所有对话ID。"""
        return list(self.histories.keys())


class FileMessageHistoryManager(MessageHistoryManagerInterface):
    """基于文件的消息历史管理器。"""

    def __init__(self, storage_dir: str):
        """初始化文件消息历史管理器。

        Args:
            storage_dir: 存储目录路径
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._cache: dict[str, MessageHistory] = {}

    def _get_file_path(self, conversation_id: str) -> Path:
        """获取对话文件路径。

        Args:
            conversation_id: 对话ID

        Returns:
            文件路径
        """
        safe_id = conversation_id.replace("/", "_").replace("\\", "_")
        return self.storage_dir / f"{safe_id}.json"

    async def create_history(self, conversation_id: str) -> MessageHistory:
        """创建新的消息历史。"""
        history = MessageHistory(conversation_id=conversation_id)
        await self.save_history(history)
        logger.info(f"创建消息历史 {conversation_id}")
        return history

    async def get_history(self, conversation_id: str) -> MessageHistory | None:
        """获取消息历史。"""
        # 先检查缓存
        if conversation_id in self._cache:
            return self._cache[conversation_id]

        # 从文件加载
        file_path = self._get_file_path(conversation_id)
        if not file_path.exists():
            return None

        try:
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)
                history = MessageHistory(**data)
                self._cache[conversation_id] = history
                return history
        except Exception as e:
            logger.error(f"加载消息历史 {conversation_id} 失败: {e}")
            return None

    async def save_history(self, history: MessageHistory) -> None:
        """保存消息历史。"""
        history.updated_at = datetime.now(UTC)
        file_path = self._get_file_path(history.conversation_id)

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(history.dict(), f, ensure_ascii=False, indent=2, default=str)

            # 更新缓存
            self._cache[history.conversation_id] = history
            logger.debug(f"保存消息历史 {history.conversation_id}")
        except Exception as e:
            logger.error(f"保存消息历史 {history.conversation_id} 失败: {e}")
            raise

    async def delete_history(self, conversation_id: str) -> None:
        """删除消息历史。"""
        file_path = self._get_file_path(conversation_id)

        try:
            if file_path.exists():
                file_path.unlink()

            # 从缓存中删除
            if conversation_id in self._cache:
                del self._cache[conversation_id]

            logger.info(f"删除消息历史 {conversation_id}")
        except Exception as e:
            logger.error(f"删除消息历史 {conversation_id} 失败: {e}")
            raise

    async def list_conversations(self) -> list[str]:
        """列出所有对话ID。"""
        try:
            conversation_ids = []
            for file_path in self.storage_dir.glob("*.json"):
                # 从文件名恢复对话ID
                conversation_id = file_path.stem
                conversation_ids.append(conversation_id)
            return conversation_ids
        except Exception as e:
            logger.error(f"列出对话ID失败: {e}")
            return []


class MessageHistoryManager:
    """消息历史管理器工厂类。"""

    @staticmethod
    def create_memory_manager() -> InMemoryMessageHistoryManager:
        """创建内存管理器。

        Returns:
            内存消息历史管理器
        """
        return InMemoryMessageHistoryManager()

    @staticmethod
    def create_file_manager(storage_dir: str) -> FileMessageHistoryManager:
        """创建文件管理器。

        Args:
            storage_dir: 存储目录路径

        Returns:
            文件消息历史管理器
        """
        return FileMessageHistoryManager(storage_dir)
