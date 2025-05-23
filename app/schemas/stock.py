from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


# 共享属性
class StockBase(BaseModel):
    """库存基础模型"""
    warehouse_id: int = Field(..., description="仓库唯一标识")
    goods_id: int = Field(..., description="货物种类唯一标识")
    all_count: int = Field(..., description="总库存量", ge=0)
    last_add_count: int = Field(..., description="新增库存量")
    last_add_date: Optional[datetime] = None


class StockCreate(BaseModel):
    """创建库存请求模型"""
    goods_name: str = Field(..., description="新增材料种类")
    warehouse_id: int = Field(..., description="仓库唯一标识")
    all_count: int = Field(..., description="总库存量", ge=0)
    last_add_count: int = Field(..., description="新增库存量")
    last_add_date: Optional[datetime] = None


class StockUpdate(StockBase):
    """更新库存请求模型"""
    warehouse_id: Optional[int] = Field(None, description="仓库唯一标识")
    goods_id: Optional[int] = Field(None, description="货物种类唯一标识")
    all_count: Optional[int] = Field(None, description="总库存量", ge=0)
    last_add_count: Optional[int] = Field(None, description="新增库存量（可以为负数表示减少库存）")
    last_add_date: Optional[datetime] = Field(None, description="新增库存时间")


class StockResponse(StockBase):
    """库存响应模型"""
    id: int = Field(..., description="库存唯一标识")
    last_add_date: Optional[datetime] = None
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "warehouse_id": 1,
                "goods_id": 1,
                "all_count": 100,
                "last_add_count": 20,
                "last_add_date": "2023-11-15T14:30:00"
            }
        }
    }


class StockStatisticsResponse(BaseModel):
    categories: List[str]
    existingData: List[int]
    newData: List[int] 