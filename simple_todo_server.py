from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

app = FastAPI(title="Todo API for Lab 4")

class TodoCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str = "MEDIUM"

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    completed: Optional[bool] = None

class Todo(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    priority: str = "MEDIUM"
    completed: bool = False

todos_db = []
next_id = 1

@app.post("/api/todos", response_model=Todo)
def create_todo(todo: TodoCreate):
    global next_id
    new_todo = Todo(
        id=next_id,
        title=todo.title,
        description=todo.description,
        priority=todo.priority,
        completed=False
    )
    todos_db.append(new_todo)
    next_id += 1
    return new_todo

@app.get("/api/todos", response_model=List[Todo])
def get_todos():
    return todos_db

@app.get("/api/todos/{todo_id}", response_model=Todo)
def get_todo(todo_id: int):
    todo = next((t for t in todos_db if t.id == todo_id), None)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

@app.put("/api/todos/{todo_id}", response_model=Todo)
def update_todo(todo_id: int, todo_update: TodoUpdate):
    todo = next((t for t in todos_db if t.id == todo_id), None)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    if todo_update.title is not None:
        todo.title = todo_update.title
    if todo_update.description is not None:
        todo.description = todo_update.description
    if todo_update.priority is not None:
        todo.priority = todo_update.priority
    if todo_update.completed is not None:
        todo.completed = todo_update.completed
    
    return todo

@app.delete("/api/todos/{todo_id}")
def delete_todo(todo_id: int):
    global todos_db
    todo = next((t for t in todos_db if t.id == todo_id), None)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    todos_db = [t for t in todos_db if t.id != todo_id]
    return {"message": "Todo deleted successfully"}

@app.get("/api/todos/search/{query}", response_model=List[Todo])
def search_todos(query: str):
    results = [
        todo for todo in todos_db 
        if query.lower() in todo.title.lower() or 
           (todo.description and query.lower() in todo.description.lower())
    ]
    return results

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
