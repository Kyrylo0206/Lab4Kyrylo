import strawberry
from strawberry.types import Info
from strawberry.scalars import JSON
from typing import List, Optional, AsyncIterator
from datetime import datetime, date
from uuid import UUID
import asyncio
from dataclasses import dataclass

from models.enums import PriorityEnum, EventTypeEnum
from models.todo_models import Create, Update, Pagination, Filter

@strawberry.type
class Priority:
    LOW: str = "LOW"
    MEDIUM: str = "MEDIUM"
    HIGH: str = "HIGH"

@strawberry.type
class TodoType:
    id: str
    title: str
    description: Optional[str]
    is_completed: bool
    created_at: str
    updated_at: Optional[str]
    due_date: Optional[str]
    priority: str
    
    @strawberry.field
    async def user(self, info: Info) -> Optional['UserType']:
        user_loader = info.context.get('user_loader')
        if user_loader:
            user = await user_loader.load(self.id) 
            if user:
                return UserType(
                    id=user.get('id', 'user-1'),
                    username=user.get('username', 'default_user'),
                    email=user.get('email', 'user@example.com'),
                    full_name=user.get('full_name', 'Default User')
                )
        return UserType(
            id="user-1",
            username="default_user", 
            email="user@example.com",
            full_name="Default User"
        )
    
    @strawberry.field
    async def tags(self, info: Info) -> List['TagType']:
        """Nested entities - Level 3 nesting: Todo -> User -> Tags (using DataLoader)"""
        tag_loader = info.context.get('tag_loader')
        if tag_loader:
            tags = await tag_loader.load(self.id)  
            return [TagType(
                id=tag.get('id', f'tag-{i}'),
                name=tag.get('name', f'Tag {i}'),
                color=tag.get('color', '#blue')
            ) for i, tag in enumerate(tags)]
        return [
            TagType(id="tag-1", name="Work", color="#blue"),
            TagType(id="tag-2", name="Personal", color="#green")
        ]

@strawberry.type
class UserType:
    id: str
    username: str
    email: str
    full_name: str
    
    @strawberry.field
    def todos(self, info: Info, completed: Optional[bool] = None) -> List[TodoType]:
        todo_service = info.context['todo_service']
        pagination = Pagination(page=1, size=100)
        filters = Filter(completed=completed)
        result = todo_service.list_todos(pagination, filters)
        return [TodoType(
            id=str(todo['id']),
            title=todo['title'],
            description=todo.get('description'),
            is_completed=todo['is_completed'],
            created_at=todo['created_at'].isoformat() if hasattr(todo['created_at'], 'isoformat') else str(todo['created_at']),
            updated_at=todo.get('updated_at').isoformat() if todo.get('updated_at') and hasattr(todo.get('updated_at'), 'isoformat') else str(todo.get('updated_at')) if todo.get('updated_at') else None,
            due_date=todo.get('due_date').isoformat() if todo.get('due_date') and hasattr(todo.get('due_date'), 'isoformat') else str(todo.get('due_date')) if todo.get('due_date') else None,
            priority=todo['priority']
        ) for todo in result['items']]
    
    @strawberry.field 
    async def profile(self, info: Info) -> Optional['UserProfileType']:
        profile_loader = info.context.get('profile_loader')
        if profile_loader:
            profile = await profile_loader.load(self.id) 
            if profile:
                return UserProfileType(
                    id=profile.get('id', f'profile-{self.id}'),
                    bio=profile.get('bio', 'Default bio'),
                    avatar_url=profile.get('avatar_url'),
                    created_at=profile.get('created_at', datetime.now().isoformat())
                )
        return UserProfileType(
            id=f"profile-{self.id}",
            bio="Default user bio",
            avatar_url="https://example.com/avatar.jpg",
            created_at=datetime.now().isoformat()
        )

@strawberry.type
class TagType:
    id: str
    name: str
    color: str

@strawberry.type
class UserProfileType:
    id: str
    bio: str
    avatar_url: Optional[str]
    created_at: str
    
    @strawberry.field
    def settings(self, info: Info) -> 'UserSettingsType':
        settings_service = info.context.get('settings_service')
        if settings_service:
            settings = settings_service.get_settings(self.id)
            if settings:
                return UserSettingsType(
                    theme=settings.get('theme', 'light'),
                    notifications_enabled=settings.get('notifications_enabled', True),
                    language=settings.get('language', 'en')
                )
        return UserSettingsType(
            theme="light",
            notifications_enabled=True,
            language="en"
        )

