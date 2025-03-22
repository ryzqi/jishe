from typing import Optional, List
from pydantic import BaseModel, Field, field_validator


# 共享属性
class DroneBase(BaseModel):
    """无人机基础模型"""
    drone_type: str = Field(..., description="机型")
    states: str = Field(..., description="无人机状态: 1->正常工作, 0->未工作", min_length=1, max_length=1)
    
    @field_validator("states")
    @classmethod
    def validate_states(cls, v):
        if v not in ["0", "1"]:
            raise ValueError("状态值必须是 '0' 或 '1'")
        return v


class DroneCreate(DroneBase):
    """创建无人机请求模型"""
    pass


class DroneUpdate(BaseModel):
    """更新无人机请求模型"""
    drone_type: Optional[str] = Field(None, description="机型")
    states: Optional[str] = Field(None, description="无人机状态: 1->正常工作, 0->未工作", min_length=1, max_length=1)
    
    @field_validator("states")
    @classmethod
    def validate_states(cls, v):
        if v is not None and v not in ["0", "1"]:
            raise ValueError("状态值必须是 '0' 或 '1'")
        return v


class DroneResponse(DroneBase):
    """无人机响应模型"""
    id: int = Field(..., description="无人机编号")
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "drone_type": "D-1000型",
                "states": "1"
            }
        }
    } 