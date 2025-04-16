from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.crud.table import (
    create_table,
    get_table,
    get_tables,
    update_table,
    delete_table
)
from app.database import get_db
from app.schemas.table import TableCreate, TableResponse


router = APIRouter()


@router.post("/", response_model=TableResponse)
async def create_new_table(
    table: TableCreate,
    db: AsyncSession = Depends(get_db),
):
    return await create_table(db, table)


@router.get("/", response_model=List[TableResponse])
async def read_tables(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    return await get_tables(db, skip=skip, limit=limit)


@router.get("/{table_id}", response_model=TableResponse)
async def read_table(
    table_id: int,
    db: AsyncSession = Depends(get_db)
):
    db_table = await get_table(db, table_id)
    if not db_table:
        raise HTTPException(status_code=404, detail="Table not found")
    return db_table


@router.put("/{table_id}", response_model=TableResponse)
async def update_existing_table(
    table_id: int,
    table: TableCreate,
    db: AsyncSession = Depends(get_db),
):
    db_table = await update_table(db, table_id, table)
    if not db_table:
        raise HTTPException(status_code=404, detail="Table not found")
    return db_table


@router.delete("/{table_id}")
async def delete_existing_table(
    table_id: int,
    db: AsyncSession = Depends(get_db),
):
    db_table = await delete_table(db, table_id)
    if not db_table:
        raise HTTPException(status_code=404, detail="Table not found")
    return {"message": "Table deleted successfully"}
