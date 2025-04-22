
import os
from typing import List, Optional
from zoneinfo import ZoneInfo
from app.models.booking import Booking
from app.models.table import Table
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from sqlalchemy import between, func, select, and_, exists, text
from fastapi import HTTPException


from app.schemas.booking import BookingFilter


async def _apply_booking_filters(
    query,
    filters: BookingFilter
):
    """Apply filters to booking query"""
    if filters.user_id is not None:
        query = query.where(Booking.user_id == filters.user_id)
    if filters.status is not None:
        query = query.where(Booking.status == filters.status)
    if filters.booking_date is not None:
        query = query.where(
            between(
                Booking.start_time,
                datetime.combine(filters.booking_date, datetime.min.time()),
                datetime.combine(filters.booking_date, datetime.max.time())
            )
        )
    return query


# Retrieves a list of available tables for a specified time range and
# optional guest count, ensuring no conflicting bookings exist.
async def get_available_tables(
    db: AsyncSession,
    start_time: datetime,
    end_time: datetime,
    guest_count: Optional[int] = None,
) -> List[Table]:
    try:
        query = select(Table).where(
            Table.is_active
        ).where(
            ~exists().where(
                and_(
                    Booking.table_id == Table.id,
                    Booking.status == "confirmed",
                    Booking.start_time < end_time,
                    Booking.end_time > start_time
                )
            )
        )
        if guest_count:
            query = query.where(Table.capacity >= guest_count)
        result = await db.execute(query)
        tables = result.scalars().all()
        return tables if tables else []
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error checking availability: {str(e)}"
        )


# Create a booking
# This function assumes that the table_id is valid and the user_id exists
async def create_booking(
    db: AsyncSession,
    user_id: int,
    table_id: int,
    start_time: datetime,
    guest_count: int,
    special_requests: str = None
):
    # Ensure timezone awareness
    if start_time.tzinfo is None:
        start_time = start_time.replace(tzinfo=ZoneInfo("UTC"))

    end_time = start_time + timedelta(hours=int(os.getenv("DEFAULT_DURATION")))

    # Ensure end_time is timezone-aware
    if end_time.tzinfo is None:
        end_time = end_time.replace(tzinfo=ZoneInfo("UTC"))
    await db.execute(
        text("SELECT pg_advisory_xact_lock(:lock_id)"),
        {"lock_id": table_id}
    )

    available_tables = await get_available_tables(db, start_time, end_time)
    if not any(table.id == table_id for table in available_tables):
        raise ValueError("Table is no longer available for the selected time")

    booking = Booking(
        user_id=user_id,
        table_id=table_id,
        start_time=start_time,
        end_time=end_time,
        guest_count=guest_count,
        special_requests=special_requests,
        status="confirmed"
    )
    db.add(booking)
    await db.commit()
    await db.refresh(booking)
    return booking


async def extend_booking(
    db: AsyncSession,
    booking_id: int,
    additional_hours: int = 1
):
    booking = await db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Check for conflicts with the new extended time
    new_end_time = booking.end_time + timedelta(hours=additional_hours)
    conflicting_tables = await get_available_tables(
        db, booking.end_time, new_end_time
    )
    if not any(t.id == booking.table_id for t in conflicting_tables):
        raise HTTPException(
            status_code=400,
            detail="Cannot extend, time conflict"
        )
    booking.end_time = new_end_time
    await db.commit()
    await db.refresh(booking)
    return booking


async def cancel_and_free_booking(
    db: AsyncSession,
    booking_id: int
):
    booking = await db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking.status != "confirmed":
        raise HTTPException(
            status_code=400,
            detail="Booking is already cancelled or inactive"
        )
    # Mark booking as cancelled
    booking.status = "cancelled"
    await db.commit()
    await db.refresh(booking)

    return {
        "message": (
            f"Booking {booking_id} cancelled and table is now free."
        )
    }


async def get_bookings(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    filters: Optional[BookingFilter] = None
) -> List[Booking]:
    try:
        query = select(Booking)
        if filters:
            query = await _apply_booking_filters(query, filters)
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )
    

async def get_booking_count(
    db: AsyncSession,
    filters: Optional[BookingFilter] = None
) -> int:
    try:
        query = select(func.count(Booking.id))
        if filters:
            query = await _apply_booking_filters(query, filters)
        result = await db.execute(query)
        return result.scalar()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )
