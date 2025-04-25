from typing import Optional
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException

from app.models.table import Table, TableStatus


async def create_table(db: AsyncSession, table_data):
    db_table = Table(**table_data.dict())
    db.add(db_table)
    await db.commit()
    await db.refresh(db_table)
    return db_table


async def get_table(db: AsyncSession, table_id: int):
    result = await db.execute(select(Table).where(Table.id == table_id))
    return result.scalars().first()


async def get_tables(
    db: AsyncSession,
    status: Optional[TableStatus] = None,
    location: Optional[str] = None,
    capacity: Optional[int] = None,
    skip: int = 0,
    limit: int = 100
):
    conditions = []

    if status:
        conditions.append(Table.status == status)
    if location:
        conditions.append(Table.location == location)
    if capacity:
        conditions.append(Table.capacity >= capacity)

    stmt = (
        select(Table)
        .where(and_(*conditions) if conditions else True)
        .order_by(Table.capacity.asc())
        .offset(skip)
        .limit(limit)
    )

    result = await db.execute(stmt)
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
