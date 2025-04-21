from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from enum import Enum as PyEnum


class UserRole(str, PyEnum):
    ADMIN = "admin"
    GUEST = "guest"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(Enum(UserRole), default=UserRole.GUEST, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # Relationships
    bookings = relationship("Booking", back_populates="user")

    @property
    def is_superuser(self) -> bool:
        return self.role == UserRole.ADMIN

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
