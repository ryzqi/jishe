from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db_session
from app.schemas.auth import LoginRequest
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserResponse
from app.services.auth_service import login
from app.services.user_service import create_user, get_user_by_username


router = APIRouter()


@router.post("/login", response_model=Token)
async def login_access_token(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """
    OAuth2登录端点，获取访问令牌
    """
    # 尝试登录
    token = await login(db, login_data)
    if not token:
        # 登录失败
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码不正确",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return token


@router.post("/login/oauth2", response_model=Token)
async def login_oauth2_compat(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db_session)
):
    """
    兼容OAuth2标准的登录端点，用于与OAuth2客户端集成
    """
    # 转换为内部登录格式
    login_data = LoginRequest(
        username=form_data.username,
        password=form_data.password
    )
    
    # 尝试登录
    token = await login(db, login_data)
    if not token:
        # 登录失败
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码不正确",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return token


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db_session)
):
    """
    用户注册端点
    """
    # 检查用户名是否已存在
    existing_user = await get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已被注册"
        )
    
    # 创建新用户
    user = await create_user(db, user_data)
    
    return user 