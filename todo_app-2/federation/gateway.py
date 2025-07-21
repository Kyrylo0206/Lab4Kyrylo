from fastapi import FastAPI
import strawberry
from strawberry.fastapi import GraphQLRouter

app = FastAPI(title="Federated GraphQL Gateway")

@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "Federated GraphQL"
    
    @strawberry.field 
    def federation_info(self) -> str:
        return "This gateway demonstrates GraphQL"

schema = strawberry.Schema(query=Query)

graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")

@app.get("/")
def root():
    return {
        "message": " GraphQL Federation Gateway",
        "description": "GraphQL Federation",
        "subgraphs": [
            {
                "name": "user-service", 
                "url": "http://localhost:8002/graphql",
                "description": "User management"
            },
            {
                "name": "todo-service", 
                "url": "http://localhost:8003/graphql",
                "description": "TODO management"
            }
        ],
        "gateway_schema": "/graphql",
        "instructions": {
            "1": "Start user service: python federation/user_server.py",
            "2": "Start todo service: python federation/todo_server.py", 
            "3": "Start gateway: python federation/gateway.py",
            "4": "Test on different ports: 8001 (gateway), 8002 (users), 8003 (todos)"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
