"""AgenticZero API 主应用"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse

# 创建 FastAPI 应用实例
app = FastAPI(
    title="AgenticZero API",
    description="AgenticZero - 智能代理系统 API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.get("/", response_class=JSONResponse)
async def root():
    """根路由 - 返回欢迎信息"""
    return {
        "message": "欢迎使用 AgenticZero API",
        "version": "0.1.0",
        "description": "AgenticZero - 智能代理系统",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", response_class=JSONResponse)
async def health_check():
    """健康检查端点"""
    return {"status": "healthy", "service": "AgenticZero API", "version": "0.1.0"}
