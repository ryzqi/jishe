from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger

from core.security import get_current_user
from db.database import CurrentSession
from models.user import User
from schemas.error import ErrorCreate, ErrorUpdate, ErrorResponse
from schemas.patrol import ErrorUpdateResponse
from crud.error import get_error_by_id, create_error as create_error_crud, update_error, delete_error, get_errors_by_user_id, get_all_errors
from crud.user import get_user_by_id

router = APIRouter()


@router.get(
    "", response_model=List[ErrorUpdateResponse], summary="获取错误列表及统计"
)
async def get_errors(
    db: CurrentSession, current_user: User = Depends(get_current_user)
) -> List[ErrorUpdateResponse]:
    """
    获取所有错误信息及状态统计
    
    返回带有用户信息的错误列表，包括错误ID、发送者、标题、内容、创建时间和状态
    """
    try:
        errors_data = await get_all_errors(db)
        
        # 将字典数据转换为ErrorUpdateResponse模型
        return [ErrorUpdateResponse(**error) for error in errors_data]
    except Exception as e:
        logger.error(f"获取错误统计信息失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取错误统计信息失败",
        )


@router.post("", status_code=status.HTTP_201_CREATED, response_model=ErrorResponse)
async def create_error_record(
    error_create: ErrorCreate,
    db: CurrentSession,
    current_user: User = Depends(get_current_user)
) -> ErrorResponse:
    """
        创建问题记录
        {
      "error_content": "string",
      "states": 1,
      "title": "string"
    }
    """
    # 获取所有错误数据并确保设置user_id
    error_dict = error_create.model_dump()
    error_dict["user_id"] = current_user.id  # 始终使用当前用户ID
    
    # 确保states是字符串
    if "states" in error_dict and isinstance(error_dict["states"], int):
        error_dict["states"] = str(error_dict["states"])
    
    
    # 使用更新后的数据创建错误记录
    error = await create_error_crud(db, ErrorCreate(**error_dict))
    return error


@router.delete("/{error_id}", status_code=status.HTTP_200_OK, summary="删除错误记录")
async def delete_error_record(
    error_id: int,
    db: CurrentSession, 
    current_user: User = Depends(get_current_user)
):
    """
    删除一条巡查问题记录

    Args:
        error_id: 要删除的问题ID
    
    Returns:
        删除结果信息
    """
    try:
        # 查询是否存在该问题
        error = await get_error_by_id(db, error_id)
        if error is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"问题ID:{error_id}不存在"
            )

        # 执行删除
        success = await delete_error(db, error_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail="删除问题失败"
            )

        return {"success": True, "message": "删除成功", "error_id": error_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除问题失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"删除问题失败: {str(e)}"
        )


@router.put("/{error_id}", status_code=status.HTTP_200_OK, summary="更新错误记录")
async def update_error_record(
    error_id: int,
    update_data: ErrorUpdate,
    db: CurrentSession,
    current_user: User = Depends(get_current_user),
):
    """
    更新一条巡查问题记录

    Args:
        error_id: 要更新的问题ID
        update_data: 更新的内容
    
    Returns:
        更新结果信息
    """
    try:
        # 查询是否存在该问题
        error = await get_error_by_id(db, error_id)
        if error is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"问题ID:{error_id}不存在"
            )

        # 执行更新
        updated_error = await update_error(db, error_id, update_data)
        if not updated_error:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail="更新问题失败"
            )

        return {"success": True, "message": "更新成功", "error_id": error_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新问题失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"更新问题失败: {str(e)}"
        )


@router.get("/{error_id}", response_model=ErrorResponse, summary="获取错误详情")
async def get_error(
    error_id: int,
    db: CurrentSession,
    current_user: User = Depends(get_current_user),
):
    """
    获取错误详细信息
    
    Args:
        error_id: 错误ID
    
    Returns:
        错误详细信息
    """
    try:
        error = await get_error_by_id(db, error_id)
        if error is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"问题ID:{error_id}不存在"
            )
        return error
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取错误详情失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取错误详情失败: {str(e)}"
        )


@router.get("/users/{user_id}", response_model=List[ErrorResponse], summary="获取用户的所有错误")
async def get_user_errors(
    user_id: int,
    db: CurrentSession,
    current_user: User = Depends(get_current_user),
):
    """
    获取指定用户的所有错误记录
    
    Args:
        user_id: 用户ID
    
    Returns:
        用户的所有错误记录列表
    """
    try:
        # 检查用户是否存在
        user = await get_user_by_id(db, user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"用户ID:{user_id}不存在"
            )
            
        # 获取用户的所有错误
        errors = await get_errors_by_user_id(db, user_id)
        return errors
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取用户错误列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户错误列表失败: {str(e)}"
        )
