from sqlalchemy import (TIMESTAMP, Column, Enum,
                        Integer, String,
                        DateTime, ForeignKey,
                        Index)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
from app.schemas.booking import BookingStatus


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    table_id = Column(Integer, ForeignKey("tables.id"), index=True)
    start_time = Column(TIMESTAMP(timezone=True), nullable=False, index=True)
    end_time = Column(TIMESTAMP(timezone=True), nullable=False, index=True)
    guest_count = Column(Integer)
    special_requests = Column(String, nullable=True)
    status = Column(Enum(BookingStatus),
                    default=BookingStatus.CONFIRMED, index=True)
    created_at = Column(DateTime, server_default=func.now(), index=True)
    updated_at = Column(DateTime,
                        server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="bookings")
    table = relationship("Table", back_populates="bookings")

    __table_args__ = (
        Index('idx_booking_composite', 'user_id', 'status', 'start_time'),
        Index('idx_booking_date_range', 'start_time', 'end_time'),
        Index('idx_booking_status_created', 'status', 'created_at'),
    )
