from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger

from app.db.database import CurrentSession
from app.crud.patrol import get_patrol_list, get_road_conditions, get_status_summary, get_all_errors_with_user_info
from app.schemas.patrol import PatrolListResponse, RoadConditionResponse, StatusSummaryResponse, ErrorUpdateResponse
from app.core.security import get_current_user


router = APIRouter()


@router.get("/list", response_model=PatrolListResponse, summary="获取巡逻列表")
async def get_patrol_list_endpoint(
    db: CurrentSession,
    user: str = Depends(get_current_user)
) -> PatrolListResponse:
    """
    获取所有巡逻信息列表
    
    - **user**: 当前登录用户
    
    返回:
    - patrols: 巡逻信息列表，包含：
      - 机型: 无人机型号
      - 编号: 无人机编号
      - 巡查路段: 巡查路段
      - 状态: 工作状态（正常工作/未工作）
      - 预计续航时长: 预计续航时长
      - 已工作时长: 已工作时长
    """
    try:
        patrols = await get_patrol_list(db)
        return PatrolListResponse(patrols=patrols)
    except Exception as e:
        logger.error(f"获取巡逻列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取巡逻列表失败"
        )


@router.get("/road-conditions", response_model=RoadConditionResponse, summary="获取道路状况")
async def get_road_conditions_endpoint(
    db: CurrentSession,
    user: str = Depends(get_current_user)
) -> RoadConditionResponse:
    """
    获取道路状况信息
    
    - **user**: 当前登录用户
    
    返回:
    - conditions: 道路状况列表，包含：
      - id: 巡查路段
      - time: 更新时间
      - status: 道路状况
    """
    try:
        conditions = await get_road_conditions(db)
        return RoadConditionResponse(conditions=conditions)
    except Exception as e:
        logger.error(f"获取道路状况失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取道路状况失败"
        )


@router.get("/status-summary", response_model=StatusSummaryResponse, summary="获取状态统计")
async def get_status_summary_endpoint(
    db: CurrentSession,
    user: str = Depends(get_current_user)
) -> StatusSummaryResponse:
    """
    获取系统状态统计信息
    
    - **user**: 当前登录用户
    
    返回:
    - total: 无人机总数
    - flying: 飞行中的无人机数量
    - inspecting: 巡检记录总数
    - issuesFound: 错误总数
    - pendingIssues: 待处理错误数量
    - solvingIssues: 处理中的错误数量
    """
    try:
        summary = await get_status_summary(db)
        return summary
    except Exception as e:
        logger.error(f"获取状态统计信息失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取状态统计信息失败"
        )


@router.get("/error_update", response_model=List[ErrorUpdateResponse], summary="获取状态统计")
async def get_error_update(
        db: CurrentSession,
        user: str = Depends(get_current_user)
) -> List[ErrorUpdateResponse]:
    """
    """
    try:
        return await get_all_errors_with_user_info(db)
    except Exception as e:
        logger.error(f"获取统计信息失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取状态统计信息失败"
        )