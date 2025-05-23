from typing import List, Optional, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    应用配置设置类
    """
    # API配置
    API_V1_STR: str = "/api/v1"

    # 应用配置
    APP_NAME: str
    APP_ENV: str
    DEBUG: bool = False

    # 安全配置
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # 数据库配置
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Redis配置
    REDIS_HOST: Optional[str] = None
    REDIS_PORT: Optional[int] = None
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: Optional[int] = None

    # CORS配置
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    # Gemini API配置
    GEMINI_API_KEY: str

    # 高德地图 API配置
    GAODE_API_KEY: str

    # 华为云配置
    HUAWEICLOUD_SDK_AK: str
    HUAWEICLOUD_SDK_SK: str

    # aliyunOSS配置
    OSS_ACCESS_KEY_ID: str
    OSS_ACCESS_KEY_SECRET: str
    OSS_ENDPOINT: str
    OSS_BUCKET_NAME: str

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    def get_db_uri(self) -> str:
        """
        获取数据库连接URI
        """
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


# 创建全局配置实例
settings = Settings()
