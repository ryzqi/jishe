from typing import Optional, List
from pydantic import BaseModel, Field, field_serializer
from datetime import datetime, time


class LogResponse(BaseModel):
    """用户基础模型"""
    time: str = Field(..., description="时间")
    action: str = Field(..., description="活动类型")
    status: str = Field(..., description="操作状态")
