from typing import Optional

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
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "sub": "user@example.com",
                "exp": 1639858800
            }
        }
    }