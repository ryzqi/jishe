from fastapi import APIRouter

from app.api.v1.endpoints import auth_router, users_router


api_router = APIRouter()

# 添加认证路由
api_router.include_router(auth_router, prefix="/auth", tags=["认证"])

# 添加用户路由
api_router.include_router(users_router, prefix="/users", tags=["用户管理"])
