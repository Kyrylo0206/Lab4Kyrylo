from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import requests
import re
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Todo MCP Server", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SecurityGuard:
    def __init__(self):
        self.rate_limits = {}
        self.max_requests_per_minute = 30
        self.dangerous_patterns = [
            r'DROP\s+TABLE', r'DELETE\s+FROM', r'INSERT\s+INTO',
            r'UPDATE\s+SET', r'UNION\s+SELECT', r'<script',
            r'javascript:', r'eval\s*\(', r'exec\s*\('
        ]
    
    def check_rate_limit(self, client_id: str = "default") -> bool:
        current_time = time.time()
        if client_id not in self.rate_limits:
            self.rate_limits[client_id] = []
        
        self.rate_limits[client_id] = [
            req_time for req_time in self.rate_limits[client_id]
            if current_time - req_time < 60
        ]
        
        if len(self.rate_limits[client_id]) >= self.max_requests_per_minute:
            return False
        
        self.rate_limits[client_id].append(current_time)
        return True
    
    def check_input_safety(self, input_text: str) -> bool:
        for pattern in self.dangerous_patterns:
            if re.search(pattern, input_text, re.IGNORECASE):
                logger.warning(f"Suspicious pattern: {pattern}")
                return False
        return True

security_guard = SecurityGuard()

class ToolCall(BaseModel):
    name: str
    arguments: Dict[str, Any]

class MCPResponse(BaseModel):
    content: List[Dict[str, str]]
    isError: Optional[bool] = False

@app.get("/")
async def root():
    return {"message": "Todo MCP Server", "version": "1.0.0"}

@app.get("/mcp/capabilities")
async def get_capabilities():
    return {
        "tools": [
            {
                "name": "create_todo_secure",
                "description": "Securely create a new todo with validation",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "Todo title"},
                        "description": {"type": "string", "description": "Todo description"},
                        "priority": {"type": "string", "enum": ["LOW", "MEDIUM", "HIGH"], "description": "Priority level"}
                    },
                    "required": ["title"]
                }
            },
            {
                "name": "get_todos_filtered",
                "description": "Get todos with filtering and security checks",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "priority": {"type": "string", "enum": ["LOW", "MEDIUM", "HIGH"]},
                        "completed": {"type": "boolean"}
                    }
                }
            },
            {
                "name": "update_todo_secure",
                "description": "Securely update a todo",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "todo_id": {"type": "integer", "description": "Todo ID"},
                        "title": {"type": "string"},
                        "description": {"type": "string"},
                        "priority": {"type": "string", "enum": ["LOW", "MEDIUM", "HIGH"]},
                        "completed": {"type": "boolean"}
                    },
                    "required": ["todo_id"]
                }
            },
            {
                "name": "delete_todo_secure",
                "description": "Securely delete a todo",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "todo_id": {"type": "integer", "description": "Todo ID"}
                    },
                    "required": ["todo_id"]
                }
            },
            {
                "name": "search_todos_by_keyword",
                "description": "Search todos by keyword with security validation",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "keyword": {"type": "string", "description": "Search keyword"}
                    },
                    "required": ["keyword"]
                }
            }
        ],
        "resources": [
            {
                "uri": "todos://all",
                "name": "All Todos",
                "description": "Complete list of all todos",
                "mimeType": "application/json"
            },
            {
                "uri": "todos://stats",
                "name": "Todo Statistics", 
                "description": "Statistics about todos",
                "mimeType": "application/json"
            }
        ],
        "prompts": [
            {
                "name": "create_todo_prompt",
                "description": "Help with creating todos"
            },
            {
                "name": "todo_management_help",
                "description": "General todo management guidance"
            }
        ]
    }

@app.post("/mcp/tools/call")
async def call_tool(tool_call: ToolCall) -> MCPResponse:
    if not security_guard.check_rate_limit():
        return MCPResponse(
            content=[{"type": "text", "text": "Rate limit exceeded. Please try again later."}],
            isError=True
        )
    
    for key, value in tool_call.arguments.items():
        if isinstance(value, str) and not security_guard.check_input_safety(value):
            return MCPResponse(
                content=[{"type": "text", "text": f"Security violation detected in parameter: {key}"}],
                isError=True
            )
    
    try:
        if tool_call.name == "create_todo_secure":
            response = requests.post("http://localhost:8000/api/todos", json={
                "title": tool_call.arguments["title"],
                "description": tool_call.arguments.get("description", ""),
                "priority": tool_call.arguments.get("priority", "MEDIUM")
            })
            result = f"✅ Created todo: {response.json()}"
            
        elif tool_call.name == "get_todos_filtered":
            params = {}
            if "priority" in tool_call.arguments:
                params["priority"] = tool_call.arguments["priority"]
            if "completed" in tool_call.arguments:
                params["completed"] = tool_call.arguments["completed"]
            
            response = requests.get("http://localhost:8000/api/todos", params=params)
            todos = response.json()
            result = f"📋 Found {len(todos)} todos: {todos}"
            
        elif tool_call.name == "update_todo_secure":
            todo_id = tool_call.arguments["todo_id"]
            update_data = {k: v for k, v in tool_call.arguments.items() if k != "todo_id"}
            response = requests.put(f"http://localhost:8000/api/todos/{todo_id}", json=update_data)
            result = f"✏️ Updated todo: {response.json()}"
            
        elif tool_call.name == "delete_todo_secure":
            todo_id = tool_call.arguments["todo_id"]
            response = requests.delete(f"http://localhost:8000/api/todos/{todo_id}")
            result = f"🗑️ Deleted todo {todo_id}"
            
        elif tool_call.name == "search_todos_by_keyword":
            keyword = tool_call.arguments["keyword"]
            response = requests.get(f"http://localhost:8000/api/todos/search/{keyword}")
            results = response.json()
            result = f"🔍 Search results for '{keyword}': {results}"
        else:
            result = f"❌ Unknown tool: {tool_call.name}"
            
        return MCPResponse(content=[{"type": "text", "text": result}])
        
    except Exception as e:
        return MCPResponse(
            content=[{"type": "text", "text": f"❌ Error: {str(e)}"}],
            isError=True
        )

@app.get("/mcp/resources")
async def get_resources():
    return {
        "resources": [
            {
                "uri": "todos://all",
                "name": "All Todos",
                "description": "Complete list of all todos"
            },
            {
                "uri": "todos://stats",
                "name": "Todo Statistics",
                "description": "Statistics about todos"
            }
        ]
    }

@app.get("/mcp/resources/read")
async def read_resource(uri: str):
    try:
        if uri == "todos://all":
            response = requests.get("http://localhost:8000/api/todos")
            return {"contents": [{"type": "text", "text": response.text}]}
        elif uri == "todos://stats":
            response = requests.get("http://localhost:8000/api/todos")
            todos = response.json()
            stats = {
                "total": len(todos),
                "completed": len([t for t in todos if t.get("completed", False)]),
                "high_priority": len([t for t in todos if t.get("priority") == "HIGH"])
            }
            return {"contents": [{"type": "text", "text": str(stats)}]}
        else:
            raise HTTPException(status_code=404, detail=f"Unknown resource: {uri}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/mcp/prompts")
async def get_prompts():
    return {
        "prompts": [
            {
                "name": "create_todo_prompt",
                "description": "Help with creating todos"
            },
            {
                "name": "todo_management_help", 
                "description": "General todo management guidance"
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
