from datetime import timedelta
import asyncio
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from loguru import logger

from core.config import settings
from core.security import create_access_token
from crud.user import authenticate_user, get_user_roles
from db.database import CurrentSession
from schemas.token import Token, LoginRequest
from fastapi.responses import Response  # 导入Response


router = APIRouter()


async def retry_db_operation(operation, max_retries=3, *args, **kwargs):
    """尝试执行数据库操作，失败时自动重试"""
    retries = 0
    last_error = None

    while retries < max_retries:
        try:
            return await operation(*args, **kwargs)
        except (OperationalError, ConnectionError) as e:
            retries += 1
            last_error = e
            logger.warning(f"数据库操作失败，重试 {retries}/{max_retries}: {str(e)}")
            await asyncio.sleep(0.5)  # 短暂等待后重试

    # 所有重试都失败
    logger.error(f"数据库操作在 {max_retries} 次重试后仍然失败: {str(last_error)}")
    raise last_error


@router.post("/login", response_model=Token, summary="用户登录")
async def login(
    login_data: LoginRequest,
    db: CurrentSession,
    background_tasks: BackgroundTasks,
    response: Response
) -> Token:
    """
    使用用户名和密码登录获取访问令牌
    
    - **username**: 用户名
    - **password**: 密码
    - **role_name**: 角色名称
    """
    try:
        # 验证用户凭据
        user = await authenticate_user(db, login_data.username, login_data.password)
        if not user:
            logger.warning(f"登录失败: 用户名或密码错误 (用户名: {login_data.username})")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 获取用户所有角色 - 使用重试机制
        try:
            user_roles = await retry_db_operation(get_user_roles, 3, db, user.id)
            # 获取用户所有角色ID列表
            all_role_ids = [role.role_id for role in user_roles]
            
            if not all_role_ids:
                logger.warning(f"登录失败: 用户 {login_data.username} 没有任何角色权限")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Access denied. User has no roles.",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # 验证请求的角色是否在用户权限列表中
            requested_role = next((role for role in user_roles if role.role_name == login_data.role_name), None)
            if not requested_role:
                logger.warning(f"登录失败: 用户 {login_data.username} 没有 {login_data.role_name} 角色权限")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Access denied. No matching role found.",
                    headers={"WWW-Authenticate": "Bearer"},
                )
                
        except Exception as e:
            logger.error(f"获取用户角色失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Failed to verify user roles.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 创建访问令牌，使用用户所有角色ID列表
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            subject=user.id,
            roles=all_role_ids,  # 使用用户所有角色ID列表
            expires_delta=access_token_expires
        )

        # 将记录日志放入后台任务，不阻塞响应
        background_tasks.add_task(logger.info, f"用户 {user.username} (ID: {user.id}) 登录成功，角色: {login_data.role_name}")
        return Token(access_token=access_token, token_type="bearer")
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"数据库错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service is currently unavailable. Please try again later."
        )
    except Exception as e:
        logger.error(f"登录过程发生未知错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again later."
        )


@router.post("/login/oauth2", response_model=Token, summary="OAuth2 登录")
async def login_oauth2(
    db: CurrentSession,
    background_tasks: BackgroundTasks,
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Token:
    """
    使用OAuth2 Password流程登录获取访问令牌（适用于Swagger UI中的授权）
    
    - **username**: 用户名
    - **password**: 密码
    """
    try:
        # 验证用户凭据
        user = await authenticate_user(db, form_data.username, form_data.password)
        if not user:
            logger.warning(f"OAuth2登录失败: 用户名或密码错误 (用户名: {form_data.username})")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 获取用户角色 - 使用重试机制
        try:
            user_roles = await retry_db_operation(get_user_roles, 3, db, user.id)
            role_ids = [role.role_id for role in user_roles]
        except Exception as e:
            # 如果获取角色失败，默认给予最低权限继续
            logger.error(f"获取用户角色失败: {str(e)}")
            role_ids = []

        # 创建访问令牌
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            subject=user.id,
            roles=role_ids,
            expires_delta=access_token_expires
        )

        # 将记录日志放入后台任务，不阻塞响应
        background_tasks.add_task(logger.info, f"用户 {user.username} (ID: {user.id}) 通过OAuth2登录成功")
        return Token(access_token=access_token, token_type="bearer")
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"数据库错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service is currently unavailable. Please try again later."
        )
    except Exception as e:
        logger.error(f"OAuth2登录过程中发生错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during authentication",
        )
