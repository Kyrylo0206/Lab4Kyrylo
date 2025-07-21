from datetime import datetime, date
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, validator
from models.enums import PriorityEnum

class Create(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    due_date: Optional[date] = None
    priority: Optional[PriorityEnum] = PriorityEnum.LOW

    @validator("due_date")
    def due_date_not_in_past(cls, value):
        if value is not None and value < date.today():
            raise ValueError("due_date cannot be in the past")
        return value

class Update(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_completed: Optional[bool] = None
    due_date: Optional[date] = None
    priority: Optional[PriorityEnum] = None

    @validator("due_date")
    def due_date_not_in_past(cls, value):
        if value is not None and value < date.today():
            raise ValueError("due_date cannot be in the past")
        return value

class Request(BaseModel):
    id: UUID 
    description: Optional[str]
    completed: bool
    created_at: datetime
    due_date: Optional[date]
    priority: PriorityEnum

class Pagination(BaseModel):
    page: int = Field(1, ge=1)
    size: int = Field(10, ge=1, le=100)

class Filter(BaseModel):
    completed: Optional[bool] = None
    due_before: Optional[date] = None
    due_after: Optional[date] = None
    priority: Optional[List[PriorityEnum]] = None

class Error(BaseModel):
    code: int
    msg: str