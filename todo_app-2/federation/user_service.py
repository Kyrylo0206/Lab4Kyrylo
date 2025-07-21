import strawberry
from typing import Optional, List
from fastapi import FastAPI
import strawberry.fastapi
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@strawberry.type
class User:
    id: strawberry.ID
    username: str
    email: str
    full_name: str

@strawberry.type
class Query:
    @strawberry.field
    def user(self, id: strawberry.ID) -> Optional[User]:
        users = {
            "user-1": User(
                id="user-1",
                username="john_doe",
                email="john@example.com", 
                full_name="John Doe"
            ),
            "user-2": User(
                id="user-2",
                username="jane_smith",
                email="jane@example.com",
                full_name="Jane Smith"
            )
        }
        return users.get(str(id))
    
    @strawberry.field
    def users(self) -> List[User]:
        return [
            User(
                id="user-1",
                username="john_doe",
                email="john@example.com",
                full_name="John Doe"
            ),
            User(
                id="user-2", 
                username="jane_smith",
                email="jane@example.com",
                full_name="Jane Smith"
            )
        ]

schema = strawberry.Schema(query=Query)

app = FastAPI(title="User Service - GraphQL Federation")

graphql_app = strawberry.fastapi.GraphQLRouter(schema, graphiql=True)
app.include_router(graphql_app, prefix="/graphql")

@app.get("/")
def root():
    return {"service": "user-service", "graphql": "/graphql"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
