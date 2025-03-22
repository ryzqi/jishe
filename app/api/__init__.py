"""
API路由模块

包含所有API路由及其版本
"""

from fastapi import APIRouter

from app.api.v1 import api_router as api_v1_router

# 创建主API路由
api_router = APIRouter()

# 包含v1版本路由
api_router.include_router(api_v1_router, prefix="/v1")
