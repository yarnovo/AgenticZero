"""记忆管理模块，负责管理智能体的长期记忆和短期记忆。"""

import json
import logging
from abc import ABC, abstractmethod
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class MemoryType(Enum):
    """记忆类型枚举。"""

    SHORT_TERM = "short_term"  # 短期记忆
    LONG_TERM = "long_term"  # 长期记忆
    EPISODIC = "episodic"  # 情景记忆
    SEMANTIC = "semantic"  # 语义记忆


class MemoryItem(BaseModel):
    """记忆项模型。"""

    id: str = Field(..., description="记忆ID")
    type: MemoryType = Field(..., description="记忆类型")
    content: str = Field(..., description="记忆内容")
    embedding: list[float] | None = Field(None, description="向量嵌入")
    metadata: dict[str, Any] = Field(default_factory=dict, description="元数据")
    importance: float = Field(default=0.5, description="重要性分数 0-1")
    access_count: int = Field(default=0, description="访问次数")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    last_accessed_at: datetime | None = Field(None, description="最后访问时间")

    def access(self) -> None:
        """记录访问。"""
        self.access_count += 1
        self.last_accessed_at = datetime.now(UTC)

    class Config:
        extra = "allow"


class MemoryQuery(BaseModel):
    """记忆查询模型。"""

    query: str = Field(..., description="查询文本")
    memory_types: list[MemoryType] | None = Field(None, description="限定的记忆类型")
    limit: int = Field(default=10, description="返回数量限制")
    min_importance: float = Field(default=0.0, description="最小重要性阈值")
    time_range: tuple[datetime | None, datetime | None] | None = Field(
        None, description="时间范围"
    )


class MemorySearchResult(BaseModel):
    """记忆搜索结果。"""

    memory: MemoryItem = Field(..., description="记忆项")
    relevance_score: float = Field(..., description="相关性分数")
    metadata: dict[str, Any] = Field(default_factory=dict, description="搜索元数据")


class MemoryStats(BaseModel):
    """记忆统计信息。"""

    total_memories: int = Field(..., description="总记忆数")
    by_type: dict[str, int] = Field(..., description="按类型统计")
    average_importance: float = Field(..., description="平均重要性")
    total_access_count: int = Field(..., description="总访问次数")
    memory_usage_bytes: int = Field(0, description="内存使用量")


