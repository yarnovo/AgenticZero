"""AgenticZero API 主应用"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# 导入路由
from src.api.routes import chat, sessions

# 创建 FastAPI 应用实例
app = FastAPI(
    title="AgenticZero API",
    description="AgenticZero - 智能代理系统 API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# 配置 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(sessions.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")


@app.get("/", response_class=JSONResponse)
async def root():
    """根路由 - 返回欢迎信息"""
    return {
        "message": "欢迎使用 AgenticZero API",
        "version": "0.1.0",
        "description": "AgenticZero - 智能代理系统",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "sessions": "/api/v1/sessions",
            "chat": "/api/v1/chat/completions",
        },
    }


@app.get("/health", response_class=JSONResponse)
async def health_check():
    """健康检查端点"""
    return {"status": "healthy", "service": "AgenticZero API", "version": "0.1.0"}
