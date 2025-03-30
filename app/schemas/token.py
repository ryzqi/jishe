from typing import Optional, List

from pydantic import BaseModel


class Token(BaseModel):
    """
    OAuth2 令牌响应模型
    """
    access_token: str
    token_type: str = "bearer"
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }
    }


class TokenPayload(BaseModel):
    """
    令牌数据模型
    """
    sub: Optional[str] = None
    exp: int  # 过期时间戳
    roles: Optional[List[int]] = None  # 用户角色ID列表
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "sub": "1",
                "exp": 1639858800,
                "roles": [1]
            }
        }
    }


class LoginRequest(BaseModel):
    """
    登录请求模型
    """
    username: str
    password: str
    role_name: str
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "username": "admin",
                "password": "123456",
                "role_name": "Super Admin"
            }
        }
    }