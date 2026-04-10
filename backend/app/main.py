"""
FastAPI 应用入口
包含 CORS 配置和路由注册
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, training, report, family, achievement, daily_task
from app.core.config import settings
from app.core.database import create_tables

app = FastAPI(
    title="脑力锻炼 API",
    description="脑力锻炼小程序/App 后端接口",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["认证"])
app.include_router(training.router, prefix="/api/v1/training", tags=["训练"])
app.include_router(report.router, prefix="/api/v1/report", tags=["报告"])
app.include_router(family.router, prefix="/api/v1/family", tags=["家人关注"])
app.include_router(achievement.router, prefix="/api/v1/achievement", tags=["成就"])
app.include_router(daily_task.router, prefix="/api/v1/daily-task", tags=["每日任务"])


@app.on_event("startup")
async def startup_event():
    """应用启动时自动创建数据库表"""
    create_tables()


@app.get("/")
async def root():
    """根路径，用于健康检查"""
    return {"message": "脑力锻炼 API 服务运行中", "version": "2.0.0"}


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy"}
