from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

from app.models.table import TableStatus


class TableBase(BaseModel):
    capacity: int = Field(
        ...,
        gt=0,
        json_schema_extra={
            "description": "Number of people the table can accommodate",
            "examples": [2, 4, 6]
        }
    )
    location: str = Field(
        ...,
        min_length=2,
        json_schema_extra={
            "description": "Table location in restaurant",
            "examples": ["Patio", "Window", "Bar"]
        }
    )
    status: TableStatus = Field(
        default=TableStatus.AVAILABLE,
        json_schema_extra={
            "description": "Current status of the table",
            "examples": ["available"]
        }
    )
    is_active: bool = Field(
        default=True,
        json_schema_extra={
            "description": "Whether the table is active",
            "examples": [True]
        }
    )


class TableCreate(TableBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "capacity": 4,
                "location": "Window",
                "status": "available",
                "is_active": True
            }
        }
    )


class TableUpdate(BaseModel):
    capacity: Optional[int] = Field(
        default=None,
        gt=0,
        json_schema_extra={
            "description": "Updated capacity if provided",
            "examples": [4]
        }
    )
    location: Optional[str] = Field(
        default=None,
        min_length=2,
        json_schema_extra={
            "description": "Updated location if provided",
            "examples": ["Patio"]
        }
    )
    status: Optional[TableStatus] = Field(
        default=None,
        json_schema_extra={
            "description": "Updated status if provided",
            "examples": ["reserved"]
        }
    )
    is_active: Optional[bool] = Field(
        default=None,
        json_schema_extra={
            "description": "Updated active status if provided",
            "examples": [False]
        }
    )


class TableResponse(TableBase):
    id: int = Field(
        ...,
        json_schema_extra={
            "description": "Unique identifier of the table",
            "examples": [1]
        }
    )

    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "capacity": 4,
                "location": "Window",
                "status": "available",
                "is_active": True
            }
        }
    )