@strawberry.type 
class UserSettingsType:
    theme: str
    notifications_enabled: bool
    language: str

@strawberry.type
class PaginatedTodosType:
    page: int
    size: int
    total_items: int
    total_pages: int
    items: List[TodoType]

@strawberry.type
class EventType:
    id: str
    event_type: str
    payload: JSON
    created_at: str

@strawberry.input
class CreateTodoInput:
    title: str
    description: Optional[str] = None
    due_date: Optional[str] = None
    priority: Optional[str] = "LOW"

@strawberry.input
class UpdateTodoInput:
    title: Optional[str] = None
    description: Optional[str] = None
    is_completed: Optional[bool] = None
    due_date: Optional[str] = None
    priority: Optional[str] = None

@strawberry.input
class PaginationInput:
    page: int = 1
    size: int = 10

@strawberry.input
class FilterInput:
    completed: Optional[bool] = None
    due_before: Optional[str] = None
    due_after: Optional[str] = None
    priority: Optional[List[str]] = None

event_queue = asyncio.Queue()

@strawberry.type
class Query:
    
    @strawberry.field
    def todo(self, info: Info, id: str) -> Optional[TodoType]:
        todo_service = info.context['todo_service']
        try:
            todo = todo_service.get_todo(UUID(id))
            if todo:
                return TodoType(
                    id=str(todo['id']),
                    title=todo['title'],
                    description=todo.get('description'),
                    is_completed=todo['is_completed'],
                    created_at=todo['created_at'].isoformat() if hasattr(todo['created_at'], 'isoformat') else str(todo['created_at']),
                    updated_at=todo.get('updated_at').isoformat() if todo.get('updated_at') and hasattr(todo.get('updated_at'), 'isoformat') else str(todo.get('updated_at')) if todo.get('updated_at') else None,
                    due_date=todo.get('due_date').isoformat() if todo.get('due_date') and hasattr(todo.get('due_date'), 'isoformat') else str(todo.get('due_date')) if todo.get('due_date') else None,
                    priority=todo['priority']
                )
        except Exception as e:
            print(f"Error getting todo {id}: {e}")
        return None
    
    @strawberry.field
    def todos(
        self, 
        info: Info, 
        pagination: Optional[PaginationInput] = None,
        filters: Optional[FilterInput] = None,
        sort_by: str = "created_at",
        order: str = "asc"
    ) -> PaginatedTodosType:
        todo_service = info.context['todo_service']

        page_input = Pagination(
            page=pagination.page if pagination else 1,
            size=pagination.size if pagination else 10
        )
        
        filter_input = Filter()
        if filters:
            filter_input.completed = filters.completed
            if filters.due_before:
                try:
                    filter_input.due_before = datetime.fromisoformat(filters.due_before).date()
                except:
                    pass
            if filters.due_after:
                try:
                    filter_input.due_after = datetime.fromisoformat(filters.due_after).date()
                except:
                    pass
            if filters.priority:
                filter_input.priority = [PriorityEnum(p) for p in filters.priority if p in ['LOW', 'MEDIUM', 'HIGH']]
        
        result = todo_service.list_todos(page_input, filter_input, sort_by, order)
        
        todos = [TodoType(
            id=str(todo['id']),
            title=todo['title'],
            description=todo.get('description'),
            is_completed=todo['is_completed'],
            created_at=todo['created_at'].isoformat() if hasattr(todo['created_at'], 'isoformat') else str(todo['created_at']),
            updated_at=todo.get('updated_at').isoformat() if todo.get('updated_at') and hasattr(todo.get('updated_at'), 'isoformat') else str(todo.get('updated_at')) if todo.get('updated_at') else None,
            due_date=todo.get('due_date').isoformat() if todo.get('due_date') and hasattr(todo.get('due_date'), 'isoformat') else str(todo.get('due_date')) if todo.get('due_date') else None,
            priority=todo['priority']
        ) for todo in result['items']]
        
        return PaginatedTodosType(
            page=result['page'],
            size=result['size'],
            total_items=result['total_items'],
            total_pages=result['total_pages'],
            items=todos
        )
    
    @strawberry.field
    def user(self, info: Info, id: str) -> Optional[UserType]:
        user_service = info.context.get('user_service')
        if user_service:
            user = user_service.get_user(id)
            if user:
                return UserType(
                    id=user['id'],
                    username=user['username'],
                    email=user['email'],
                    full_name=user['full_name']
                )
        return UserType(
            id=id,
            username="default_user",
            email="user@example.com", 
            full_name="Default User"
        )

