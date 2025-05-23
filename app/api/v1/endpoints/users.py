from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status,UploadFile, File, Body
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
from schemas.user import UserCreate, UserResponse, UserUpdate, UserResponse_me, PasswordChange,UpdateUserPayload
from schemas.role import RoleResponse
from service.user_log import insert_user_log
from core.password import verify_password, get_password_hash
from service.aliyunOSS import upload_avatar

router = APIRouter()


@router.get("/logout")
async def logout(
    db: CurrentSession,
    current_user: User = Depends(get_current_user)
):
    insert_user_log(str(current_user.id), "退出登录", "成功")
    return current_user


@router.get("/me", response_model=UserResponse_me, summary="获取当前用户信息")
async def read_users_me(
        db: CurrentSession,
        current_user: User = Depends(get_current_user)
) -> UserResponse_me:
    """
    获取当前登录用户信息
    """
    insert_user_log(str(current_user.id), "查看个人信息", "成功")
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
    ).order_by(User.id.asc()).offset(skip).limit(limit)

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
    insert_user_log(str(current_user.id), "查看所有用户", "成功")
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
    insert_user_log(str(current_user.id), "新增系统用户", "成功")
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
        payload: UpdateUserPayload,
        current_user: User = Depends(get_super_admin_user),
) -> UserResponse:
    """
    更新用户信息（仅限超级管理员）
    
    - **user_id**: 用户ID
    - **user_in**: 用户更新模型
    - **role_ids**: 角色ID列表
    """
    # 更新用户
    user = await update_user(db, user_id, payload.user_in, payload.role_ids)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    insert_user_log(str(current_user.id), "更新用户信息", "成功")
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
    if user_id in [1, 2, 3, 4]:
        insert_user_log(str(current_user.id), "删除系统用户", "成功")
        return
    # 删除用户
    success = await delete_user(db, user_id)
    insert_user_log(str(current_user.id), "删除系统用户", "成功")
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )


@router.post("/change_password", summary="修改密码")
async def delete_user_endpoint(
        password_change: PasswordChange,
        db: CurrentSession,
        current_user: User = Depends(get_current_user)
):
    # 检查当前用户是否正在删除自己
    print("当前用户id：", current_user.id)
    if current_user.id != password_change.user_id:
        roles = await get_user_roles(db, current_user.id)
        role_ids = [role.role_id for role in roles]  # 提取 ID 列表
        print("当前用户角色列表：", role_ids)
        if 1 not in role_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin users can change passwords for other users"
            )
    user = await get_user_by_id(db, password_change.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"can't find user with user_id = {password_change.user_id}"
        )
    psw_result = verify_password(password_change.old_password, user.password)
    print("old_password:", password_change.old_password)
    print("hashed_password:", user.password)
    print("psw_result:", psw_result)
    if not psw_result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="password is incorrect"
        )
    psw_update = UserUpdate(password=password_change.new_password)

    res_user = await update_user(db, password_change.user_id, psw_update, None)
    insert_user_log(str(current_user.id), "修改密码", "成功")
    return res_user


@router.post("/upload-avatar")
async def upload_user_avatar(
        db: CurrentSession,
        current_user: User = Depends(get_current_user),
        file: UploadFile = File(...)
):
    # 限制文件类型（建议做）
    allowed_suffix = {"jpg", "jpeg", "png", "gif"}
    suffix = file.filename.split('.')[-1].lower()
    if suffix not in allowed_suffix:
        raise HTTPException(status_code=400, detail="不支持的文件类型")

    try:
        file_bytes = await file.read()
        url = upload_avatar(file_bytes, suffix)
        user_in = UserUpdate(avatar_url=url)
        user = await update_user(db, current_user.id, user_in, None)
        if user is None:
            raise HTTPException(status_code=500, detail=f"上传失败")
        return {"url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")