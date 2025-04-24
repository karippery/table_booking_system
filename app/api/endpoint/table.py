from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.crud.table import (
    create_table,
    get_table,
    get_tables,
    update_table,
    delete_table,
    get_available_tables,
    set_table_status
)
from app.database import get_db
from app.schemas.table import (
    TableCreate,
    TableResponse,
    TableUpdate,
    TableAvailabilityQuery,
    TableStatus
)
from app.utils.role import is_admin, is_guest

router = APIRouter(tags=["tables"])


@router.post(
    "/",
    response_model=TableResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(is_admin)]
)
async def create_new_table(
    table: TableCreate,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await create_table(db, table)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating table: {str(e)}"
        )


@router.get("/",
            response_model=List[TableResponse],
            dependencies=[Depends(is_admin)])
async def read_tables(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    return await get_tables(db, skip=skip, limit=limit)


@router.get("/available",
            response_model=List[TableResponse],
            dependencies=[Depends(is_guest)])
async def read_available_tables(
    query: TableAvailabilityQuery,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all available tables that match the query criteria.
    Accessible to all authenticated users (both guests and admins).
    """
    try:
        return await get_available_tables(db, query, skip=skip, limit=limit)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid availability request: {str(e)}"
        )


@router.get("/{table_id}",
            response_model=TableResponse,
            dependencies=[Depends(is_admin)])
async def read_table(
    table_id: int,
    db: AsyncSession = Depends(get_db)
):
    db_table = await get_table(db, table_id)
    if not db_table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Table not found"
        )
    return db_table


@router.put("/{table_id}", response_model=TableResponse)
async def update_existing_table(
    table_id: int,
    table: TableUpdate,
    db: AsyncSession = Depends(get_db),
):
    db_table = await update_table(db, table_id, table)
    if not db_table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Table not found"
        )
    return db_table


@router.patch("/{table_id}/status/{status}")
async def change_table_status(
    table_id: int,
    status: TableStatus,
    db: AsyncSession = Depends(get_db),
):
    db_table = await set_table_status(db, table_id, status)
    if not db_table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Table not found"
        )
    return {"message": f"Table status updated to {status}"}


@router.delete(
    "/{table_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_existing_table(
    table_id: int,
    db: AsyncSession = Depends(get_db),
):
    db_table = await delete_table(db, table_id)
    if not db_table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Table not found"
        )
