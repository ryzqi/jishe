"""
API端点模块

包含所有API v1版本的端点路由
"""

from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.users import router as users_router
from app.api.v1.endpoints.chat import router as chat_router

__all__ = ["auth_router", "users_router", "chat_router"] 