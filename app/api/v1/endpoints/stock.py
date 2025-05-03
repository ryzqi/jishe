from typing import Dict, List
from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from sqlalchemy import select, delete
from db.database import CurrentSession
from service.warehouse_service import get_warehouse_stock_statistics
from schemas.stock import (
    StockCreate,
    StockUpdate,
    StockResponse,
    StockStatisticsResponse
)
from schemas import RoomsResponse, StreamUrlRequest
from crud.stock import (
    create_stock,
    get_stock,
    get_stocks_by_warehouse,
    update_stock,
    delete_stock,
    get_stock_statistics_by_warehouse,
    check_stock_exists
)
from core.security import get_current_user
from models.user import User
from models import Rooms
from models import StreamConfig


router = APIRouter()


@router.post("/stock", response_model=StockResponse, status_code=status.HTTP_201_CREATED, summary="创建库存")
async def create_stock_endpoint(
    stock_data: StockCreate,
    db: CurrentSession,
    user: str = Depends(get_current_user)
) -> StockResponse:
    """
    创建新的库存记录
    
    - **warehouse_id**: 仓库ID
    - **goods_id**: 商品ID
    - **all_count**: 总库存量
    - **last_add_count**: 新增库存量
    - **user**: 当前登录用户
    """
    try:
        new_stock = await create_stock(db, stock_data)
        return new_stock
    except Exception as e:
        logger.error(f"创建库存失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"创建库存失败: {str(e)}"
        )


@router.put("/stock/{stock_id}", response_model=StockResponse, summary="更新库存")
async def update_stock_endpoint(
    stock_id: int,
    stock_data: StockUpdate,
    db: CurrentSession,
    user: str = Depends(get_current_user)
) -> StockResponse:
    """
    更新指定ID的库存记录
    
    - **stock_id**: 库存ID
    - **stock_data**: 更新的库存数据，推荐只提供last_add_count字段
      - last_add_count: 新增库存量（可以为负数表示减少库存）
    - **user**: 当前登录用户
    
    注意：
    - 如果提供了last_add_count，系统会自动计算新的总库存量(all_count = 原all_count + last_add_count)
    - 如果计算后的all_count小于0，将被设置为0
    """
    try:
        updated_stock = await update_stock(db, stock_id, stock_data)
        if not updated_stock:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"库存ID {stock_id} 不存在"
            )
        return updated_stock
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新库存失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"更新库存失败: {str(e)}"
        )


@router.put("/warehouse/{warehouse_id}/goods/{goods_id}/stock", response_model=StockResponse, summary="根据仓库ID和商品ID更新库存")
async def update_stock_by_warehouse_goods_endpoint(
    warehouse_id: int,
    goods_id: int,
    stock_data: StockUpdate,
    db: CurrentSession,
    user: str = Depends(get_current_user)
) -> StockResponse:
    """
    根据仓库ID和商品ID更新库存记录
    
    - **warehouse_id**: 仓库ID
    - **goods_id**: 商品ID
    - **stock_data**: 更新的库存数据，推荐只提供last_add_count字段
      - last_add_count: 新增库存量（可以为负数表示减少库存）
    - **user**: 当前登录用户
    
    注意：
    - 如果提供了last_add_count，系统会自动计算新的总库存量(all_count = 原all_count + last_add_count)
    - 如果计算后的all_count小于0，将被设置为0
    """
    try:
        # 查找库存记录
        existing_stock = await check_stock_exists(db, warehouse_id, goods_id)
        if not existing_stock:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"仓库ID {warehouse_id} 和商品ID {goods_id} 的库存记录不存在"
            )
        
        # 更新库存记录
        updated_stock = await update_stock(db, existing_stock.id, stock_data)
        return updated_stock
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新库存失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"更新库存失败: {str(e)}"
        )


@router.delete("/stock/{stock_id}", status_code=status.HTTP_204_NO_CONTENT, summary="删除库存")
async def delete_stock_endpoint(
    stock_id: int,
    db: CurrentSession,
    user: str = Depends(get_current_user)
):
    """
    删除指定ID的库存记录
    
    - **stock_id**: 库存ID
    - **user**: 当前登录用户
    """
    try:
        deleted = await delete_stock(db, stock_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"库存ID {stock_id} 不存在"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除库存失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"删除库存失败: {str(e)}"
        )


@router.get("/warehouse/{warehouse_id}/statistics/{count}", summary="获取仓库库存统计")
async def get_warehouse_statistics(
        warehouse_id: int,
        count: int,
        db: CurrentSession,
        user: str = Depends(get_current_user)
) -> Dict[str, List]:
    """
    获取指定仓库的库存统计信息
    
    - **warehouse_id**: 仓库ID
    - **user**: 当前登录用户
    """
    try:
        # 获取统计信息
        statistics = await get_warehouse_stock_statistics(db, warehouse_id)

        # 限制每个列表的数据数量不超过5个
        if statistics["yAxisData"] and len(statistics["yAxisData"]) > count:
            statistics["yAxisData"] = statistics["yAxisData"][:count]
            statistics["seriesData"] = statistics["seriesData"][:count]

        return statistics
    except Exception as e:
        logger.error(f"获取仓库统计信息失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取仓库统计信息失败"
        )