class MemoryManagerInterface(ABC):
    """记忆管理器抽象接口。"""

    @abstractmethod
    async def store_memory(
        self,
        content: str,
        memory_type: MemoryType,
        importance: float = 0.5,
        metadata: dict[str, Any] | None = None,
    ) -> MemoryItem:
        """存储记忆。

        Args:
            content: 记忆内容
            memory_type: 记忆类型
            importance: 重要性分数
            metadata: 元数据

        Returns:
            记忆项
        """

    @abstractmethod
    async def search_memories(self, query: MemoryQuery) -> list[MemorySearchResult]:
        """搜索记忆。

        Args:
            query: 查询条件

        Returns:
            搜索结果列表
        """

    @abstractmethod
    async def get_memory(self, memory_id: str) -> MemoryItem | None:
        """获取指定记忆。

        Args:
            memory_id: 记忆ID

        Returns:
            记忆项，如果不存在则返回None
        """

    @abstractmethod
    async def update_memory(
        self,
        memory_id: str,
        content: str | None = None,
        importance: float | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> MemoryItem | None:
        """更新记忆。

        Args:
            memory_id: 记忆ID
            content: 新内容
            importance: 新重要性分数
            metadata: 新元数据

        Returns:
            更新后的记忆项
        """

    @abstractmethod
    async def delete_memory(self, memory_id: str) -> bool:
        """删除记忆。

        Args:
            memory_id: 记忆ID

        Returns:
            是否删除成功
        """

    @abstractmethod
    async def get_recent_memories(
        self,
        limit: int = 10,
        memory_types: list[MemoryType] | None = None,
    ) -> list[MemoryItem]:
        """获取最近的记忆。

        Args:
            limit: 数量限制
            memory_types: 记忆类型筛选

        Returns:
            记忆项列表
        """

    @abstractmethod
    async def get_important_memories(
        self,
        limit: int = 10,
        min_importance: float = 0.7,
        memory_types: list[MemoryType] | None = None,
    ) -> list[MemoryItem]:
        """获取重要记忆。

        Args:
            limit: 数量限制
            min_importance: 最小重要性阈值
            memory_types: 记忆类型筛选

        Returns:
            记忆项列表
        """

    @abstractmethod
    async def consolidate_memories(self) -> None:
        """整合记忆，将短期记忆转化为长期记忆。"""

    @abstractmethod
    async def forget_memories(
        self,
        threshold_date: datetime | None = None,
        max_memories: int | None = None,
    ) -> int:
        """遗忘记忆。

        Args:
            threshold_date: 时间阈值，删除此日期之前的记忆
            max_memories: 最大记忆数，超出则删除旧记忆

        Returns:
            删除的记忆数量
        """

    @abstractmethod
    async def get_memory_stats(self) -> MemoryStats:
        """获取记忆统计信息。

        Returns:
            统计信息
        """

    @abstractmethod
    async def clear_all_memories(self) -> None:
        """清除所有记忆。"""


class InMemoryMemoryManager(MemoryManagerInterface):
    """基于内存的记忆管理器实现。"""

    def __init__(self):
        """初始化内存记忆管理器。"""
        self.memories: dict[str, MemoryItem] = {}
        self._next_id = 1

    def _generate_id(self) -> str:
        """生成记忆ID。"""
        memory_id = f"mem_{self._next_id}"
        self._next_id += 1
        return memory_id

    async def store_memory(
        self,
        content: str,
        memory_type: MemoryType,
        importance: float = 0.5,
        metadata: dict[str, Any] | None = None,
    ) -> MemoryItem:
        """存储记忆。"""
        memory = MemoryItem(
            id=self._generate_id(),
            type=memory_type,
            content=content,
            importance=max(0.0, min(1.0, importance)),  # 确保在0-1范围内
            metadata=metadata or {},
        )
        self.memories[memory.id] = memory
        logger.info(f"存储记忆 {memory.id}, 类型: {memory_type.value}")
        return memory

    async def search_memories(self, query: MemoryQuery) -> list[MemorySearchResult]:
        """搜索记忆（简单的关键词匹配实现）。"""
        results = []

        for memory in self.memories.values():
            # 类型过滤
            if query.memory_types and memory.type not in query.memory_types:
                continue

            # 重要性过滤
            if memory.importance < query.min_importance:
                continue

            # 时间范围过滤
            if query.time_range:
                start_time, end_time = query.time_range
                if start_time and memory.created_at < start_time:
                    continue
                if end_time and memory.created_at > end_time:
                    continue

            # 简单的关键词匹配
            relevance_score = self._calculate_relevance(query.query, memory.content)
            if relevance_score > 0:
                memory.access()  # 更新访问信息
                results.append(
                    MemorySearchResult(
                        memory=memory,
                        relevance_score=relevance_score,
                    )
                )

        # 按相关性排序并限制返回数量
        results.sort(key=lambda r: r.relevance_score, reverse=True)
        return results[: query.limit]

    def _calculate_relevance(self, query: str, content: str) -> float:
        """计算相关性分数（简单实现）。"""
        query_lower = query.lower()
        content_lower = content.lower()

        # 完全匹配
        if query_lower in content_lower:
            return 1.0

        # 部分匹配
        query_words = set(query_lower.split())
        content_words = set(content_lower.split())
        common_words = query_words.intersection(content_words)

        if not query_words:
            return 0.0

        return len(common_words) / len(query_words)

    async def get_memory(self, memory_id: str) -> MemoryItem | None:
        """获取指定记忆。"""
        memory = self.memories.get(memory_id)
        if memory:
            memory.access()
        return memory

    async def update_memory(
        self,
        memory_id: str,
        content: str | None = None,
        importance: float | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> MemoryItem | None:
        """更新记忆。"""
        memory = self.memories.get(memory_id)
        if not memory:
            return None

        if content is not None:
            memory.content = content
        if importance is not None:
            memory.importance = max(0.0, min(1.0, importance))
        if metadata is not None:
            memory.metadata.update(metadata)

        memory.updated_at = datetime.now(UTC)
        logger.debug(f"更新记忆 {memory_id}")
        return memory

    async def delete_memory(self, memory_id: str) -> bool:
        """删除记忆。"""
        if memory_id in self.memories:
            del self.memories[memory_id]
            logger.info(f"删除记忆 {memory_id}")
            return True
        return False

    async def get_recent_memories(
        self,
        limit: int = 10,
        memory_types: list[MemoryType] | None = None,
    ) -> list[MemoryItem]:
        """获取最近的记忆。"""
        memories = list(self.memories.values())

        # 类型过滤
        if memory_types:
            memories = [m for m in memories if m.type in memory_types]

        # 按创建时间排序
        memories.sort(key=lambda m: m.created_at, reverse=True)
        return memories[:limit]

    async def get_important_memories(
        self,
        limit: int = 10,
        min_importance: float = 0.7,
        memory_types: list[MemoryType] | None = None,
    ) -> list[MemoryItem]:
        """获取重要记忆。"""
        memories = list(self.memories.values())

        # 类型和重要性过滤
        if memory_types:
            memories = [m for m in memories if m.type in memory_types]
        memories = [m for m in memories if m.importance >= min_importance]

        # 按重要性和访问次数综合排序
        memories.sort(
            key=lambda m: (m.importance * 0.7 + min(m.access_count / 100, 0.3)),
            reverse=True,
        )
        return memories[:limit]

    async def consolidate_memories(self) -> None:
        """整合记忆（将短期记忆转化为长期记忆）。"""
        short_term_memories = [
            m for m in self.memories.values() if m.type == MemoryType.SHORT_TERM
        ]

        for memory in short_term_memories:
            # 基于访问次数和重要性决定是否转为长期记忆
            if memory.access_count >= 3 or memory.importance >= 0.8:
                memory.type = MemoryType.LONG_TERM
                memory.updated_at = datetime.now(UTC)
                logger.info(f"将短期记忆 {memory.id} 转换为长期记忆")

    async def forget_memories(
        self,
        threshold_date: datetime | None = None,
        max_memories: int | None = None,
    ) -> int:
        """遗忘记忆。"""
        deleted_count = 0

        # 按时间删除
        if threshold_date:
            to_delete = [
                m_id
                for m_id, m in self.memories.items()
                if m.created_at < threshold_date and m.importance < 0.9
            ]
            for memory_id in to_delete:
                del self.memories[memory_id]
                deleted_count += 1

        # 按数量限制删除
        if max_memories and len(self.memories) > max_memories:
            # 计算综合得分并排序
            current_time = datetime.now(UTC)
            scored_memories = [
                (
                    m_id,
                    m.importance * 0.4
                    + min(m.access_count / 100, 0.3)
                    + (1 - (current_time - m.created_at).days / 365) * 0.3,
                )
                for m_id, m in self.memories.items()
            ]
            scored_memories.sort(key=lambda x: x[1])

            # 删除得分最低的记忆
            to_delete_count = len(self.memories) - max_memories
            for memory_id, _ in scored_memories[:to_delete_count]:
                del self.memories[memory_id]
                deleted_count += 1

        if deleted_count > 0:
            logger.info(f"遗忘了 {deleted_count} 条记忆")

        return deleted_count

    async def get_memory_stats(self) -> MemoryStats:
        """获取记忆统计信息。"""
        by_type = {}
        total_importance = 0.0
        total_access = 0

        for memory in self.memories.values():
            type_name = memory.type.value
            by_type[type_name] = by_type.get(type_name, 0) + 1
            total_importance += memory.importance
            total_access += memory.access_count

        # 估算内存使用量
        memory_usage = len(json.dumps([m.dict() for m in self.memories.values()]))

        return MemoryStats(
            total_memories=len(self.memories),
            by_type=by_type,
            average_importance=(
                total_importance / len(self.memories) if self.memories else 0.0
            ),
            total_access_count=total_access,
            memory_usage_bytes=memory_usage,
        )

    async def clear_all_memories(self) -> None:
        """清除所有记忆。"""
        self.memories.clear()
        self._next_id = 1
        logger.info("清除所有记忆")


class MemoryManager:
    """记忆管理器工厂类。"""

    @staticmethod
    def create_memory_manager() -> InMemoryMemoryManager:
        """创建内存记忆管理器。

        Returns:
            内存记忆管理器实例
        """
        return InMemoryMemoryManager()
