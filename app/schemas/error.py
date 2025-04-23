from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


# 共享属性
class ErrorBase(BaseModel):
    """问题基础模型"""
    error_content: str = Field(..., description="问题内容")
    error_found_time: Optional[datetime] = None  # 👈 改成 Optional
    states: str = Field(..., description="问题状态: 0->待解决, 1->正在解决", min_length=1, max_length=1)
    user_id: Optional[int]
    title: str
    @field_validator("states")
    @classmethod
    def validate_states(cls, v):
        if v not in ["0", "1"]:
            raise ValueError("状态值必须是 '0' 或 '1'")
        return v


class ErrorCreate(ErrorBase):
    """创建问题请求模型"""
    pass


class ErrorUpdate(BaseModel):
    """更新问题请求模型"""
    error_content: Optional[str] = Field(None, description="问题内容")
    error_found_time: Optional[datetime] = Field(None, description="问题发现时间")
    states: Optional[str] = Field(None, description="问题状态: 0->待解决, 1->正在解决", min_length=1, max_length=1)
    title: Optional[str]
    user_id: Optional[int]

    @field_validator("states")
    @classmethod
    def validate_states(cls, v):
        if v is not None and v not in ["0", "1"]:
            raise ValueError("状态值必须是 '0' 或 '1'")
        return v


class ErrorResponse(ErrorBase):
    """问题响应模型"""
    error_id: int = Field(..., description="问题编号")
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "error_id": 1,
                "error_content": "巡查发现A区货架破损",
                "error_found_time": "2023-11-15T08:30:00",
                "states": "0"
            }
        }
    } 