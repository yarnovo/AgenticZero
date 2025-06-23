"""会话管理模块 - 管理 Agent 会话的创建、存储和生命周期"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from src.agent import Agent
from src.agent.settings import AgentSettings, LLMSettings, LLMProvider


class SessionConfig(BaseModel):
    """会话配置"""

    session_id: str = Field(description="会话唯一标识符")
    name: str = Field(default="未命名会话", description="会话名称")
    description: str = Field(default="", description="会话描述")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    agent_settings: Optional[dict] = Field(default=None, description="Agent 配置")
    metadata: Dict[str, any] = Field(default_factory=dict, description="元数据")


class SessionManager:
    """会话管理器 - 处理内存和文件系统中的会话"""

    def __init__(self, base_path: str = "sessions"):
        """
        初始化会话管理器

        Args:
            base_path: 会话存储的基础路径
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
        self.sessions: Dict[str, Agent] = {}  # 内存中的会话
        self.session_configs: Dict[str, SessionConfig] = {}  # 会话配置

    def _get_session_path(self, session_id: str) -> Path:
        """获取会话的文件系统路径"""
        return self.base_path / session_id

    def _save_session_config(self, session_id: str, config: SessionConfig) -> None:
        """保存会话配置到文件"""
        session_path = self._get_session_path(session_id)
        session_path.mkdir(exist_ok=True)
        config_file = session_path / "session_config.json"
        config.updated_at = datetime.now()
        config_file.write_text(config.model_dump_json(indent=2))

    def _load_session_config(self, session_id: str) -> Optional[SessionConfig]:
        """从文件加载会话配置"""
        config_file = self._get_session_path(session_id) / "session_config.json"
        if config_file.exists():
            config_data = json.loads(config_file.read_text())
            return SessionConfig(**config_data)
        return None

    async def create_session(
        self,
        session_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        llm_provider: LLMProvider = LLMProvider.OPENAI,
        llm_settings: Optional[dict] = None,
        agent_settings: Optional[dict] = None,
    ) -> SessionConfig:
        """
        创建新的会话

        Args:
            session_id: 会话ID
            name: 会话名称
            description: 会话描述
            llm_provider: LLM 提供商
            llm_settings: LLM 设置
            agent_settings: Agent 设置

        Returns:
            创建的会话配置
        """
        # 检查会话是否已存在
        if session_id in self.sessions or self._get_session_path(session_id).exists():
            raise ValueError(f"会话 {session_id} 已存在")

        # 创建会话目录结构
        session_path = self._get_session_path(session_id)
        session_path.mkdir(exist_ok=True)

        # 创建子目录
        (session_path / "memory").mkdir(exist_ok=True)
        (session_path / "mcp").mkdir(exist_ok=True)
        (session_path / "graphs").mkdir(exist_ok=True)
        (session_path / "logs").mkdir(exist_ok=True)

        # 创建会话配置
        config = SessionConfig(
            session_id=session_id,
            name=name or f"会话 {session_id}",
            description=description or "",
            agent_settings=agent_settings or {},
        )

        # 保存配置
        self._save_session_config(session_id, config)
        self.session_configs[session_id] = config

        # 创建 Agent 实例
        llm_settings_obj = LLMSettings(
            provider=llm_provider,
            **(llm_settings or {}),
        )

        agent_settings_obj = AgentSettings(
            name=config.name,
            instruction=config.description or "你是一个有用的AI助手。",
            llm_settings=llm_settings_obj,
            **(agent_settings or {}),
        )

        # 创建并存储 Agent，使用会话特定的存储目录
        agent = Agent(
            config=agent_settings_obj,
            conversation_id=session_id,
            storage_dir=str(session_path),
        )

        # 初始化 Agent
        await agent.initialize()

        self.sessions[session_id] = agent

        return config

    async def get_session(self, session_id: str) -> Optional[Agent]:
        """
        获取会话的 Agent 实例

        Args:
            session_id: 会话ID

        Returns:
            Agent 实例，如果不存在则返回 None
        """
        # 如果在内存中，直接返回
        if session_id in self.sessions:
            return self.sessions[session_id]

        # 尝试从文件系统加载
        config = self._load_session_config(session_id)
        if config:
            # 这里简化处理，实际应该根据配置重建 Agent
            # 目前返回 None，需要实现完整的 Agent 恢复逻辑
            return None

        return None

    async def delete_session(self, session_id: str) -> bool:
        """
        删除会话

        Args:
            session_id: 会话ID

        Returns:
            是否删除成功
        """
        # 先关闭 Agent
        if session_id in self.sessions:
            agent = self.sessions[session_id]
            await agent.close()
            del self.sessions[session_id]

        if session_id in self.session_configs:
            del self.session_configs[session_id]

        # 从文件系统删除
        session_path = self._get_session_path(session_id)
        if session_path.exists():
            shutil.rmtree(session_path)
            return True

        return False

    async def list_sessions(self, source: str = "all") -> List[SessionConfig]:
        """
        列出所有会话

        Args:
            source: 数据源 - "memory", "file", "all"

        Returns:
            会话配置列表
        """
        sessions = []

        # 从内存获取
        if source in ["memory", "all"]:
            sessions.extend(self.session_configs.values())

        # 从文件系统获取
        if source in ["file", "all"]:
            for session_dir in self.base_path.iterdir():
                if session_dir.is_dir():
                    config = self._load_session_config(session_dir.name)
                    if config and config.session_id not in self.session_configs:
                        sessions.append(config)

        # 按更新时间排序
        sessions.sort(key=lambda x: x.updated_at, reverse=True)
        return sessions

    async def update_session(
        self,
        session_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, any]] = None,
    ) -> Optional[SessionConfig]:
        """
        更新会话信息

        Args:
            session_id: 会话ID
            name: 新的会话名称
            description: 新的会话描述
            metadata: 要更新的元数据

        Returns:
            更新后的会话配置，如果会话不存在则返回 None
        """
        # 获取现有配置
        config = None
        if session_id in self.session_configs:
            config = self.session_configs[session_id]
        else:
            config = self._load_session_config(session_id)

        if not config:
            return None

        # 更新配置
        if name is not None:
            config.name = name
        if description is not None:
            config.description = description
        if metadata is not None:
            config.metadata.update(metadata)

        # 保存更新
        self._save_session_config(session_id, config)
        self.session_configs[session_id] = config

        return config

    def get_session_stats(self) -> Dict[str, any]:
        """获取会话统计信息"""
        return {
            "total_sessions": len(list(self.base_path.iterdir())),
            "active_sessions": len(self.sessions),
            "cached_configs": len(self.session_configs),
        }
