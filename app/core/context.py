from contextlib import asynccontextmanager
from loguru import logger

from app.core.config import settings


@asynccontextmanager
async def app_lifespan_context(app):
    """
    应用生命周期上下文管理器
    
    启动时初始化资源，结束时释放资源
    
    Args:
        app: FastAPI应用实例
    """
    # 启动时执行的操作
    logger.info(f"正在启动 {settings.APP_NAME}")
    

    
    # 提供应用上下文
    yield
    
    # 关闭时执行的操作
    logger.info(f"正在关闭 {settings.APP_NAME}") 