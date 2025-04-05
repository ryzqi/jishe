import logging
import sys
from typing import Any, Dict, Optional

from loguru import logger

from core.config import settings


class InterceptHandler(logging.Handler):
    """
    Logging handler intercepting standard logging messages toward Loguru.
    See: https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging
    """

    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back  # type: ignore
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging() -> None:
    """配置日志"""
    # 移除所有处理器
    logger.remove()

    # 获取日志配置
    log_level = settings.LOG_LEVEL.upper()
    log_format = settings.LOG_FORMAT

    # 配置控制台输出
    logger.configure(handlers=[{"sink": sys.stdout, "format": log_format, "level": log_level}])

    # 如果DEBUG模式，则日志级别设置为DEBUG
    if settings.DEBUG:
        log_level = "DEBUG"

    # 如果是生产环境，添加文件日志
    if settings.APP_ENV == "production":
        logger.add(
            "logs/{time:YYYY-MM-DD}.log",
            rotation="00:00",
            retention="7 days",
            format=log_format,
            level=log_level,
            compression="zip",
        )

    # 拦截来自标准库的日志
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    # 修改uvicorn和其他库的日志配置
    for logger_name in ("uvicorn", "uvicorn.error", "fastapi", "sqlalchemy.engine"):
        logging_logger = logging.getLogger(logger_name)
        logging_logger.handlers = [InterceptHandler()]

    # 记录配置信息
    logger.debug(f"Logging configured. Level: {log_level}, Environment: {settings.APP_ENV}")


# 导出配置好的logger
def get_logger():
    return logger 