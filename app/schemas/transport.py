import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class TransportBase(BaseModel):
    """
    基础运输线路 Schema
    """

    stock: int = Field(..., description="货物量", examples=[1000])
    already_percent: int = Field(..., ge=0, le=100, description="已送达百分比 (0-100)", examples=[50])
    estimated_duration: Optional[datetime.timedelta] = Field(None, description="预估时长 (例如: '2 days, 12:30:00')", examples=["P2DT12H30M"])
    name: str = Field(..., description="运输路线名称")
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )


class TransportCreate(TransportBase):
    """
    创建运输线路 Schema
    """
    pass


class TransportUpdate(BaseModel):
    """
    更新运输线路 Schema (所有字段可选)
    """
    stock: Optional[int] = Field(None, description="货物量", examples=[1200])
    already_percent: Optional[int] = Field(None, ge=0, le=100, description="已送达百分比 (0-100)", examples=[75])
    estimated_duration: Optional[datetime.timedelta] = Field(None, description="预估时长", examples=["P3DT6H"])

    # Pydantic V2 配置
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )


class TransportRead(TransportBase):
    """
    读取/返回运输线路 Schema
    """

    id: int = Field(..., description="唯一ID", examples=[1])

    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True,
    )


class TransportId(BaseModel):
    id: int = Field(..., description="唯一ID", examples=[1])