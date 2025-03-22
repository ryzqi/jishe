from typing import Optional
from pydantic import BaseModel, Field


# 共享属性
class RoleBase(BaseModel):
    """角色基础模型"""
    role_name: str = Field(..., description="角色名称")


class RoleCreate(RoleBase):
    """创建角色请求模型"""
    pass


class RoleUpdate(BaseModel):
    """更新角色请求模型"""
    role_name: Optional[str] = Field(None, description="角色名称")


class RoleResponse(RoleBase):
    """角色响应模型"""
    role_id: int = Field(..., description="角色唯一标识")
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "role_id": 1,
                "role_name": "管理员"
            }
        }
    } 