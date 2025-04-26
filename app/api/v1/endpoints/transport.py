from fastapi import APIRouter, HTTPException, status, Depends
from loguru import logger
from typing import List

from db.database import CurrentSession
from schemas.transport import TransportRead, TransportCreate, TransportUpdate
from crud import transport as crud_transport
from core.security import get_current_user

router = APIRouter()


@router.post(
    "/",
    response_model=TransportRead,
    status_code=status.HTTP_201_CREATED,
    summary="创建新的运输线路",
)
async def create_transport(
        transport_in: TransportCreate,
        db: CurrentSession,
        user: str = Depends(get_current_user)
):
    """
    创建运输线路记录。
    """
    logger.info(f"接收到创建运输线路请求: {transport_in.model_dump()}")
    created_transport = await crud_transport.create_transport(db=db, transport=transport_in)
    logger.info(f"成功创建运输线路记录，ID: {created_transport.id}")
    return created_transport


@router.get(
    "/",
    response_model=List[TransportRead],
    summary="获取运输线路列表",
)
async def read_transports(
        db: CurrentSession,
        skip: int = 0,
        limit: int = 100,
        user: str = Depends(get_current_user)
):
    """
    获取运输线路列表 (支持分页)。
    """
    logger.info(f"请求运输线路列表: skip={skip}, limit={limit}")
    transports = await crud_transport.get_transports(db=db, skip=skip, limit=limit)
    logger.debug(f"查询到 {len(transports)} 条运输线路记录")
    return transports


@router.get(
    "/{transport_id}",
    response_model=TransportRead,
    summary="根据ID获取运输线路详情",
)
async def read_transport(
        transport_id: int,
        db: CurrentSession,
        user: str = Depends(get_current_user)
):
    """
    获取单个运输线路详情。
    """
    logger.info(f"请求运输线路详情，ID: {transport_id}")
    db_transport = await crud_transport.get_transport(db=db, transport_id=transport_id)
    if db_transport is None:
        logger.warning(f"运输线路记录未找到，ID: {transport_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID 为 {transport_id} 的运输记录未找到"
        )
    logger.debug(f"成功获取运输线路详情，ID: {transport_id}")
    return db_transport


@router.patch(
    "/{transport_id}",
    response_model=TransportRead,
    summary="更新指定ID的运输线路",
)
async def update_transport(
        transport_id: int,
        transport_in: TransportUpdate,
        db: CurrentSession,
        user: str = Depends(get_current_user)
):
    """
    更新运输线路记录 (部分更新)。
    """
    logger.info(f"接收到更新运输线路请求，ID: {transport_id}, 数据: {transport_in.model_dump(exclude_unset=True)}")
    # 首先检查记录是否存在
    db_transport = await crud_transport.get_transport(db=db, transport_id=transport_id)
    if db_transport is None:
        logger.warning(f"尝试更新但未找到运输线路记录，ID: {transport_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"无法更新：ID 为 {transport_id} 的运输记录未找到"
        )

    # 执行更新操作
    updated_transport = await crud_transport.update_transport(
        db=db, db_obj=db_transport, obj_in=transport_in
    )
    logger.info(f"成功更新运输线路记录，ID: {transport_id}")
    return updated_transport


@router.delete(
    "/{transport_id}",
    response_model=TransportRead,
    summary="删除指定ID的运输线路",
)
async def delete_transport(
        transport_id: int,
        db: CurrentSession,
        user: str = Depends(get_current_user)
):
    """
    删除运输线路记录。
    """
    logger.info(f"接收到删除运输线路请求，ID: {transport_id}")
    # 先尝试获取以确认存在并获取对象用于返回（如果需要）
    deleted_transport = await crud_transport.delete_transport(db=db, transport_id=transport_id)

    if deleted_transport is None:
        logger.warning(f"尝试删除但未找到运输线路记录，ID: {transport_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"无法删除：ID 为 {transport_id} 的运输记录未找到"
        )

    logger.info(f"成功删除运输线路记录，ID: {transport_id}")

    return deleted_transport
