from typing import Any, Dict, List
from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, func
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs


class Base(AsyncAttrs, DeclarativeBase):
    """
    SQLAlchemy 2.0 基础模型类
    所有模型类都应该继承此类
    """
    
    # 自动生成表名（转换为蛇形命名）
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
    
    
    def to_dict(self) -> Dict[str, Any]:
        """
        将模型对象转换为字典
        """
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            # 处理日期时间类型
            if isinstance(value, datetime):
                value = value.isoformat()
            result[column.name] = value
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Base":
        """
        从字典创建模型对象
        """
        return cls(**{
            k: v for k, v in data.items() 
            if k in [c.name for c in cls.__table__.columns]
        }) 