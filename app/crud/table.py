from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.table import Table


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
        for key, value in table_data.dict().items():
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
