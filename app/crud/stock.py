from typing import Optional, List
from datetime import datetime
from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger

from models.stock import Stock
from schemas.stock import StockCreate, StockUpdate, StockStatisticsResponse
from models.goods import Goods


async def create_stock(db: AsyncSession, stock: StockCreate) -> Stock:
    """
    创建库存记录
    
    Args:
        db: 数据库会话
        stock: 库存创建模型
        
    Returns:
        Stock: 创建的库存对象
    """
    try:
        db_stock = Stock(
            warehouse_id=stock.warehouse_id,
            goods_id=stock.goods_id,
            all_count=stock.all_count,
            last_add_count=stock.last_add_count,
            last_add_date=datetime.now()
        )
        db.add(db_stock)
        await db.commit()
        await db.refresh(db_stock)
        return db_stock
    except SQLAlchemyError as e:
        logger.error(f"创建库存记录失败: {str(e)}")
        await db.rollback()
        raise


async def get_stock(db: AsyncSession, stock_id: int) -> Optional[Stock]:
    """
    根据ID获取库存记录
    
    Args:
        db: 数据库会话
        stock_id: 库存ID
        
    Returns:
        Stock: 找到的库存记录或None
    """
    try:
        query = select(Stock).where(Stock.id == stock_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    except SQLAlchemyError as e:
        logger.error(f"查询库存记录(ID:{stock_id})失败: {str(e)}")
        raise


async def get_stocks_by_warehouse(db: AsyncSession, warehouse_id: int) -> List[Stock]:
    """
    获取指定仓库的所有库存记录
    
    Args:
        db: 数据库会话
        warehouse_id: 仓库ID
        
    Returns:
        List[Stock]: 库存记录列表
    """
    try:
        query = select(Stock).where(Stock.warehouse_id == warehouse_id)
        result = await db.execute(query)
        return list(result.scalars().all())
    except SQLAlchemyError as e:
        logger.error(f"查询仓库(ID:{warehouse_id})的库存记录失败: {str(e)}")
        raise


async def update_stock(db: AsyncSession, stock_id: int, stock: StockUpdate) -> Optional[Stock]:
    """
    更新库存记录
    
    Args:
        db: 数据库会话
        stock_id: 库存ID
        stock: 库存更新模型
        
    Returns:
        Stock: 更新后的库存对象或None
    """
    try:
        db_stock = await get_stock(db, stock_id)
        if not db_stock:
            return None
        
        for field, value in stock.dict(exclude_unset=True).items():
            setattr(db_stock, field, value)
        
        await db.commit()
        await db.refresh(db_stock)
        return db_stock
    except SQLAlchemyError as e:
        logger.error(f"更新库存记录(ID:{stock_id})失败: {str(e)}")
        await db.rollback()
        raise


async def delete_stock(db: AsyncSession, stock_id: int) -> bool:
    """
    删除库存记录
    
    Args:
        db: 数据库会话
        stock_id: 库存ID
        
    Returns:
        bool: 是否删除成功
    """
    try:
        db_stock = await get_stock(db, stock_id)
        if not db_stock:
            return False
        
        await db.delete(db_stock)
        await db.commit()
        return True
    except SQLAlchemyError as e:
        logger.error(f"删除库存记录(ID:{stock_id})失败: {str(e)}")
        await db.rollback()
        raise


async def get_stock_statistics_by_warehouse(
    db: AsyncSession,
    warehouse_id: int
) -> StockStatisticsResponse:
    """
    获取指定仓库的库存统计数据
    
    Args:
        db: 数据库会话
        warehouse_id: 仓库ID
        
    Returns:
        StockStatisticsResponse: 包含分类、现有数据和新增数据的统计信息
    """
    # 构建查询
    query = (
        select(
            Goods.goods_name,
            Stock.all_count,
            Stock.last_add_count
        )
        .join(Stock, Stock.goods_id == Goods.id)
        .where(Stock.warehouse_id == warehouse_id)
    )
    
    # 执行查询
    result = await db.execute(query)
    rows = result.all()
    
    # 提取数据
    categories = []
    existing_data = []
    new_data = []
    
    for row in rows:
        categories.append(row.goods_name)
        existing_data.append(row.all_count)
        new_data.append(row.last_add_count)
    
    return StockStatisticsResponse(
        categories=categories,
        existingData=existing_data,
        newData=new_data
    )
