from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
from app.schemas.booking import BookingStatus


class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    table_id = Column(Integer, ForeignKey("tables.id"), index=True)
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=False, index=True)
    guest_count = Column(Integer)
    special_requests = Column(String, nullable=True)
    status = Column(String, default=BookingStatus.CONFIRMED, index=True)
    created_at = Column(DateTime, server_default=func.now(), index=True)
    user = relationship("User", back_populates="bookings")
    table = relationship("Table", back_populates="bookings")
    __table_args__ = (
        Index('idx_booking_composite', 'user_id', 'status', 'start_time'),
        Index('idx_booking_date_range', 'start_time', 'end_time'),
    )
