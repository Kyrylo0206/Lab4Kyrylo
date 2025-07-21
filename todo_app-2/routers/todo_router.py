from typing import List, Dict, Any, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, Path, status
from fastapi.responses import JSONResponse

from models.todo_models import (
    Create, Update, 
    Pagination, Filter, Error
)
from services.todo_service import ToDoService
from repositories.todo_repository import ToDoRepo
from common.settings import PAGE_SIZE_DEFAULT
from events.event_producer import EventProducer


router = APIRouter(prefix="/api/todos", tags=["ToDo"])

event_producer = EventProducer()
todo_repository = ToDoRepo(event_producer) 
todo_service = ToDoService(repository=todo_repository, event_producer=event_producer)

class ErrorResponse(Error):
    pass

PAGE_SIZE_MIN = 10

@router.get(
    "",
    response_model=Dict[str, Any],
    responses={400: {"model": ErrorResponse}, 422: {"model": ErrorResponse}}
)
def list_todos(
    page: int = Query(1, ge=1),
    size: int = Query(PAGE_SIZE_DEFAULT, ge=1, le=100),
    is_completed: Optional[bool] = Query(None),
    due_before: Optional[str] = Query(None),
    due_after: Optional[str] = Query(None),
    priority: Optional[List[str]] = Query(None),
    sort_by: str = Query("created_at"),
    order: str = Query("asc")
):
    filters = Filter(
        completed=is_completed,
        due_before=due_before,
        due_after=due_after,
        priority=priority
    )
    pagination = Pagination(page=page, size=size)

    result = todo_service.list_todos(
        pagination=pagination,
        filters=filters,
        sort_by=sort_by,
        order=order
    )
    return result

@router.get(
    "/{todo_id}",
    response_model=Dict[str, Any],
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}}
)
def get_todo(
    todo_id: UUID = Path(..., description="UUID of the ToDo")
):
    todo_dict = todo_service.get_todo(todo_id)
    return todo_dict

@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=Dict[str, Any],
    responses={422: {"model": ErrorResponse}, 400: {"model": ErrorResponse}}
)
def create_todo(
    todo_create: Create
):
    created = todo_service.create_todo(todo_create)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=created
    )

@router.put(
    "/{todo_id}",
    response_model=Dict[str, Any],
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}, 422: {"model": ErrorResponse}}
)
def update_todo(
    todo_id: UUID = Path(..., description="UUID of the ToDo to update"),
    todo_update: Update = ...
):
    updated = todo_service.update_todo(todo_id, todo_update)
    event_producer.send_event("todo_updated", updated)  
    return updated

@router.delete(
    "/{todo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}}
)
def delete_todo(
    todo_id: UUID = Path(..., description="UUID of ToDo to delete")
):
    todo_service.delete_todo(todo_id)
    event_producer.send_event("todo_deleted", {"id": str(todo_id)})  
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=None)