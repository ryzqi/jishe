"""
API端点模块

包含所有API v1版本的端点路由
"""

from api.v1.endpoints.auth import router as auth_router
from api.v1.endpoints.users import router as users_router
from api.v1.endpoints.chat import router as chat_router
from api.v1.endpoints.stock import router as stock_router
from api.v1.endpoints.patrol import router as patrol_router
from api.v1.endpoints.error import router as error_router
from api.v1.endpoints.transport import router as transport_router
from api.v1.endpoints.iodta import router as iodta_router

__all__ = [
    "auth_router",
    "users_router",
    "chat_router",
    "stock_router",
    "patrol_router",
    "error_router",
    "transport_router",
    "iodta_router",
]
