from typing import List, Dict, Any
from datetime import date
from uuid import UUID

from models.todo_models import Create, Update, Pagination, Filter
from common.exceptions import ParameterError
from repositories.todo_repository import ToDoRepo
from events.event_producer import EventProducer

class ToDoService:
    def __init__(self, repository: ToDoRepo, event_producer: EventProducer):
        self.repo = repository
        self.event_producer = event_producer

    def list_todos(
        self,
        pagination: Pagination,
        filters: Filter,
        sort_by: str = "created_at",
        order: str = "asc"
    ) -> Dict[str, Any]:
        todos = self.repo.get_all()

        todos_filtered = []
        for item in todos:
            if filters.completed is not None and item["is_completed"] != filters.completed:
                continue

            if filters.due_before:
                if item["due_date"] is None or item["due_date"] > filters.due_before:
                    continue

            if filters.due_after:
                if item["due_date"] is None or item["due_date"] < filters.due_after:
                    continue

            if filters.priority and item["priority"] not in filters.priority:
                continue

            todos_filtered.append(item)

        if sort_by not in ("created_at", "due_date"):
            raise ParameterError(detail="sort_by must be 'created_at' or 'due_date'")

        reverse_flag = order.lower() == "desc"
        todos_filtered.sort(
            key=lambda x: x.get(sort_by) or date.max,
            reverse=reverse_flag
        )

        page = pagination.page
        size = pagination.size
        total_items = len(todos_filtered)
        total_pages = (total_items + size - 1) // size if total_items > 0 else 1

        if page > total_pages and total_items > 0:
            raise ParameterError(detail=f"page {page} is out of range (total_pages={total_pages})")

        start = (page - 1) * size
        end = start + size
        items_page = todos_filtered[start:end]

        return {
            "page": page,
            "size": size,
            "total_items": total_items,
            "total_pages": total_pages,
            "items": items_page
        }

    def get_todo(self, todo_id: UUID) -> Dict:
        return self.repo.get_by_id(todo_id)

    def create_todo(self, todo_data: Create) -> Dict:
        created_todo = self.repo.create(todo_data)
        self.event_producer.send_event("todo_created", created_todo)
        return created_todo

    def update_todo(self, todo_id: UUID, update_data: Update) -> Dict:
        update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
        if not update_dict:
            raise ParameterError(detail="No fields provided for update")
        updated_todo = self.repo.update(todo_id, update_dict)
        self.event_producer.send_event("todo_updated", updated_todo)
        return updated_todo

    def delete_todo(self, todo_id: UUID) -> None:
        self.repo.delete(todo_id)
        self.event_producer.send_event("todo_deleted", {"id": str(todo_id)})