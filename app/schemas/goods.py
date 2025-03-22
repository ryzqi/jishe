from typing import Optional
from pydantic import BaseModel, Field


# 共享属性
class GoodsBase(BaseModel):
    """货物基础模型"""
    goods_name: str = Field(..., description="货物种类名称")


class GoodsCreate(GoodsBase):
    """创建货物请求模型"""
    pass


class GoodsUpdate(BaseModel):
    """更新货物请求模型"""
    goods_name: Optional[str] = Field(None, description="货物种类名称")


class GoodsResponse(GoodsBase):
    """货物响应模型"""
    id: int = Field(..., description="货物种类唯一标识")
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "goods_name": "电子产品"
            }
        }
    } 