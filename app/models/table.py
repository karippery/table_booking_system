from sqlalchemy import Column, Integer, String, Boolean, Index
from sqlalchemy.orm import relationship

from app.database import Base


class Table(Base):
    __tablename__ = "tables"
    id = Column(Integer, primary_key=True, index=True)
    capacity = Column(Integer, nullable=False)  # 2, 4, 6, etc.
    location = Column(String)  # "window", "patio", etc.
    is_active = Column(Boolean, default=False)
    bookings = relationship("Booking", back_populates="table")
    __table_args__ = (
        Index('idx_table_capacity', 'capacity'),
    )
