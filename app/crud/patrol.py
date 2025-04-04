from typing import List

from sqlalchemy import select, func, and_, distinct
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from app.models import User
from app.models.patrol import Patrol
from app.models.drone import Drone
from app.models.error import Error
from app.schemas.patrol import PatrolInfo, RoadConditionInfo, StatusSummaryResponse, ErrorUpdateResponse
from loguru import logger


def format_timedelta(td: timedelta) -> str:
    """将timedelta格式化为HH:MM:SS字符串"""
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


async def get_patrol_list(db: AsyncSession) -> list[PatrolInfo]:
    """
    获取巡逻列表信息
    
    Args:
        db: 数据库会话
        
    Returns:
        list[PatrolInfo]: 巡逻信息列表
    """
    # 构建查询
    query = (
        select(
            Drone.drone_type,
            Drone.id.label('drone_id'),
            Patrol.address,
            Drone.states,
            Patrol.predict_fly_time,
            Patrol.fly_start_datetime
        )
        .join(Patrol, Patrol.drone_id == Drone.id)
    )

    # 执行查询
    result = await db.execute(query)
    rows = result.all()

    # 处理数据
    patrols = []
    current_time = datetime.now()

    for row in rows:
        # 打印状态值，用于调试
        logger.debug(f"Drone ID: {row.drone_id}, States: {row.states}, Type: {type(row.states)}")

        # 计算已工作时长
        if row.fly_start_datetime:
            work_duration = current_time - row.fly_start_datetime
            work_time = format_timedelta(work_duration)
        else:
            work_time = "00:00:00"

        # 转换状态
        try:
            # 确保states是整数类型
            states = int(row.states)
            state = "正常工作" if states == 1 else "未工作"
        except (ValueError, TypeError):
            # 如果转换失败，记录错误并使用默认值
            logger.error(f"Invalid states value for drone {row.drone_id}: {row.states}")
            state = "未工作"

        logger.debug(f"Converted state: {state}")

        # 格式化预计飞行时间
        predict_time = str(row.predict_fly_time)
        if len(predict_time) == 5:  # 如果格式是 HH:MM
            predict_time = f"{predict_time}:00"

        patrols.append(PatrolInfo(
            机型=row.drone_type,
            编号=row.drone_id,
            巡查路段=row.address,
            状态=state,
            预计续航时长=predict_time,
            已工作时长=work_time
        ))

    return patrols


async def get_road_conditions(db: AsyncSession) -> list[RoadConditionInfo]:
    """
    获取道路状况信息
    
    Args:
        db: 数据库会话
        
    Returns:
        list[RoadConditionInfo]: 道路状况信息列表
    """
    # 构建子查询，获取每个无人机最新的记录
    subquery = (
        select(
            Patrol.drone_id,
            func.max(Patrol.update_time).label('max_time')
        )
        .group_by(Patrol.drone_id)
        .subquery()
    )

    # 构建主查询，使用DISTINCT确保数据不重复
    query = (
        select(
            Patrol.drone_id,
            Patrol.address,  # 添加address字段
            Patrol.update_time,
            Patrol.error_id,
            Error.error_content
        )
        .join(subquery,
              and_(
                  Patrol.drone_id == subquery.c.drone_id,
                  Patrol.update_time == subquery.c.max_time
              )
              )
        .outerjoin(Error, Patrol.error_id == Error.error_id)  # 修改连接条件，使用error_id
        .distinct(Patrol.drone_id)  # 使用distinct确保每个无人机只返回一条记录
        .order_by(Patrol.drone_id)
    )

    # 打印SQL语句用于调试
    compiled_sql = str(query.compile(compile_kwargs={"literal_binds": True}))
    logger.debug(f"执行的SQL: {compiled_sql}")

    try:
        # 执行查询
        result = await db.execute(query)
        rows = result.all()
        logger.debug(f"数据库查询返回的结果: {rows}")

        # 处理数据
        conditions = []

        for row in rows:
            # 格式化时间
            time_str = row.update_time.strftime("%H:%M:%S") if row.update_time else "00:00:00"

            # 判断状态
            if row.error_id is None:
                status = "正常"
            else:
                # 打印错误信息用于调试
                logger.info(f"Error ID: {row.error_id}, Error Content: {row.error_content}")
                status = row.error_content if row.error_content else "未知错误"

            conditions.append(RoadConditionInfo(
                id=row.address,  # 使用address作为id
                time=time_str,
                status=status
            ))

        # 打印巡检状态信息
        logger.debug("巡检状态信息:")
        for condition in conditions:
            logger.debug(f"巡查路段: {condition.id}, 时间: {condition.time}, 状态: {condition.status}")

        return conditions
    except Exception as e:
        logger.error(f"获取道路状况失败: {str(e)}")
        raise


async def get_status_summary(db: AsyncSession) -> StatusSummaryResponse:
    """
    获取状态统计信息
    
    Args:
        db: 数据库会话
        
    Returns:
        StatusSummaryResponse: 状态统计信息
    """
    try:
        # 获取无人机总数
        total_query = select(func.count(Drone.id))
        total_result = await db.execute(total_query)
        total = total_result.scalar()

        # 获取飞行中的无人机数量
        flying_query = select(func.count(Drone.id)).where(Drone.states == '1')
        flying_result = await db.execute(flying_query)
        flying = flying_result.scalar()

        # 获取巡检记录总数
        inspecting_query = select(func.count(Patrol.id))
        inspecting_result = await db.execute(inspecting_query)
        inspecting = inspecting_result.scalar()

        # 获取错误总数
        issues_found_query = select(func.count(Error.error_id))
        issues_found_result = await db.execute(issues_found_query)
        issues_found = issues_found_result.scalar()

        # 获取待处理错误数量
        pending_issues_query = select(func.count(Error.error_id)).where(Error.states == '0')
        pending_issues_result = await db.execute(pending_issues_query)
        pending_issues = pending_issues_result.scalar()

        # 获取处理中的错误数量
        solving_issues_query = select(func.count(Error.error_id)).where(Error.states == '1')
        solving_issues_result = await db.execute(solving_issues_query)
        solving_issues = solving_issues_result.scalar()

        return StatusSummaryResponse(
            total=total,
            flying=flying,
            inspecting=inspecting,
            issuesFound=issues_found,
            pendingIssues=pending_issues,
            solvingIssues=solving_issues
        )
    except Exception as e:
        logger.error(f"获取状态统计信息失败: {str(e)}")
        raise


async def get_all_errors_with_user_info(db: AsyncSession) -> List[ErrorUpdateResponse]:
    # 查询 error 关联 user1 的 name 字段
    stmt = (
        select(
            Error.error_id.label("id"),
            User.name.label("sender"),
            Error.error_content.label("content"),
            Error.error_found_time.label("createTime"),
            Error.states.label("raw_status"),
            Error.title.label("title")
        )
        .join(User, Error.user_id == User.id)
    )

    results = await db.execute(stmt)

    # 转换成响应结构
    response_list = []
    for row in results:
        status = "待处理" if row.raw_status == "0" else "已处理"
        # 转换时间格式为 'YYYY-MM-DD HH:MM:SS'
        formatted_time = row.createTime.strftime("%Y-%m-%d %H:%M:%S")
        response = ErrorUpdateResponse(
            id=row.id,
            sender=row.sender,
            title=row.title,
            content=row.content,
            createTime=formatted_time,
            status=status
        )
        response_list.append(response)
    return response_list
