import strawberry
from typing import Optional, List
from datetime import datetime
from fastapi import FastAPI
import strawberry.fastapi
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@strawberry.type
class User:
    id: strawberry.ID

@strawberry.type
class Todo:
    id: strawberry.ID
    title: str
    description: Optional[str]
    is_completed: bool
    created_at: str
    updated_at: Optional[str]
    due_date: Optional[str]
    priority: str
    user_id: str
    
    @strawberry.field
    def user(self) -> User:
        return User(id=self.user_id)

@strawberry.input
class CreateTodoInput:
    title: str
    description: Optional[str] = None
    due_date: Optional[str] = None
    priority: str = "LOW"
    user_id: str

@strawberry.type
class Query:
    @strawberry.field
    def todo(self, id: strawberry.ID) -> Optional[Todo]:
        if str(id) == "todo-1":
            return Todo(
                id="todo-1",
                title="Learn GraphQL Federation",
                description="Implement federation for microservices",
                is_completed=False,
                created_at=datetime.now().isoformat(),
                updated_at=None,
                due_date=None,
                priority="HIGH",
                user_id="user-1"
            )
        elif str(id) == "todo-2":
            return Todo(
                id="todo-2",
                title="Update documentation",
                description="Write comprehensive docs",
                is_completed=True,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                due_date=None,
                priority="MEDIUM",
                user_id="user-2"
            )
        return None
    
    @strawberry.field
    def todos(self) -> List[Todo]:
        return [
            Todo(
                id="todo-1",
                title="Learn GraphQL Federation",
                description="Implement federation for microservices", 
                is_completed=False,
                created_at=datetime.now().isoformat(),
                updated_at=None,
                due_date=None,
                priority="HIGH",
                user_id="user-1"
            ),
            Todo(
                id="todo-2",
                title="Update documentation",
                description="Write comprehensive docs",
                is_completed=True,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                due_date=None,
                priority="MEDIUM",
                user_id="user-2"
            )
        ]

@strawberry.type
class Mutation:
    @strawberry.field
    def create_todo(self, input: CreateTodoInput) -> Todo:
        return Todo(
            id=f"todo-{datetime.now().microsecond}",
            title=input.title,
            description=input.description,
            is_completed=False,
            created_at=datetime.now().isoformat(),
            updated_at=None,
            due_date=input.due_date,
            priority=input.priority,
            user_id=input.user_id
        )

schema = strawberry.Schema(
    query=Query,
    mutation=Mutation
)

app = FastAPI(title="Todo Service - GraphQL Federation")

graphql_app = strawberry.fastapi.GraphQLRouter(schema, graphiql=True)
app.include_router(graphql_app, prefix="/graphql")

@app.get("/")
def root():
    return {"service": "todo-service", "graphql": "/graphql"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
