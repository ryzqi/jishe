from datetime import datetime, timedelta, timezone
from typing import Any, List, Optional, Union

from jose import jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from db.database import CurrentSession
from schemas.token import TokenPayload
from crud.user import get_user_by_id, get_user_roles
from models.user import User

# 定义密码哈希上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 定义OAuth2密码Bearer流程
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login/oauth2")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证明文密码是否与哈希密码匹配
    
    Args:
        plain_password: 明文密码
        hashed_password: 哈希后的密码
        
    Returns:
        bool: 密码是否匹配
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    获取密码的哈希值
    
    Args:
        password: 明文密码
        
    Returns:
        str: 哈希后的密码
    """
    return pwd_context.hash(password)


def create_access_token(
    subject: Union[str, Any], 
    roles: List[int] = None,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    创建JWT访问令牌
    
    Args:
        subject: 令牌主题，通常是用户ID
        roles: 用户角色ID列表
        expires_delta: 令牌有效期
        
    Returns:
        str: 编码后的JWT令牌
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {
        "exp": expire,
        "sub": str(subject)
    }
    
    # 如果提供了角色，添加到令牌中
    if roles:
        to_encode["roles"] = roles
    
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


async def get_current_user(
    db: CurrentSession,
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    获取当前用户，依赖验证
    
    Args:
        db: 数据库会话
        token: JWT令牌
        
    Returns:
        User: 当前用户对象
        
    Raises:
        HTTPException: 凭证无效或用户不存在
    """
    try:
        # 解码JWT令牌
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
        
        # 检查令牌是否过期
        if datetime.fromtimestamp(token_data.exp) < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 从令牌中获取用户ID并查询用户
    user_id = int(token_data.sub)
    user = await get_user_by_id(db, user_id)
    
    # 检查用户是否存在
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


def get_role_checker(required_roles: List[int]):
    """
    创建一个角色检查器依赖
    
    Args:
        required_roles: 所需的角色ID列表
        
    Returns:
        callable: 角色检查依赖
    """
    async def check_roles(
        db: CurrentSession,
        current_user: User = Security(get_current_user)
    ) -> User:
        """
        检查用户是否具有所需角色
        
        Args:
            db: 数据库会话
            current_user: 当前用户
            
        Returns:
            User: 当前用户对象
            
        Raises:
            HTTPException: 用户没有所需角色
        """
        # 获取用户角色
        user_roles = await get_user_roles(db, current_user.id)
        user_role_ids = [role.role_id for role in user_roles]
        
        # 检查是否有所需角色的任意一个
        if not any(role_id in required_roles for role_id in user_role_ids):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        return current_user
    
    return check_roles


# 定义常用的角色检查依赖
get_super_admin_user = get_role_checker([1])  # 超级管理员 (role_id=1)
get_transport_admin_user = get_role_checker([1, 2])  # 超级管理员或运输管理员 (role_id=1或2)
get_warehouse_admin_user = get_role_checker([1, 3])  # 超级管理员或仓库管理员 (role_id=1或3)
get_any_admin_user = get_role_checker([1, 2, 3])  # 任意管理员角色


    
