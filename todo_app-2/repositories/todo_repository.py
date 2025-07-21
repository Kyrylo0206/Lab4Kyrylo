from typing import List, Dict, Any
from uuid import UUID, uuid4 
from datetime import datetime

from models.todo_models import Create
from common.exceptions import FoundError
from events.event_producer import EventProducer


class ToDoRepo:
    def __init__(self, event_producer: EventProducer):
        self._storage: Dict[UUID, Dict[str, Any]] = {}
        self.event_producer = event_producer

    def get_all(self) -> List[Dict[str, Any]]:
        return list(self._storage.values())

    def get_by_id(self, todo_id: UUID) -> Dict[str, Any]:
        if todo_id not in self._storage:
            raise FoundError(detail=f"ToDo with id {todo_id} not found, pls check your id")
        return self._storage[todo_id]

    def create(self, todo_data: Create) -> Dict[str, Any]:
        new_id = uuid4() 
        now = datetime.utcnow()

        todo_dict = {
            "id": str(new_id),
            "title": todo_data.title,
            "description": todo_data.description,
            "is_completed": False,
            "created_at": now.isoformat() + "Z",
            "due_date": todo_data.due_date.isoformat() if todo_data.due_date else None,
            "priority": todo_data.priority.value if todo_data.priority else None
        }
        self._storage[new_id] = todo_dict
        
        self.event_producer.send_event("todo_created", todo_dict)
        
        return todo_dict

    def update(self, todo_id: UUID, update_data: Dict[str, Any]) -> Dict[str, Any]:
        if todo_id not in self._storage:
            raise FoundError(detail=f"ToDo with id {todo_id} not found")
        existing = self._storage[todo_id]

        for field, value in update_data.items():
            if field == "due_date" and value is not None:
                existing["due_date"] = value.isoformat()
            elif field == "priority" and value is not None:
                existing["priority"] = value.value
            else:
                existing[field] = value

        self._storage[todo_id] = existing
        

        self.event_producer.send_event("todo_updated", existing)

        return existing

    def delete(self, todo_id: UUID) -> None:
        if todo_id not in self._storage:
            raise FoundError(detail=f"ToDo with id {todo_id} not found")
        del self._storage[todo_id]
        

        self.event_producer.send_event("todo_deleted", {"id": str(todo_id)})