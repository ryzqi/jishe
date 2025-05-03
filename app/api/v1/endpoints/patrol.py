from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger

from db.database import CurrentSession
from crud.patrol import get_patrol_list, get_road_conditions, get_status_summary
from schemas.patrol import PatrolListResponse, RoadConditionResponse, StatusSummaryResponse, PatrolUpdate
from core.security import get_current_user
from models.patrol import Patrol
from sqlalchemy import select, delete
from starlette.status import HTTP_404_NOT_FOUND

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


@router.post("/", summary="新增巡查任务")
async def get_road_conditions_endpoint(
    patrol_data: PatrolUpdate,
    db: CurrentSession,
    user: str = Depends(get_current_user)
):
    # 创建 Patrol 实例
    new_patrol = Patrol(
        drone_id=patrol_data.drone_id,
        address=patrol_data.address,
        predict_fly_time=patrol_data.predict_fly_time,
        fly_start_datetime=datetime.utcnow(),  # 自动生成飞行开始时间
        update_time=datetime.utcnow(),  # 自动生成更新时间
        error_id=None  # 初始无错误
    )

    try:
        db.add(new_patrol)
        await db.commit()
        await db.refresh(new_patrol)
        logger.info(f"新增巡查记录 ID: {new_patrol.id}")
        return {"message": "新增成功", "patrol_id": new_patrol.id}
    except Exception as e:
        await db.rollback()
        logger.error(f"插入巡查记录失败: {e}")
        raise HTTPException(status_code=500, detail="新增巡查记录失败")


@router.delete("/{patrol_id}", summary="删除指定巡查记录")
async def delete_patrol_record(
    patrol_id: int,
    db: CurrentSession,
):
    # 查询该记录是否存在
    result = await db.execute(select(Patrol).where(Patrol.id == patrol_id))
    patrol = result.scalar_one_or_none()

    if patrol is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="巡查记录不存在")

    # 执行删除
    await db.execute(delete(Patrol).where(Patrol.id == patrol_id))
    await db.commit()

    return {"message": "删除成功"}