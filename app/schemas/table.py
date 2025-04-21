from pydantic import BaseModel, Field
from typing import Optional

from app.models.table import TableStatus


class TableBase(BaseModel):
    capacity: int = Field(
        ...,
        gt=0,
        description=(
            "Number of people the table can accommodate"
        )
    )
    location: str = Field(
        ...,
        min_length=2,
        description="Table location in restaurant"
    )
    status: TableStatus = TableStatus.AVAILABLE
    is_active: bool = True


class TableCreate(TableBase):
    pass


class TableUpdate(BaseModel):
    capacity: Optional[int] = Field(None, gt=0)
    location: Optional[str] = Field(None, min_length=2)
    status: Optional[TableStatus] = None
    is_active: Optional[bool] = None


class TableResponse(TableBase):
    id: int

    class Config:
        from_attributes = True
        use_enum_values = True


class TableAvailabilityQuery(BaseModel):
    capacity: int = Field(..., gt=0)
    location: Optional[str] = None
