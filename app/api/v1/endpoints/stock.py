from typing import Dict, List
from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger

from app.db.database import CurrentSession
from app.service.warehouse_service import get_warehouse_stock_statistics
from app.schemas.stock import (
    StockCreate,
    StockUpdate,
    StockResponse,
    StockStatisticsResponse
)
from app.crud.stock import (
    create_stock,
    get_stock,
    get_stocks_by_warehouse,
    update_stock,
    delete_stock,
    get_stock_statistics_by_warehouse
)
from app.core.security import get_current_user
from app.models.user import User


router = APIRouter()


# @router.post("/", response_model=StockResponse, status_code=status.HTTP_201_CREATED, summary="创建库存记录")
# async def create_stock_endpoint(
#     db: CurrentSession,
#     stock: StockCreate,
#     user: str = Depends(get_current_user)
# ):
#     """创建库存记录"""
#     try:
#         return await create_stock(db, stock)
#     except Exception as e:
#         logger.error(f"创建库存记录失败: {str(e)}")
#         raise HTTPException(status_code=500, detail="创建库存记录失败")
#
#
# @router.get("/{stock_id}", response_model=StockResponse, summary="获取指定库存记录")
# async def get_stock_endpoint(
#     db: CurrentSession,
#     stock_id: int,
#     current_user: User = Depends(get_current_user)
# ):
#     """获取指定库存记录"""
#     try:
#         stock = await get_stock(db, stock_id)
#         if not stock:
#             raise HTTPException(status_code=404, detail="库存记录不存在")
#         return stock
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"获取库存记录失败: {str(e)}")
#         raise HTTPException(status_code=500, detail="获取库存记录失败")
#
#
# @router.get("/warehouse/{warehouse_id}", response_model=List[StockResponse], summary="获取仓库库存记录")
# async def get_warehouse_stocks_endpoint(
#     db: CurrentSession,
#     warehouse_id: int,
#     current_user: User = Depends(get_current_user)
# ):
#     """获取指定仓库的所有库存记录"""
#     try:
#         return await get_stocks_by_warehouse(db, warehouse_id)
#     except Exception as e:
#         logger.error(f"获取仓库库存记录失败: {str(e)}")
#         raise HTTPException(status_code=500, detail="获取仓库库存记录失败")
#
#
# @router.put("/{stock_id}", response_model=StockResponse, summary="更新库存记录")
# async def update_stock_endpoint(
#     db: CurrentSession,
#     stock_id: int,
#     stock: StockUpdate,
#     current_user: User = Depends(get_current_user)
# ):
#     """更新库存记录"""
#     try:
#         updated_stock = await update_stock(db, stock_id, stock)
#         if not updated_stock:
#             raise HTTPException(status_code=404, detail="库存记录不存在")
#         return updated_stock
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"更新库存记录失败: {str(e)}")
#         raise HTTPException(status_code=500, detail="更新库存记录失败")
#
#
# @router.delete("/{stock_id}", status_code=status.HTTP_204_NO_CONTENT, summary="删除库存记录")
# async def delete_stock_endpoint(
#     db: CurrentSession,
#     stock_id: int,
#     current_user: User = Depends(get_current_user)
# ):
#     """删除库存记录"""
#     try:
#         success = await delete_stock(db, stock_id)
#         if not success:
#             raise HTTPException(status_code=404, detail="库存记录不存在")
#         return None
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"删除库存记录失败: {str(e)}")
#         raise HTTPException(status_code=500, detail="删除库存记录失败")


@router.get("/warehouse/{warehouse_id}/statistics", summary="获取仓库库存统计")
async def get_warehouse_statistics(
    warehouse_id: int,
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
        if statistics["yAxisData"] and len(statistics["yAxisData"]) > 5:
            statistics["yAxisData"] = statistics["yAxisData"][:5]
            statistics["seriesData"] = statistics["seriesData"][:5]
            
        return statistics
    except Exception as e:
        logger.error(f"获取仓库统计信息失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取仓库统计信息失败"
        )


@router.get("/warehouse/{warehouse_id}/goods-statistics", response_model=StockStatisticsResponse, summary="获取仓库货物统计")
async def get_warehouse_goods_statistics(
    warehouse_id: int,
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
        if len(statistics.categories) > 5:
            statistics.categories = statistics.categories[:5]
            statistics.existingData = statistics.existingData[:5]
            statistics.newData = statistics.newData[:5]
            
        return statistics
    except Exception as e:
        logger.error(f"获取仓库货物统计信息失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取仓库货物统计信息失败"
        )

