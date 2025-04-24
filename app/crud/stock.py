from typing import Optional, List
from datetime import datetime
from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger
from fastapi import HTTPException, status

from models.stock import Stock
from schemas.stock import StockCreate, StockUpdate, StockStatisticsResponse
from models.goods import Goods


async def check_stock_exists(db: AsyncSession, warehouse_id: int, goods_id: int) -> Optional[Stock]:
    """
    检查指定仓库和商品组合的库存记录是否已存在
    
    Args:
        db: 数据库会话
        warehouse_id: 仓库ID
        goods_id: 商品ID
        
    Returns:
        Stock: 存在的库存记录或None
    """
    try:
        query = select(Stock).where(
            Stock.warehouse_id == warehouse_id,
            Stock.goods_id == goods_id
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()
    except SQLAlchemyError as e:
        logger.error(f"检查库存记录是否存在失败: {str(e)}")
        raise


async def create_stock(db: AsyncSession, stock: StockCreate) -> Stock:
    """
    创建库存记录
    
    Args:
        db: 数据库会话
        stock: 库存创建模型
        
    Returns:
        Stock: 创建的库存对象
        
    Raises:
        HTTPException: 当仓库和商品组合已存在时抛出异常
    """
    try:
        # 检查该仓库和商品组合是否已存在
        existing_stock = await check_stock_exists(db, stock.warehouse_id, stock.goods_id)
        if existing_stock:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"仓库ID {stock.warehouse_id} 和商品ID {stock.goods_id} 的库存记录已存在，请使用更新接口"
            )
        
        # 使用当前时间作为last_add_date
        current_time = datetime.now()
        
        db_stock = Stock(
            warehouse_id=stock.warehouse_id,
            goods_id=stock.goods_id,
            all_count=stock.all_count,
            last_add_count=stock.last_add_count,
            last_add_date=current_time
        )
        db.add(db_stock)
        await db.commit()
        await db.refresh(db_stock)
        
        # 增加last_add_time字段以便与Schema匹配
        setattr(db_stock, "last_add_time", db_stock.last_add_date)
        
        return db_stock
    except HTTPException:
        raise
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
        stock = result.scalar_one_or_none()
        
            
        return stock
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
        stocks = list(result.scalars().all())
        
        # 为每个库存记录设置last_add_time以便与Schema匹配
        for stock in stocks:
            setattr(stock, "last_add_time", stock.last_add_date)
            
        return stocks
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
        
        update_data = stock.dict(exclude_unset=True)
        
        # 检查是否提供了last_add_count，如果有则更新all_count
        if "last_add_count" in update_data:
            # 提取last_add_count值
            last_add_count = update_data["last_add_count"]
            
            # 计算新的总库存量
            new_all_count = db_stock.all_count + last_add_count
            
            # 确保total_count不小于0
            if new_all_count < 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="库存不足"
                )
            
            # 更新all_count
            update_data["all_count"] = new_all_count
            
            # 更新last_add_date
            update_data["last_add_date"] = datetime.now()
        
        for field, value in update_data.items():
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
