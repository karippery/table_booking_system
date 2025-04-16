# app/schemas/booking.py
from datetime import datetime, date
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class Meta(BaseModel):
    total: int
    skip: int
    limit: int


class BookingStatus(str, Enum):
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class BookingBase(BaseModel):
    table_id: int
    start_time: datetime
    end_time: datetime
    guest_count: int = Field(..., gt=0)
    special_requests: Optional[str] = None


class BookingCreate(BookingBase):
    pass


class BookingResponse(BaseModel):
    id: int
    user_id: int
    table_id: int
    start_time: datetime
    end_time: datetime
    guest_count: int
    special_requests: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class BookingListResponse(BaseModel):
    data: List[BookingResponse]
    meta: Meta
    

class AvailabilityQuery(BaseModel):
    start_time: datetime = Field(..., example="2025-04-14T18:00:00")
    end_time: datetime = Field(..., example="2025-04-14T20:00:00")
    guest_count: Optional[int] = Field(None, gt=0, example=4)


class BookingUpdate(BaseModel):
    table_id: Optional[int] = Field(None, example=5)
    start_time: Optional[datetime] = Field(None, example="2025-04-14T18:00:00")
    end_time: Optional[datetime] = Field(None, example="2025-04-14T20:00:00")
    guest_count: Optional[int] = Field(None, gt=0, example=4)
    special_requests: Optional[str] = Field(
        None, example="Window seat, birthday decoration"
    )
    status: Optional[BookingStatus] = Field(None, example="confirmed")


class BookingFilter(BaseModel):
    user_id: Optional[int] = None
    status: Optional[str] = None
    booking_date: Optional[date] = None
    min_capacity: Optional[int] = None

    class Config:
        extra = "forbid"
