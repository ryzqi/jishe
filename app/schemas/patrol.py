from typing import Optional, List
from datetime import datetime, time
from pydantic import BaseModel, Field


# 共享属性
class PatrolBase(BaseModel):
    """巡查记录基础模型"""
    drone_id: int = Field(..., description="无人机编号")
    address: str = Field(..., description="在寻路段")
    predict_fly_time: time = Field(..., description="预计飞行时长")
    fly_start_datetime: datetime = Field(..., description="开始飞行时间")


class PatrolCreate(PatrolBase):
    """创建巡查记录请求模型"""
    pass


class PatrolUpdate(BaseModel):
    """更新巡查记录请求模型"""
    drone_id: Optional[int] = Field(None, description="无人机编号")
    address: Optional[str] = Field(None, description="在寻路段")
    predict_fly_time: Optional[time] = Field(None, description="预计飞行时长")
    # fly_start_datetime: Optional[datetime] = Field(None, description="开始飞行时间")


class PatrolResponse(PatrolBase):
    """巡查记录响应模型"""
    id: int = Field(..., description="巡查记录唯一标识")
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "drone_id": 1,
                "address": "A区-B区",
                "predict_fly_time": "00:30:00",
                "fly_start_datetime": "2023-11-15T10:00:00"
            }
        }
    }


class PatrolInfo(BaseModel):
    """巡逻信息模型"""
    机型: str = Field(..., description="无人机型号")
    编号: int = Field(..., description="无人机编号")
    巡查路段: str = Field(..., description="巡查路段")
    状态: str = Field(..., description="工作状态")
    预计续航时长: str = Field(..., description="预计续航时长")
    已工作时长: str = Field(..., description="已工作时长")
    id: int = Field(..., description="巡查记录id")


class PatrolListResponse(BaseModel):
    """巡逻列表响应模型"""
    patrols: List[PatrolInfo]


class RoadConditionInfo(BaseModel):
    """道路状况信息模型"""
    id: str = Field(..., description="无人机编号")
    time: str = Field(..., description="更新时间")
    status: str = Field(..., description="道路状况")


class RoadConditionResponse(BaseModel):
    """道路状况响应模型"""
    conditions: List[RoadConditionInfo]


class StatusSummaryResponse(BaseModel):
    """状态统计响应模型"""
    total: int
    flying: int
    inspecting: int
    issuesFound: int
    pendingIssues: int
    solvingIssues: int


class ErrorUpdateResponse(BaseModel):
    id: int
    sender: str
    user_id: int
    title: str
    content: str
    createTime: str
    status: str