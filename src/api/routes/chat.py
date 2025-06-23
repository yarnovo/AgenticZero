"""聊天 API 路由 - 支持流式和非流式响应"""

import json
from collections.abc import AsyncGenerator

from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

# 创建路由器
router = APIRouter(prefix="/chat", tags=["chat"])

# 使用同一个会话管理器实例
from src.api.routes.sessions import session_manager


class ChatRequest(BaseModel):
    """聊天请求"""

    session_id: str = Field(description="会话ID")
    message: str = Field(description="用户消息")
    stream: bool = Field(default=False, description="是否使用流式响应")
    max_iterations: int | None = Field(
        default=None, description="最大迭代次数（用于控制工具调用）"
    )


class ChatResponse(BaseModel):
    """聊天响应（非流式）"""

    session_id: str
    message: str
    response: str


async def generate_stream_response(
    agent, message: str, max_iterations: int | None = None
) -> AsyncGenerator[str, None]:
    """
    生成流式响应

    使用 Agent 的原生 run_stream 方法
    """
    # 使用 Agent 的原生流式方法
    async for chunk in agent.run_stream(message, max_iterations):
        # 将 chunk 转换为 SSE 格式
        yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"

    # 发送流结束信号
    yield "data: [DONE]\n\n"


@router.post("/completions")
async def chat_completion(request: ChatRequest, accept: str | None = Header(None)):
    """
    聊天完成端点

    支持两种响应模式：
    1. 非流式：返回完整的 JSON 响应
    2. 流式：返回 Server-Sent Events (SSE) 流
    """
    try:
        # 获取会话中的 Agent
        agent = await session_manager.get_session(request.session_id)
        if not agent:
            raise HTTPException(
                status_code=404, detail=f"会话 {request.session_id} 不存在或未激活"
            )

        # 根据请求决定响应方式
        if request.stream:
            # 流式响应
            return StreamingResponse(
                generate_stream_response(
                    agent, request.message, request.max_iterations
                ),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no",  # 禁用 Nginx 缓冲
                },
            )
        else:
            # 非流式响应
            response = await agent.run(request.message, request.max_iterations)
            return ChatResponse(
                session_id=request.session_id,
                message=request.message,
                response=response,
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"聊天处理失败: {str(e)}")


@router.post("/{session_id}/messages")
async def send_message(
    session_id: str,
    message: str,
    stream: bool = False,
    max_iterations: int | None = None,
):
    """
    发送消息到指定会话（简化的接口）

    这是一个更简单的接口，直接在 URL 中指定会话 ID
    """
    request = ChatRequest(
        session_id=session_id,
        message=message,
        stream=stream,
        max_iterations=max_iterations,
    )
    return await chat_completion(request)


# 健康检查端点
@router.get("/health")
async def chat_health():
    """聊天服务健康检查"""
    return {
        "status": "healthy",
        "service": "chat",
        "active_sessions": len(session_manager.sessions),
    }
