# schemas/user.py
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional

from app.models.user import UserRole


class UserBase(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, example="Str0ngP@ssword")

    @field_validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError(
                "Password must be at least 8 characters"
                )
        if not any(c.isupper() for c in v):
            raise ValueError(
                "Password must contain at least one uppercase letter"
                )
        if not any(c.islower() for c in v):
            raise ValueError(
                "Password must contain at least one lowercase letter"
                )
        if not any(c.isdigit() for c in v):
            raise ValueError(
                "Password must contain at least one digit"
                )
        return v


class UserCreateAdmin(UserCreate):
    role: UserRole = UserRole.GUEST


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None

    @field_validator('password')
    def validate_password(cls, v):
        if v is not None:
            if len(v) < 8:
                raise ValueError(
                    "Password must be at least 8 characters"
                    )
            if not any(c.isupper() for c in v):
                raise ValueError(
                    "Password must contain at least one uppercase letter"
                    )
            if not any(c.islower() for c in v):
                raise ValueError(
                    "Password must contain at least one lowercase letter"
                    )
            if not any(c.isdigit() for c in v):
                raise ValueError(
                    "Password must contain at least one digit"
                    )
        return v


class UserResponse(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str
