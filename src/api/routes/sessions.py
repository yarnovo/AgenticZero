"""会话管理 API 路由"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from src.agent.settings import LLMProvider
from src.api.session_manager import SessionConfig, SessionManager

# 创建路由器
router = APIRouter(prefix="/sessions", tags=["sessions"])

# 创建全局会话管理器实例
session_manager = SessionManager()


# 请求/响应模型
class CreateSessionRequest(BaseModel):
    """创建会话请求"""

    session_id: str = Field(description="会话唯一标识符")
    name: Optional[str] = Field(default=None, description="会话名称")
    description: Optional[str] = Field(default=None, description="会话描述")
    llm_provider: LLMProvider = Field(
        default=LLMProvider.OPENAI, description="LLM 提供商"
    )
    llm_settings: Optional[dict] = Field(default=None, description="LLM 设置")
    agent_settings: Optional[dict] = Field(default=None, description="Agent 设置")


class UpdateSessionRequest(BaseModel):
    """更新会话请求"""

    name: Optional[str] = Field(default=None, description="会话名称")
    description: Optional[str] = Field(default=None, description="会话描述")
    metadata: Optional[dict] = Field(default=None, description="元数据")


class SessionResponse(BaseModel):
    """会话响应"""

    session_id: str
    name: str
    description: str
    created_at: str
    updated_at: str
    metadata: dict


class SessionListResponse(BaseModel):
    """会话列表响应"""

    sessions: List[SessionResponse]
    total: int


# API 端点
@router.post("/", response_model=SessionResponse)
async def create_session(request: CreateSessionRequest):
    """创建新的会话"""
    try:
        config = await session_manager.create_session(
            session_id=request.session_id,
            name=request.name,
            description=request.description,
            llm_provider=request.llm_provider,
            llm_settings=request.llm_settings,
            agent_settings=request.agent_settings,
        )
        return SessionResponse(
            session_id=config.session_id,
            name=config.name,
            description=config.description,
            created_at=config.created_at.isoformat(),
            updated_at=config.updated_at.isoformat(),
            metadata=config.metadata,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建会话失败: {str(e)}")


@router.get("/", response_model=SessionListResponse)
async def list_sessions(
    source: str = Query(
        default="all",
        description="数据源: memory(内存), file(文件), all(所有)",
        regex="^(memory|file|all)$",
    ),
):
    """列出所有会话"""
    try:
        sessions = await session_manager.list_sessions(source=source)
        return SessionListResponse(
            sessions=[
                SessionResponse(
                    session_id=s.session_id,
                    name=s.name,
                    description=s.description,
                    created_at=s.created_at.isoformat(),
                    updated_at=s.updated_at.isoformat(),
                    metadata=s.metadata,
                )
                for s in sessions
            ],
            total=len(sessions),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取会话列表失败: {str(e)}")


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str):
    """获取指定会话的信息"""
    try:
        # 尝试从配置中获取
        config = None
        if session_id in session_manager.session_configs:
            config = session_manager.session_configs[session_id]
        else:
            config = session_manager._load_session_config(session_id)

        if not config:
            raise HTTPException(status_code=404, detail=f"会话 {session_id} 不存在")

        return SessionResponse(
            session_id=config.session_id,
            name=config.name,
            description=config.description,
            created_at=config.created_at.isoformat(),
            updated_at=config.updated_at.isoformat(),
            metadata=config.metadata,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取会话信息失败: {str(e)}")


@router.put("/{session_id}", response_model=SessionResponse)
async def update_session(session_id: str, request: UpdateSessionRequest):
    """更新会话信息"""
    try:
        config = await session_manager.update_session(
            session_id=session_id,
            name=request.name,
            description=request.description,
            metadata=request.metadata,
        )

        if not config:
            raise HTTPException(status_code=404, detail=f"会话 {session_id} 不存在")

        return SessionResponse(
            session_id=config.session_id,
            name=config.name,
            description=config.description,
            created_at=config.created_at.isoformat(),
            updated_at=config.updated_at.isoformat(),
            metadata=config.metadata,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新会话失败: {str(e)}")


@router.delete("/{session_id}")
async def delete_session(session_id: str):
    """删除会话"""
    try:
        success = await session_manager.delete_session(session_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"会话 {session_id} 不存在")
        return JSONResponse(
            content={"message": f"会话 {session_id} 已成功删除"}, status_code=200
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除会话失败: {str(e)}")


@router.get("/stats/summary")
async def get_session_stats():
    """获取会话统计信息"""
    try:
        stats = session_manager.get_session_stats()
        return JSONResponse(content=stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")
