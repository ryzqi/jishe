from typing import Optional
from pydantic import BaseModel, Field


# 共享属性
class UserRoleBase(BaseModel):
    """
    用户角色关系基础模型
    """
    user_id: int = Field(..., description="用户ID")
    role_id: int = Field(..., description="角色ID")


class UserRoleCreate(UserRoleBase):
    """
    创建用户角色关系请求模型
    """
    pass


class UserRoleResponse(UserRoleBase):
    """
    用户角色关系响应模型
    """
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "user_id": 1,
                "role_id": 1
            }
        }
    } 