from pydantic import BaseModel
from typing import Optional


class TableBase(BaseModel):
    capacity: int
    location: str
    is_active: bool = True


class TableCreate(TableBase):
    pass


class TableUpdate(BaseModel):
    capacity: Optional[int] = None
    location: Optional[str] = None
    is_active: Optional[bool] = None


class TableResponse(TableCreate):
    id: int

    class Config:
        from_attributes = True
