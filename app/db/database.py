from typing import AsyncGenerator, Dict, Any
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
    AsyncEngine,
)
from sqlalchemy.pool import QueuePool
from loguru import logger
from contextlib import asynccontextmanager

try:
    from app.core.config import settings
except ImportError:
    # 在core.config导入失败的情况下，使用本地配置
    from pydantic_settings import BaseSettings, SettingsConfigDict
    import os

    class DatabaseSettings(BaseSettings):
        """数据库配置设置类"""
        DB_HOST: str
        DB_PORT: int
        DB_USER: str
        DB_PASSWORD: str
        DB_NAME: str
        
        model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # 从环境变量加载数据库配置
    settings = DatabaseSettings()

# 构建数据库连接URL
DATABASE_URL = (
    f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@"
    f"{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
)

# 数据库引擎配置参数
engine_kwargs: Dict[str, Any] = {
    "echo": getattr(settings, "DEBUG", False),
    "pool_size": 5,  # 连接池大小
    "max_overflow": 10,  # 最大连接溢出数
    "pool_timeout": 30,  # 获取连接超时时间
    "pool_recycle": 1800,  # 连接回收时间(30分钟)
    "pool_pre_ping": True,  # 连接前预检
    "poolclass": QueuePool,  # 使用队列池
}

# 创建异步数据库引擎
engine: AsyncEngine = create_async_engine(DATABASE_URL, **engine_kwargs)

# 创建异步会话工厂
async_session_factory = async_sessionmaker(
    engine,
    expire_on_commit=False,  # 提交后不过期对象
    autoflush=False,         # 不自动刷新
    autocommit=False,        # 不自动提交
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    依赖注入函数，用于获取数据库会话
    
    用法示例:
    ```python
    @router.get("/items/")
    async def get_items(db: AsyncSession = Depends(get_db_session)):
        result = await db.execute(select(Item))
        return result.scalars().all()
    ```
    """
    session = async_session_factory()
    try:
        logger.debug("创建新的数据库会话")
        yield session
    finally:
        logger.debug("关闭数据库会话")
        await session.close()


@asynccontextmanager
async def get_db_context() -> AsyncGenerator[AsyncSession, None]:
    """
    上下文管理器，用于获取数据库会话
    
    用法示例:
    ```python
    async with get_db_context() as db:
        result = await db.execute(select(Item))
        items = result.scalars().all()
    ```
    """
    session = async_session_factory()
    try:
        yield session
    finally:
        await session.close()


async def init_db() -> None:
    """
    数据库初始化函数
    可在应用启动时调用，执行初始化操作
    
    用法示例:
    ```python
    @app.on_event("startup")
    async def startup_db_client():
        await init_db()
    ```
    """
    try:
        # 测试数据库连接
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        logger.info("数据库连接成功")
    except Exception as e:
        logger.error(f"数据库连接失败: {str(e)}")
        raise 