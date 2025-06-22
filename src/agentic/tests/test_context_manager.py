"""测试上下文管理器功能。"""

from datetime import datetime

import pytest

from ..context_manager import (
    ContextManager,
    ConversationContext,
    InMemoryContextManager,
    Message,
    PersistentContextManager,
)


@pytest.mark.unit
class TestMessage:
    """测试 Message 类。"""

    def test_message_creation(self):
        """测试消息创建。"""
        message = Message(role="user", content="Hello")
        assert message.role == "user"
        assert message.content == "Hello"
        assert isinstance(message.timestamp, datetime)
        assert message.metadata == {}

    def test_message_with_metadata(self):
        """测试带元数据的消息。"""
        metadata = {"source": "test", "priority": "high"}
        message = Message(role="assistant", content="Hi there", metadata=metadata)
        assert message.metadata == metadata


@pytest.mark.unit
class TestConversationContext:
    """测试 ConversationContext 类。"""

    def test_context_creation(self):
        """测试上下文创建。"""
        context = ConversationContext(conversation_id="test_1")
        assert context.conversation_id == "test_1"
        assert len(context.messages) == 0
        assert isinstance(context.created_at, datetime)
        assert isinstance(context.updated_at, datetime)

    def test_add_message(self):
        """测试添加消息。"""
        context = ConversationContext(conversation_id="test_1")
        context.add_message("user", "Hello")

        assert len(context.messages) == 1
        assert context.messages[0].role == "user"
        assert context.messages[0].content == "Hello"

    def test_get_messages_for_llm(self):
        """测试获取 LLM 格式的消息。"""
        context = ConversationContext(conversation_id="test_1")
        context.add_message("system", "You are a helpful assistant")
        context.add_message("user", "Hello")
        context.add_message("assistant", "Hi there!")

        messages = context.get_messages_for_llm()
        expected = [
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
        ]
        assert messages == expected

    def test_clear_history(self):
        """测试清除历史。"""
        context = ConversationContext(conversation_id="test_1")
        context.add_message("system", "You are a helpful assistant")
        context.add_message("user", "Hello")
        context.add_message("assistant", "Hi there!")

        # 保留系统消息
        context.clear_history(keep_system=True)
        assert len(context.messages) == 1
        assert context.messages[0].role == "system"

        # 清除所有消息
        context.add_message("user", "Hello again")
        context.clear_history(keep_system=False)
        assert len(context.messages) == 0

    def test_message_count_and_token_estimate(self):
        """测试消息计数和 token 估算。"""
        context = ConversationContext(conversation_id="test_1")
        assert context.get_message_count() == 0
        assert context.get_token_estimate() == 0

        context.add_message("user", "Hello world!")
        assert context.get_message_count() == 1
        assert context.get_token_estimate() > 0

    def test_max_history_length(self):
        """测试最大历史长度限制。"""
        context = ConversationContext(conversation_id="test_1", max_history_length=3)
        context.add_message("system", "System message")

        # 添加超过限制的消息
        for i in range(5):
            context.add_message("user", f"Message {i}")

        # 系统消息应该被保留，其他消息应该被截断
        assert len(context.messages) <= 3
        system_messages = [msg for msg in context.messages if msg.role == "system"]
        assert len(system_messages) == 1


@pytest.mark.unit
@pytest.mark.asyncio
class TestInMemoryContextManager:
    """测试内存上下文管理器。"""

    async def test_create_context(self):
        """测试创建上下文。"""
        manager = InMemoryContextManager()
        context = await manager.create_context("test_1", "System instruction")

        assert context.conversation_id == "test_1"
        assert len(context.messages) == 1
        assert context.messages[0].role == "system"
        assert context.messages[0].content == "System instruction"

    async def test_get_context(self):
        """测试获取上下文。"""
        manager = InMemoryContextManager()

        # 获取不存在的上下文
        context = await manager.get_context("nonexistent")
        assert context is None

        # 创建并获取上下文
        created_context = await manager.create_context("test_1")
        retrieved_context = await manager.get_context("test_1")
        assert retrieved_context is not None
        assert retrieved_context.conversation_id == "test_1"

    async def test_update_context(self):
        """测试更新上下文。"""
        manager = InMemoryContextManager()
        context = await manager.create_context("test_1")

        old_updated_at = context.updated_at
        context.add_message("user", "Test message")
        await manager.update_context(context)

        # 检查时间戳是否更新
        assert context.updated_at > old_updated_at

    async def test_delete_context(self):
        """测试删除上下文。"""
        manager = InMemoryContextManager()
        await manager.create_context("test_1")

        # 确认上下文存在
        context = await manager.get_context("test_1")
        assert context is not None

        # 删除上下文
        await manager.delete_context("test_1")
        context = await manager.get_context("test_1")
        assert context is None

    async def test_list_contexts(self):
        """测试列出上下文。"""
        manager = InMemoryContextManager()

        # 空列表
        contexts = await manager.list_contexts()
        assert contexts == []

        # 创建多个上下文
        await manager.create_context("test_1")
        await manager.create_context("test_2")
        await manager.create_context("test_3")

        contexts = await manager.list_contexts()
        assert set(contexts) == {"test_1", "test_2", "test_3"}


@pytest.mark.unit
def test_context_manager_factory():
    """测试上下文管理器工厂。"""
    # 测试内存管理器
    memory_manager = ContextManager.create_memory_manager()
    assert isinstance(memory_manager, InMemoryContextManager)

    # 测试持久化管理器
    persistent_manager = ContextManager.create_persistent_manager(
        "/tmp/test_contexts.json"
    )
    assert isinstance(persistent_manager, PersistentContextManager)


@pytest.mark.integration
@pytest.mark.asyncio
class TestPersistentContextManager:
    """测试持久化上下文管理器（集成测试）。"""

    async def test_persistence(self, tmp_path):
        """测试持久化功能。"""
        storage_path = tmp_path / "test_contexts.json"

        # 创建管理器并添加上下文
        manager1 = PersistentContextManager(str(storage_path))
        context = await manager1.create_context("test_1", "System message")
        context.add_message("user", "Hello")
        await manager1.update_context(context)

        # 创建新的管理器实例，应该能加载之前的数据
        manager2 = PersistentContextManager(str(storage_path))
        loaded_context = await manager2.get_context("test_1")

        assert loaded_context is not None
        assert loaded_context.conversation_id == "test_1"
        assert len(loaded_context.messages) == 2
        assert loaded_context.messages[0].content == "System message"
        assert loaded_context.messages[1].content == "Hello"
