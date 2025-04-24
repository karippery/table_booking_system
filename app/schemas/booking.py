from datetime import datetime, date, timedelta
import os
from zoneinfo import ZoneInfo
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from enum import Enum

from app.models.booking import BookingStatus


class SeatPreference(str, Enum):
    WINDOW = "window"
    AISLE = "aisle"
    ACCESSIBLE = "accessible"
    PRIVATE = "private"


class BookingBase(BaseModel):
    table_id: int = Field(..., description="ID of the table to book")
    start_time: datetime = Field(..., description="Start time of the booking")
    end_time: datetime = Field(..., description="End time of the booking")
    guest_count: int = Field(..., gt=0, description="Number of guests")
    special_requests: Optional[str] = Field(
        None,
        max_length=500,
        description="Any special requests for the booking"
    )

    @validator('end_time')
    def validate_end_time(cls, v, values):
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError("End time must be after start time")
        return v


class BookingCreate(BaseModel):
    table_id: int
    start_time: datetime
    guest_count: int = Field(..., gt=0)
    special_requests: Optional[str] = None

    @validator('start_time')
    def ensure_timezone(cls, v):
        """Ensure datetime is timezone-aware"""
        if v.tzinfo is None:
            return v.replace(tzinfo=ZoneInfo("UTC"))
        return v


class BookingUpdate(BaseModel):
    table_id: Optional[int] = Field(
        None,
        description="ID of the table to book"
    )
    start_time: Optional[datetime] = Field(
        None,
        description="New start time"
        )
    end_time: Optional[datetime] = Field(
        None,
        description="New end time"
        )
    guest_count: Optional[int] = Field(
        None,
        gt=0,
        description="New guest count"
        )
    special_requests: Optional[str] = Field(None, max_length=500)
    status: Optional[BookingStatus] = Field(None)


class BookingResponse(BookingBase):
    id: int
    user_id: int
    status: BookingStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class BookingListResponse(BaseModel):
    data: List[BookingResponse]


class AvailabilityQuery(BaseModel):
    start_time: datetime = Field(..., example="2025-04-14T18:00:00")
    guest_count: Optional[int] = Field(None, gt=0, example=4)

    @property
    def end_time(self):
        """Automatically calculate end time using DEFAULT_DURATION"""
        try:
            duration = int(os.getenv("DEFAULT_DURATION", 3))
            return self.start_time + timedelta(hours=duration)
        except ValueError:
            # Fallback if DEFAULT_DURATION is not a number
            return self.start_time + timedelta(hours=3)


class BookingFilter(BaseModel):
    user_id: Optional[int] = None
    status: Optional[BookingStatus] = None
    booking_date: Optional[date] = None
    min_capacity: Optional[int] = None

    class Config:
        extra = "forbid"
        use_enum_values = True
