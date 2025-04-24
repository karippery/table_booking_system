from sqlalchemy import Column, Integer, String, Boolean, Index, Enum
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum

from app.database import Base


class TableStatus(str, PyEnum):
    AVAILABLE = "available"
    RESERVED = "reserved"
    MAINTENANCE = "maintenance"
    SPECIAL_EVENT = "special_event"


class Table(Base):
    __tablename__ = "tables"
    id = Column(Integer, primary_key=True, index=True)
    capacity = Column(Integer, nullable=False)  # 2, 4, 6, etc.
    location = Column(String)  # "window", "patio", etc.
    status = Column(Enum(TableStatus), default=TableStatus.AVAILABLE)
    is_active = Column(Boolean, default=True)
    bookings = relationship("Booking", back_populates="table")

    __table_args__ = (
        Index('idx_table_capacity_status', 'capacity', 'status'),
        Index('idx_table_location_status', 'location', 'status'),
    )
