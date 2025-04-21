from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_
from fastapi import HTTPException

from app.models.table import Table, TableStatus
from app.schemas.table import TableAvailabilityQuery


async def create_table(db: AsyncSession, table_data):
    db_table = Table(**table_data.dict())
    db.add(db_table)
    await db.commit()
    await db.refresh(db_table)
    return db_table


async def get_table(db: AsyncSession, table_id: int):
    result = await db.execute(select(Table).where(Table.id == table_id))
    return result.scalars().first()


async def get_tables(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(Table).offset(skip).limit(limit))
    return result.scalars().all()


async def update_table(db: AsyncSession, table_id: int, table_data):
    db_table = await get_table(db, table_id)
    if db_table:
        update_data = table_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_table, key, value)
        await db.commit()
        await db.refresh(db_table)
    return db_table


async def delete_table(db: AsyncSession, table_id: int):
    db_table = await get_table(db, table_id)
    if db_table:
        await db.delete(db_table)
        await db.commit()
    return db_table


async def get_available_tables(
    db: AsyncSession,
    query: TableAvailabilityQuery,
    skip: int = 0,
    limit: int = 100
):
    conditions = [
        Table.status == TableStatus.AVAILABLE,
        Table.is_active,
        Table.capacity >= query.capacity
    ]

    if query.location:
        conditions.append(Table.location == query.location)

    stmt = (
        select(Table)
        .where(and_(*conditions))
        .order_by(Table.capacity.asc())
        .offset(skip)
        .limit(limit)
    )

    result = await db.execute(stmt)
    return result.scalars().all()


async def set_table_status(
        db: AsyncSession,
        table_id: int,
        status: TableStatus
        ):
    db_table = await get_table(db, table_id)
    if not db_table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Table not found"
        )

    db_table.status = status
    await db.commit()
    await db.refresh(db_table)
    return db_table
