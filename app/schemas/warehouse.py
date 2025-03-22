from typing import Optional
from pydantic import BaseModel, Field


# 共享属性
class WarehouseBase(BaseModel):
    """仓库基础模型"""
    warehouse_name: str = Field(..., description="仓库名称")
    states: str = Field(..., description="仓库状态: 正常,异常情况")


class WarehouseCreate(WarehouseBase):
    """创建仓库请求模型"""
    pass


class WarehouseUpdate(BaseModel):
    """更新仓库请求模型"""
    warehouse_name: Optional[str] = Field(None, description="仓库名称")
    states: Optional[str] = Field(None, description="仓库状态: 正常,异常情况")


class WarehouseResponse(WarehouseBase):
    """仓库响应模型"""
    id: int = Field(..., description="仓库唯一标识")
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "warehouse_name": "中央仓库",
                "states": "正常"
            }
        }
    } 