# api/endpoints/booking.py
from datetime import date, timedelta
import os
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
from app.utils.role import is_admin
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
    current_user: User = Depends(is_admin)
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
    """
    Check table availability for a given time and guest count.
    """
    try:
        available_tables = await get_available_tables(
            db,
            start_time=query.start_time,
            end_time=query.end_time,
            guest_count=query.guest_count
        )
        return available_tables
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid availability request: {str(e)}"
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "An unexpected error occurred while checking availability. "
                "Please try again later."
            )
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
            booking_data.guest_count,
            booking_data.special_requests
        )
        return booking
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Booking failed: {str(e)}"
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating the booking."
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
            detail="You do not have permission to cancel this booking."
        )

    if booking.status != "confirmed":
        raise HTTPException(
            status_code=400,
            detail="This booking is already cancelled or inactive."
        )

    booking.status = "cancelled"
    await db.commit()
    await db.refresh(booking)
    return {
        "message": (
            f"Booking {booking_id} has been cancelled and the table is now "
            "available."
        )
    }


@router.post("/bookings/{booking_id}/extend", response_model=dict)
async def extend_booking(
    booking_id: int,
    extension_minutes: int = os.getenv("EXTENSION_MINUTES", 30),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Extend a confirmed booking by a specific number of minutes"""
    booking = await db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to extend this booking."
        )

    if booking.status != "confirmed":
        raise HTTPException(
            status_code=400,
            detail="Only confirmed bookings can be extended."
        )

    new_end_time = booking.end_time + timedelta(minutes=extension_minutes)

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
    conflicting_booking_result = conflicting_booking.scalars().first()
    if conflicting_booking_result:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unable to extend booking: the table is already booked for "
                "the extended time."
            )
        )

    booking.end_time = new_end_time
    await db.commit()
    await db.refresh(booking)

    return {
        "message": f"Booking {booking_id} has been extended to {new_end_time}."
    }
