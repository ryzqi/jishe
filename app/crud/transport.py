from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.transport import Transport
from schemas.transport import TransportCreate, TransportUpdate


async def get_transport(db: AsyncSession, transport_id: int) -> Optional[Transport]:
    """
    根据 ID 从数据库异步获取单个运输记录。

    Args:
        db: SQLAlchemy AsyncSession 对象。
        transport_id: 要获取的运输记录的 ID。

    Returns:
        找到的 Transport SQLAlchemy 对象，如果未找到则返回 None。
    """
    stmt = select(Transport).where(Transport.id == transport_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_transports(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Transport]:
    """
    从数据库异步获取运输记录列表（支持分页）。

    Args:
        db: SQLAlchemy AsyncSession 对象。
        skip: 跳过的记录数。
        limit: 返回的最大记录数。

    Returns:
        Transport SQLAlchemy 对象的列表。
    """
    stmt = select(Transport).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


async def create_transport(db: AsyncSession, transport: TransportCreate) -> Transport:
    """
    在数据库中异步创建一条新的运输记录。

    Args:
        db: SQLAlchemy AsyncSession 对象。
        transport: 包含新运输记录数据的 Pydantic Schema 对象 (TransportCreate)。

    Returns:
        新创建的 Transport SQLAlchemy 对象 (包含数据库生成的 ID)。
    """
    db_transport = Transport(**transport.model_dump())
    db.add(db_transport)
    await db.commit()
    await db.refresh(db_transport)
    return db_transport


async def update_transport(
        db: AsyncSession,
        db_obj: Transport,
        obj_in: TransportUpdate
) -> Transport:
    """
    异步更新数据库中现有的运输记录。

    Args:
        db: SQLAlchemy AsyncSession 对象。
        db_obj: 从数据库获取的要更新的 Transport SQLAlchemy 对象。
        obj_in: 包含要更新字段的 Pydantic Schema 对象 (TransportUpdate)。

    Returns:
        更新后的 Transport SQLAlchemy 对象。
    """

    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)

    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def delete_transport(db: AsyncSession, transport_id: int) -> Optional[Transport]:
    """
    根据 ID 从数据库异步删除运输记录。

    Args:
        db: SQLAlchemy AsyncSession 对象。
        transport_id: 要删除的运输记录的 ID。

    Returns:
        被删除的 Transport SQLAlchemy 对象，如果未找到则返回 None。
    """

    db_obj = await get_transport(db, transport_id=transport_id)
    if db_obj:
        await db.delete(db_obj)
        await db.commit()
        return db_obj
    return None
