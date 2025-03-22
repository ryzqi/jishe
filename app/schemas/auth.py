from pydantic import BaseModel, Field, EmailStr


class LoginRequest(BaseModel):
    """
    用户登录请求模型
    """
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "username": "admin",
                "password": "password123"
            }
        }
    } 