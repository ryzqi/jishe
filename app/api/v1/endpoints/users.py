from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import (
    get_current_user,
    get_super_admin_user,
    get_transport_admin_user,
    get_warehouse_admin_user,
    get_any_admin_user
)
from crud.user import (
    create_user,
    get_user_by_id,
    update_user,
    delete_user,
    get_user_roles
)
from crud.role import get_all_roles, get_role_by_id
from db.database import CurrentSession
from models.user import User
from schemas.user import UserCreate, UserResponse, UserUpdate,UserResponse_me
from schemas.role import RoleResponse


router = APIRouter()


@router.get("/me", response_model=UserResponse_me, summary="获取当前用户信息")
async def read_users_me(
    db: CurrentSession,
    current_user: User = Depends(get_current_user)
) -> UserResponse_me:
    """
    获取当前登录用户信息
    """
    return current_user


@router.get("/me/roles", response_model=List[RoleResponse], summary="获取当前用户角色")
async def read_user_me_roles(
    db: CurrentSession,
    current_user: User = Depends(get_current_user)
) -> List[RoleResponse]:
    """
    获取当前登录用户的所有角色
    """
    roles = await get_user_roles(db, current_user.id)
    return roles


@router.get("", summary="获取所有用户")
async def read_users(
    db: CurrentSession,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_super_admin_user)
):
    """
    获取所有用户（仅限超级管理员）
    
    - **skip**: 跳过记录数
    - **limit**: 返回记录数
    """

    query = select(
        User.id,
        User.username,
        User.name,
        User.email,
        User.phone,
        func.to_char(User.createtime, "YYYY-MM-DD HH24:MI:SS").label("createTime")  # 格式化时间并别名
    ).offset(skip).limit(limit)

    result = await db.execute(query)
    users = result.mappings().all()  # 返回字典列表，如 [{"id": 1, "name": "张三", ...}]
    user_dicts = []
    for user in users:
        user_id = user.id
        roles = await get_user_roles(db, user_id)
        user_dict = dict(user)
        if roles:
            user_dict["role"] = roles[0].role_id
        else:
            user_dict["role"] = None  # 或者 "未分配"、空字符串等，视你的业务需要
        user_dicts.append(user_dict)

    return user_dicts


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="创建新用户")
async def create_new_user(
    db: CurrentSession,
    user_in: UserCreate,
    role_id: int,
    current_user: User = Depends(get_super_admin_user)
) -> UserResponse:
    """
    创建新用户（仅限超级管理员）
    
    - **user_in**: 用户创建模型
    - **role_ids**: 角色ID列表
    """
    # 验证角色ID
    available_roles = await get_all_roles(db)
    available_role_ids = [role.role_id for role in available_roles]

    if role_id not in available_role_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Role with ID {role_id} not found"
        )
    
    # 创建用户
    user = await create_user(db, user_in, role_id)
    return user


@router.get("/{user_id}", response_model=UserResponse, summary="获取指定用户")
async def read_user(
    db: CurrentSession,
    user_id: int,
    current_user: User = Depends(get_any_admin_user)
) -> User:
    """
    获取指定用户信息（任意管理员可访问）
    
    - **user_id**: 用户ID
    """
    user = await get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.put("/{user_id}", response_model=UserResponse, summary="更新用户")
async def update_user_endpoint(
    db: CurrentSession,
    user_id: int,
    user_in: UserUpdate,
    current_user: User = Depends(get_super_admin_user),
    role_ids: Optional[List[int]] = None
) -> UserResponse:
    """
    更新用户信息（仅限超级管理员）
    
    - **user_id**: 用户ID
    - **user_in**: 用户更新模型
    - **role_ids**: 角色ID列表
    """
    # 更新用户
    user = await update_user(db, user_id, user_in, role_ids)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="删除用户")
async def delete_user_endpoint(
    db: CurrentSession,
    user_id: int,
    current_user: User = Depends(get_super_admin_user)
) -> None:
    """
    删除用户（仅限超级管理员）
    
    - **user_id**: 用户ID
    """
    # 检查当前用户是否正在删除自己
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete self"
        )
    
    # 删除用户
    success = await delete_user(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        ) 