@strawberry.type
class Mutation:
    
    @strawberry.field
    def create_todo(self, info: Info, input: CreateTodoInput) -> TodoType:
        todo_service = info.context['todo_service']

        create_data = Create(
            title=input.title,
            description=input.description,
            due_date=datetime.fromisoformat(input.due_date).date() if input.due_date else None,
            priority=PriorityEnum(input.priority) if input.priority else PriorityEnum.LOW
        )
        
        todo = todo_service.create_todo(create_data)
        
        event_data = {
            'id': str(todo['id']),
            'event_type': 'TODO_CREATED',
            'payload': todo,
            'created_at': datetime.now().isoformat()
        }
        asyncio.create_task(event_queue.put(event_data))
        
        return TodoType(
            id=str(todo['id']),
            title=todo['title'],
            description=todo.get('description'),
            is_completed=todo['is_completed'],
            created_at=todo['created_at'].isoformat() if hasattr(todo['created_at'], 'isoformat') else str(todo['created_at']),
            updated_at=todo.get('updated_at').isoformat() if todo.get('updated_at') and hasattr(todo.get('updated_at'), 'isoformat') else str(todo.get('updated_at')) if todo.get('updated_at') else None,
            due_date=todo.get('due_date').isoformat() if todo.get('due_date') and hasattr(todo.get('due_date'), 'isoformat') else str(todo.get('due_date')) if todo.get('due_date') else None,
            priority=todo['priority']
        )
    
    @strawberry.field
    def update_todo(self, info: Info, id: str, input: UpdateTodoInput) -> Optional[TodoType]:
        todo_service = info.context['todo_service']
        update_data = Update()
        if input.title is not None:
            update_data.title = input.title
        if input.description is not None:
            update_data.description = input.description
        if input.is_completed is not None:
            update_data.is_completed = input.is_completed
        if input.due_date is not None:
            update_data.due_date = datetime.fromisoformat(input.due_date).date()
        if input.priority is not None:
            update_data.priority = PriorityEnum(input.priority)
        
        try:
            todo = todo_service.update_todo(UUID(id), update_data)
            event_data = {
                'id': str(todo['id']),
                'event_type': 'TODO_UPDATED',
                'payload': todo,
                'created_at': datetime.now().isoformat()
            }
            asyncio.create_task(event_queue.put(event_data))
            
            return TodoType(
                id=str(todo['id']),
                title=todo['title'],
                description=todo.get('description'),
                is_completed=todo['is_completed'],
                created_at=todo['created_at'].isoformat() if hasattr(todo['created_at'], 'isoformat') else str(todo['created_at']),
                updated_at=todo.get('updated_at').isoformat() if todo.get('updated_at') and hasattr(todo.get('updated_at'), 'isoformat') else str(todo.get('updated_at')) if todo.get('updated_at') else None,
                due_date=todo.get('due_date').isoformat() if todo.get('due_date') and hasattr(todo.get('due_date'), 'isoformat') else str(todo.get('due_date')) if todo.get('due_date') else None,
                priority=todo['priority']
            )
        except Exception as e:
            print(f"Error updating todo {id}: {e}")
            return None
    
    @strawberry.field
    def delete_todo(self, info: Info, id: str) -> bool:
        todo_service = info.context['todo_service']
        try:
            todo_service.delete_todo(UUID(id))
            event_data = {
                'id': id,
                'event_type': 'TODO_DELETED', 
                'payload': {'id': id},
                'created_at': datetime.now().isoformat()
            }
            asyncio.create_task(event_queue.put(event_data))
            
            return True
        except Exception as e:
            print(f"Error deleting todo {id}: {e}")
            return False

@strawberry.type
class Subscription:
    
    @strawberry.subscription
    async def todo_events(self, info: Info, event_types: Optional[List[str]] = None) -> AsyncIterator[EventType]:
        while True:
            try:
                event_data = await event_queue.get()
                if event_types and event_data['event_type'] not in event_types:
                    continue
                    
                yield EventType(
                    id=event_data['id'],
                    event_type=event_data['event_type'],
                    payload=event_data['payload'],
                    created_at=event_data['created_at']
                )
            except Exception as e:
                print(f"Subscription error: {e}")
                break

schema = strawberry.Schema(
    query=Query, 
    mutation=Mutation, 
    subscription=Subscription
)
