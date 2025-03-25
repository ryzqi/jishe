from fastapi import Depends
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy import URL, event
from loguru import logger
from typing import Annotated, AsyncGenerator
import sys
import asyncio
from app.core.config import settings


def create_engine_and_session(url: str | URL):
    try:
        # 数据库引擎 - 优化连接配置
        engine = create_async_engine(
            url, 
            future=True, 
            echo=settings.DEBUG,
            pool_pre_ping=True,      # 自动检测断开的连接
            pool_recycle=1800,       # 30分钟回收连接
            pool_size=5,             # 连接池大小
            max_overflow=10,         # 最大允许溢出的连接数
            pool_timeout=30,         # 连接池获取超时
            connect_args={
                "timeout": 30,       # 连接超时30秒
                "command_timeout": 30,  # 命令超时30秒
            }
        )
        logger.success("数据库连接成功")
    except Exception as e:
        logger.error("❌ 数据库链接失败: {}", e)
        sys.exit()
    else:
        db_session = async_sessionmaker(
            bind=engine, 
            autoflush=False, 
            expire_on_commit=False,
            class_=AsyncSession
        )
        return engine, db_session


SQLALCHEMY_DATABASE_URL = URL.create(
    "postgresql+asyncpg",
    username=settings.DB_USER,
    password=settings.DB_PASSWORD,
    host=settings.DB_HOST,
    port=settings.DB_PORT,
    database=settings.DB_NAME,
)

async_engine, async_db_session = create_engine_and_session(SQLALCHEMY_DATABASE_URL)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话的异步生成器
    
    每个请求创建独立的会话，处理完毕后关闭
    """
    session = async_db_session()
    try:
        # 设置会话超时较长，确保有足够时间完成操作
        await asyncio.wait_for(session.connection(), timeout=10.0)
        yield session
    except asyncio.TimeoutError:
        logger.error("数据库连接超时")
        await session.close()
        # 创建新的会话重试
        new_session = async_db_session()
        yield new_session
    except Exception as se:
        logger.error("数据库会话错误，执行回滚: {}", se)
        try:
            await session.rollback()
        except Exception as rollback_error:
            logger.error("回滚失败: {}", rollback_error)
        raise se
    finally:
        try:
            logger.debug("关闭数据库会话")
            await session.close()
        except Exception as close_error:
            logger.error("关闭会话失败: {}", close_error)


# 定义会话依赖
CurrentSession = Annotated[AsyncSession, Depends(get_db)]