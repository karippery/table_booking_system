# api/endpoints/booking.py
from datetime import date, timedelta
from sqlalchemy import select, and_
from app.crud.booking import (
    create_booking,
    get_available_tables,
    get_booking_count,
    get_bookings,
)
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from app.models.booking import Booking
from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.booking import (
    AvailabilityQuery,
    BookingCreate,
    BookingFilter,
    BookingListResponse,
    BookingResponse,
)
from app.database import get_db
from app.schemas.table import TableResponse
from app.utils.token import get_current_user


router = APIRouter()


# It includes endpoints for checking table availability and creating bookings
@router.get("/", response_model=BookingListResponse)
async def read_bookings(
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    status: Optional[str] = None,
    booking_date: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    filters = BookingFilter(
        user_id=user_id,  # No restriction on whose bookings can be queried
        status=status,
        booking_date=booking_date
    )
    bookings = await get_bookings(db, skip=skip, limit=limit, filters=filters)
    total = await get_booking_count(db, filters=filters)

    return {
        "data": [BookingResponse.from_orm(booking) for booking in bookings],
        "meta": {"total": total, "skip": skip, "limit": limit}
    }


@router.get("/availability", response_model=List[TableResponse])
async def check_availability(
    query: AvailabilityQuery = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Check available tables for a given time range"""
    return await get_available_tables(
        db,
        query.start_time,
        query.end_time,
        query.guest_count
    )


# for a given time range and guest count
@router.post("/book", response_model=BookingResponse)
async def book_table(
    booking_data: BookingCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new booking"""
    try:
        booking = await create_booking(
            db,
            current_user.id,
            booking_data.table_id,
            booking_data.start_time,
            booking_data.end_time,
            booking_data.guest_count,
            booking_data.special_requests
        )
        return booking
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/bookings/{booking_id}/cancel", response_model=dict)
async def cancel_and_free_booking_endpoint(
    booking_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cancel a booking and free up the table"""
    booking = await db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    if booking.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=403, 
            detail="Not authorized to cancel this booking"
        )

    if booking.status != "confirmed":
        raise HTTPException(
            status_code=400, 
            detail="Booking is already cancelled or inactive"
        )

    booking.status = "cancelled"
    await db.commit()
    await db.refresh(booking)
    return {
        "message": (
            f"Booking {booking_id} cancelled and table is now free."
        )
    }


@router.post("/bookings/{booking_id}/extend", response_model=dict)
async def extend_booking(
    booking_id: int,
    extension_minutes: int = 60,  # Default 1 hour
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Extend an existing booking duration by X minutes"""
    booking = await db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to extend this booking"
        )

    if booking.status != "confirmed":
        raise HTTPException(
            status_code=400,
            detail="Only confirmed bookings can be extended"
        )

    new_end_time = booking.end_time + timedelta(minutes=extension_minutes)

    # Check if table is available for extended time
    conflicting_booking = await db.execute(
        select(Booking).where(
            and_(
                Booking.table_id == booking.table_id,
                Booking.status == "confirmed",
                Booking.start_time < new_end_time,
                Booking.end_time > booking.end_time,
                Booking.id != booking.id
            )
        )
    )
    if conflicting_booking.scalars().first():
        raise HTTPException(
            status_code=400, 
            detail="Table not available for extension"
        )

    booking.end_time = new_end_time
    await db.commit()
    await db.refresh(booking)

    return {"message": f"Booking {booking_id} extended to {new_end_time}."}