@router.get("/warehouse/{warehouse_id}/goods-statistics/{count}", response_model=StockStatisticsResponse,
            summary="获取仓库货物统计")
async def get_warehouse_goods_statistics(
        warehouse_id: int,
        count: int,
        db: CurrentSession,
        user: str = Depends(get_current_user)
) -> StockStatisticsResponse:
    """
    获取指定仓库的货物统计信息
    
    - **warehouse_id**: 仓库ID
    - **user**: 当前登录用户
    
    返回:
    - categories: 货物名称列表（最多5个）
    - existingData: 总库存量列表（最多5个）
    - newData: 新增库存量列表（最多5个）
    """
    try:
        statistics = await get_stock_statistics_by_warehouse(db, warehouse_id)

        # 限制每个列表的数据数量不超过5个
        if len(statistics.categories) > count:
            statistics.categories = statistics.categories[:count]
            statistics.existingData = statistics.existingData[:count]
            statistics.newData = statistics.newData[:count]

        return statistics
    except Exception as e:
        logger.error(f"获取仓库货物统计信息失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取仓库货物统计信息失败"
        )


@router.get("/stock/{stock_id}", response_model=StockResponse, summary="获取单个库存")
async def get_stock_endpoint(
    stock_id: int,
    db: CurrentSession,
    user: str = Depends(get_current_user)
) -> StockResponse:
    """
    获取指定ID的库存详细信息
    
    - **stock_id**: 库存ID
    - **user**: 当前登录用户
    """
    try:
        stock = await get_stock(db, stock_id)
        if not stock:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"库存ID {stock_id} 不存在"
            )
        return stock
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取库存详情失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取库存详情失败: {str(e)}"
        )


@router.get("/warehouse/{warehouse_id}/goods/{goods_id}/stock", response_model=StockResponse, summary="根据仓库ID和商品ID获取库存")
async def get_stock_by_warehouse_goods_endpoint(
    warehouse_id: int,
    goods_id: int,
    db: CurrentSession,
    user: str = Depends(get_current_user)
) -> StockResponse:
    """
    根据仓库ID和商品ID获取库存记录
    
    - **warehouse_id**: 仓库ID
    - **goods_id**: 商品ID
    - **user**: 当前登录用户
    """
    try:
        stock = await check_stock_exists(db, warehouse_id, goods_id)
        if not stock:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"仓库ID {warehouse_id} 和商品ID {goods_id} 的库存记录不存在"
            )
        return stock
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取库存详情失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取库存详情失败: {str(e)}"
        )


@router.get("/warehouse/{warehouse_id}/stocks", summary="获取仓库所有库存")
async def get_warehouse_stocks(
    warehouse_id: int,
    db: CurrentSession,
    user: str = Depends(get_current_user)
):
    """
    获取指定仓库的所有库存记录
    
    - **warehouse_id**: 仓库ID
    - **user**: 当前登录用户
    """
    try:
        stocks = await get_stocks_by_warehouse(db, warehouse_id)
        return stocks
    except Exception as e:
        logger.error(f"获取仓库库存列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取仓库库存列表失败: {str(e)}"
        )


@router.get("/rooms", summary="获取仓库平面图数据", response_model=List[RoomsResponse])
async def get_rooms(
        db: CurrentSession,
        user: str = Depends(get_current_user)
) -> List[RoomsResponse]:
    result = await db.execute(select(Rooms))  # 使用异步查询方式
    rooms = result.scalars().all()
    return rooms


@router.get("/url", summary="获取实时视频的url")
async def get_url(
        db: CurrentSession,
        user: str = Depends(get_current_user)
):
    result = await db.execute(select(StreamConfig))  # 使用异步查询方式
    url = result.scalars().all()
    return url


@router.post("/url", summary="修改实时视频的url")
async def post_url(
    db: CurrentSession,
    stream_url_request: StreamUrlRequest
):
    # Step 1: 删除数据库中所有的 StreamConfig 数据
    await db.execute(delete(StreamConfig))  # 使用 delete 来删除 StreamConfig 表的所有数据
    await db.commit()  # 提交事务以应用删除操作

    # Step 2: 插入新的 stream_url
    new_stream_config = StreamConfig(stream_url=stream_url_request.stream_url)
    db.add(new_stream_config)
    await db.commit()  # 提交事务以保存新的数据

    return {"message": "Stream URL updated successfully"}