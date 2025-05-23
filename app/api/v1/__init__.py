from fastapi import APIRouter

from api.v1.endpoints import (
    auth_router,
    users_router,
    chat_router,
    stock_router,
    patrol_router,
    error_router,
    transport_router,
    iodta_router,
    user_log_router
)


api_router = APIRouter()

# 添加认证路由
api_router.include_router(auth_router, prefix="/auth", tags=["认证"])

# 添加用户路由
api_router.include_router(users_router, prefix="/users", tags=["用户管理"])

# 添加聊天路由
api_router.include_router(chat_router, prefix="/chat", tags=["聊天"])

# 添加库存路由
api_router.include_router(stock_router, prefix="/stock", tags=["库存"])

# 添加巡查路由
api_router.include_router(patrol_router, prefix="/patrol", tags=["巡查"])

# 添加错误管理路由
api_router.include_router(error_router, prefix="/errors", tags=["错误管理"])

# 添加运输管理路由
api_router.include_router(transport_router, prefix="/transport", tags=["运输管理"])

# 添加IODTA路由
api_router.include_router(iodta_router, prefix="/iodta", tags=["IODTA"])

api_router.include_router(user_log_router, prefix="/user_log", tags=["近期用户操作日志"])
