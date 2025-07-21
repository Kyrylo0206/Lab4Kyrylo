from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field

class EventBase(BaseModel):
    id: UUID = Field(..., description="Unique identifier for the event")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the event was created")

class TodoCreatedEvent(EventBase):
    title: str = Field(..., description="Title of the ToDo item")
    description: str = Field(None, description="Description of the ToDo item")
    due_date: str = Field(None, description="Due date of the ToDo item")
    priority: str = Field(..., description="Priority of the ToDo item")

class TodoUpdatedEvent(EventBase):
    todo_id: UUID = Field(..., description="Unique identifier of the ToDo item being updated")
    title: str = Field(None, description="Updated title of the ToDo item")
    description: str = Field(None, description="Updated description of the ToDo item")
    due_date: str = Field(None, description="Updated due date of the ToDo item")
    priority: str = Field(None, description="Updated priority of the ToDo item")

class TodoDeletedEvent(EventBase):
    todo_id: UUID = Field(..., description="Unique identifier of the ToDo item being deleted")