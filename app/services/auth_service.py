from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.auth import LoginRequest
from app.schemas.token import Token
from app.crud import auth as auth_crud


async def authenticate_user(
    db: AsyncSession, username: str, password: str
) -> Optional[User]:
    """
    验证用户凭证
    
    Args:
        db: 数据库会话
        username: 用户名
        password: 密码
        
    Returns:
        Optional[User]: 认证成功的用户对象，如果认证失败则为None
    """
    return await auth_crud.authenticate_user(db, username, password)


async def login(db: AsyncSession, login_data: LoginRequest) -> Optional[Token]:
    """
    用户登录
    
    Args:
        db: 数据库会话
        login_data: 登录请求数据
        
    Returns:
        Optional[Token]: 登录成功后的令牌，如果登录失败则为None
    """
    # 认证用户
    user = await authenticate_user(db, login_data.username, login_data.password)
    if not user:
        return None
    
    # 生成令牌
    return await auth_crud.generate_token(user.id) 