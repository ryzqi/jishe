from typing import Dict, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger

from models.goods import Goods
from models.stock import Stock
from crud.goods import get_all_goods
from crud.stock import get_stocks_by_warehouse


async def get_warehouse_stock_statistics(db: AsyncSession, warehouse_id: int) -> Dict[str, List]:
    """
    获取仓库库存统计数据
    
    Args:
        db: 数据库会话
        warehouse_id: 仓库ID
        
    Returns:
        Dict[str, List]: 包含货物名称和对应库存数量的字典
    """
    try:
        # 获取所有货物
        all_goods = await get_all_goods(db)
        
        # 获取仓库的所有库存记录
        stocks = await get_stocks_by_warehouse(db, warehouse_id)
        
        # 创建货物ID到库存数量的映射
        stock_map = {stock.goods_id: stock.all_count for stock in stocks}
        
        # 准备返回数据
        y_axis_data = []
        series_data = []
        
        # 遍历所有货物，获取其库存数量
        for goods in all_goods:
            y_axis_data.append(goods.goods_name)
            series_data.append(stock_map.get(goods.id, 0))
        
        return {
            "yAxisData": y_axis_data,
            "seriesData": series_data
        }
    except SQLAlchemyError as e:
        logger.error(f"获取仓库库存统计数据失败: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"处理仓库库存统计数据失败: {str(e)}")
        raise 