from typing import Optional
from datetime import timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.auth import LoginRequest
from app.schemas.token import Token
from app.core.security import verify_password, create_access_token
from app.core.config import settings
from app.crud.user import get_user_by_username, get_user_by_id


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
    # 获取用户
    user = await get_user_by_username(db, username)
    if not user:
        return None
    
    # 验证密码
    if not verify_password(password, user.password):
        return None
    
    # 检查用户状态
    if not user.is_active:
        return None
    
    return user


async def generate_token(user_id: int) -> Token:
    """
    为用户生成访问令牌
    
    Args:
        user_id: 用户ID
        
    Returns:
        Token: 包含访问令牌的对象
    """
    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user_id, expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token) 