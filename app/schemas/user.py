from typing import Optional, List
from pydantic import BaseModel, Field


# 共享属性
class UserBase(BaseModel):
    """用户基础模型"""
    username: str = Field(..., description="用户名", min_length=3, max_length=50)


class UserCreate(UserBase):
    """创建用户请求模型"""
    password: str = Field(..., description="用户密码", min_length=6)


class UserUpdate(BaseModel):
    """更新用户请求模型"""
    username: Optional[str] = Field(None, description="用户名", min_length=3, max_length=50)
    password: Optional[str] = Field(None, description="用户密码", min_length=6)


class UserResponse(UserBase):
    """用户响应模型"""
    id: int = Field(..., description="用户唯一标识")
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "username": "admin"
            }
        }
    }


class UserInDB(UserResponse):
    """数据库中的用户模型，包含敏感信息"""
    password: str 