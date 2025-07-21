from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import strawberry.fastapi
from contextlib import asynccontextmanager

from graphqlapi.schema import schema
from services.todo_service import ToDoService
from services.mock_services import (
    get_user_service, 
    get_tag_service, 
    get_profile_service, 
    get_settings_service
)
from repositories.todo_repository import ToDoRepo
from events.mock_event_producer import MockEventProducer
from graphqlapi.dataloaders import create_dataloaders

event_producer = MockEventProducer() 
todo_repo = ToDoRepo(event_producer)
todo_service = ToDoService(todo_repo, event_producer)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(" Starting GraphQL TODO API...")
    print("GraphiQL interface: http://localhost:8000/graphql")
    yield

app = FastAPI(
    title="TODO GraphQL API",
    description="GraphQL API for TODO management with advanced features - All Levels Implemented",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_graphql_context(
    user_service=Depends(get_user_service),
    tag_service=Depends(get_tag_service),
    profile_service=Depends(get_profile_service),
    settings_service=Depends(get_settings_service)
):
    context = {
        "todo_service": todo_service,
        "user_service": user_service,
        "tag_service": tag_service,
        "profile_service": profile_service,
        "settings_service": settings_service
    }
    dataloaders = create_dataloaders(context)
    context.update(dataloaders)
    
    return context

graphql_app = strawberry.fastapi.GraphQLRouter(
    schema=schema,
    context_getter=get_graphql_context,
    graphiql=True 
)

app.include_router(graphql_app, prefix="/graphql", tags=["graphql"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "todo-graphql-api"}

@app.get("/")
async def root():
    return {
        "message": "TODO GraphQL API",
        "graphql_endpoint": "/graphql",
        "status": "running"
    }

if __name__ == "__main__":
    import uvicorn
    print("Запуск сервера")
    print("URL: http://localhost:8000")
    print("🎮GraphiQL: http://localhost:8000/graphql") 
    print("API Info: http://localhost:8000/")
    uvicorn.run(app, host="0.0.0.0", port=8000)
