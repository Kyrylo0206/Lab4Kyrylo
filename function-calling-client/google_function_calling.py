import json
import requests
import google.generativeai as genai
import logging
import time
import re
from typing import Dict, Any, Optional, List
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TokenLimitExceededError(Exception):
    pass

class PotentialInjectionError(Exception):
    pass

class TodoAPIClient:
    def __init__(self, base_url: str = "http://localhost:8000/api"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def create_todo(self, title: str, description: str = "", priority: str = "LOW", due_date: str = None) -> Dict[str, Any]:
        try:
            payload = {"title": title, "description": description, "priority": priority}
            if due_date: payload["due_date"] = due_date
            response = self.session.post(f"{self.base_url}/todos", json=payload)
            return {"status": response.status_code, "data": response.json() if response.status_code < 400 else response.text}
        except Exception as e:
            return {"error": str(e)}

    def get_todos(self, page: int = 1, size: int = 10, priority: str = None, completed: bool = None) -> Dict[str, Any]:
        try:
            params = {}
            if priority: params["priority"] = priority
            if completed is not None: params["is_completed"] = completed
            response = self.session.get(f"{self.base_url}/todos", params=params)
            return {"status": response.status_code, "data": response.json() if response.status_code < 400 else response.text}
        except Exception as e:
            return {"error": str(e)}

    def get_todo(self, todo_id: str) -> Dict[str, Any]:
        try:
            response = self.session.get(f"{self.base_url}/todos/{todo_id}")
            return {"status": response.status_code, "data": response.json() if response.status_code < 400 else response.text}
        except Exception as e:
            return {"error": str(e)}

    def update_todo(self, todo_id: str, title: str = None, description: str = None, 
                   is_completed: bool = None, priority: str = None, due_date: str = None) -> Dict[str, Any]:
        try:
            payload = {}
            if title is not None: payload["title"] = title
            if description is not None: payload["description"] = description
            if is_completed is not None: payload["is_completed"] = is_completed
            if priority is not None: payload["priority"] = priority
            if due_date is not None: payload["due_date"] = due_date
            response = self.session.put(f"{self.base_url}/todos/{todo_id}", json=payload)
            return {"status": response.status_code, "data": response.json() if response.status_code < 400 else response.text}
        except Exception as e:
            return {"error": str(e)}

    def delete_todo(self, todo_id: str) -> Dict[str, Any]:
        try:
            response = self.session.delete(f"{self.base_url}/todos/{todo_id}")
            return {"status": response.status_code, "data": "Deleted" if response.status_code == 204 else response.text}
        except Exception as e:
            return {"error": str(e)}

    def search_todos(self, search_term: str) -> Dict[str, Any]:
        try:
            todos_response = self.get_todos()
            if "error" in todos_response or todos_response["status"] != 200:
                return todos_response
            
            todos_data = todos_response.get("data", [])
            if isinstance(todos_data, dict):
                todos_list = todos_data.get("items", [])
            else:
                todos_list = todos_data
                
            matching_todos = [todo for todo in todos_list
                            if search_term.lower() in todo.get("title", "").lower()]
            return {"status": 200, "data": matching_todos}
        except Exception as e:
            return {"error": str(e)}

class GuardrailManager:
    def __init__(self, max_requests: int = 50, max_cost: float = 0.0):
        self.max_requests = max_requests
        self.max_cost = max_cost
        self.current_requests = 0
        self.current_cost = 0.0
        self.session_start = time.time()
        
        self.injection_patterns = [
            r'ignore\s+previous\s+instructions', r'forget\s+everything\s+above',
            r'system\s*:\s*you\s+are\s+now', r'<\s*script\s*>', r'javascript\s*:',
            r'eval\s*\(', r'exec\s*\(', r'__import__\s*\('
        ]
        
    def check_request_limit(self):
        if self.current_requests >= self.max_requests:
            raise TokenLimitExceededError(f"Request limit exceeded: {self.current_requests}/{self.max_requests}")
    
    def update_usage(self):
        self.current_requests += 1
        
    def check_injection(self, text: str):
        for pattern in self.injection_patterns:
            if re.search(pattern, text.lower(), re.IGNORECASE):
                raise PotentialInjectionError(f"Potential injection detected: {pattern}")
    
    def get_usage_stats(self) -> Dict[str, Any]:
        return {
            "requests_used": self.current_requests,
            "requests_remaining": self.max_requests - self.current_requests,
            "session_duration_minutes": (time.time() - self.session_start) / 60
        }

class GoogleFunctionCaller:
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
        self.todo_client = TodoAPIClient()
        self.guardrail = GuardrailManager()
        
        self.functions = [
            genai.protos.FunctionDeclaration(
                name="create_todo",
                description="Create a new todo item",
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        "title": genai.protos.Schema(type=genai.protos.Type.STRING),
                        "description": genai.protos.Schema(type=genai.protos.Type.STRING),
                        "priority": genai.protos.Schema(type=genai.protos.Type.STRING),
                        "due_date": genai.protos.Schema(type=genai.protos.Type.STRING)
                    },
                    required=["title"]
                )
            ),
            genai.protos.FunctionDeclaration(
                name="get_todos",
                description="Get list of todos with filtering",
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        "page": genai.protos.Schema(type=genai.protos.Type.INTEGER),
                        "size": genai.protos.Schema(type=genai.protos.Type.INTEGER),
                        "priority": genai.protos.Schema(type=genai.protos.Type.STRING),
                        "completed": genai.protos.Schema(type=genai.protos.Type.BOOLEAN)
                    }
                )
            ),
            genai.protos.FunctionDeclaration(
                name="update_todo",
                description="Update existing todo",
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        "todo_id": genai.protos.Schema(type=genai.protos.Type.STRING),
                        "title": genai.protos.Schema(type=genai.protos.Type.STRING),
                        "description": genai.protos.Schema(type=genai.protos.Type.STRING),
                        "is_completed": genai.protos.Schema(type=genai.protos.Type.BOOLEAN),
                        "priority": genai.protos.Schema(type=genai.protos.Type.STRING)
                    },
                    required=["todo_id"]
                )
            ),
            genai.protos.FunctionDeclaration(
                name="search_todos",
                description="Search todos by title",
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        "search_term": genai.protos.Schema(type=genai.protos.Type.STRING)
                    },
                    required=["search_term"]
                )
            ),
            genai.protos.FunctionDeclaration(
                name="delete_todo",
                description="Delete todo by ID",
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        "todo_id": genai.protos.Schema(type=genai.protos.Type.STRING)
                    },
                    required=["todo_id"]
                )
            )
        ]

    def execute_function(self, function_call) -> Dict[str, Any]:
        function_name = function_call.name
        args = {key: val for key, val in function_call.args.items()}
        
        function_map = {
            "create_todo": self.todo_client.create_todo,
            "get_todos": self.todo_client.get_todos,
            "update_todo": self.todo_client.update_todo,
            "search_todos": self.todo_client.search_todos,
            "delete_todo": self.todo_client.delete_todo
        }
        
        if function_name not in function_map:
            return {"error": f"Unknown function: {function_name}"}
        
        try:
            return function_map[function_name](**args)
        except Exception as e:
            return {"error": f"Function execution failed: {str(e)}"}

    def call_llm_with_functions(self, user_prompt: str, max_iterations: int = 5) -> str:
        try:
            self.guardrail.check_injection(user_prompt)
            self.guardrail.check_request_limit()
            
            tool_config = genai.protos.ToolConfig(
                function_calling_config=genai.protos.FunctionCallingConfig(
                    mode=genai.protos.FunctionCallingConfig.Mode.AUTO
                )
            )
            
            tools = [genai.protos.Tool(function_declarations=self.functions)]
            
            chat = self.model.start_chat()
            
            for iteration in range(max_iterations):
                response = chat.send_message(
                    user_prompt if iteration == 0 else "Continue with the next step.",
                    tools=tools,
                    tool_config=tool_config
                )
                
                self.guardrail.update_usage()
                
                if response.candidates[0].content.parts:
                    for part in response.candidates[0].content.parts:
                        if hasattr(part, 'function_call') and part.function_call:
                            function_result = self.execute_function(part.function_call)
                            logger.info(f"Called {part.function_call.name}: {function_result}")
                            
                            response = chat.send_message(
                                genai.protos.Part(
                                    function_response=genai.protos.FunctionResponse(
                                        name=part.function_call.name,
                                        response={"result": json.dumps(function_result)}
                                    )
                                )
                            )
                        elif hasattr(part, 'text') and part.text:
                            return part.text
                
                if response.candidates[0].content.parts:
                    for part in response.candidates[0].content.parts:
                        if hasattr(part, 'text') and part.text:
                            return part.text
            
            return "Max iterations reached."
            
        except (TokenLimitExceededError, PotentialInjectionError) as e:
            logger.error(f"Guardrail violation: {str(e)}")
            return f"Request blocked: {str(e)}"
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            return f"Error occurred: {str(e)}"

def main():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Set GOOGLE_API_KEY environment variable")
        return
    
    caller = GoogleFunctionCaller(api_key)
    
    prompts = [
        "Create a high priority todo 'Complete Lab 4' due 2024-01-30",
        "Show me all todos",
        "Find todos with 'Lab' in title and mark as completed",
        "Create todo 'Study AI' if it doesn't exist, otherwise update priority to HIGH"
    ]
    
    for prompt in prompts:
        print(f"\nUser: {prompt}")
        try:
            result = caller.call_llm_with_functions(prompt)
            print(f"Assistant: {result}")
            stats = caller.guardrail.get_usage_stats()
            print(f"Usage: {stats['requests_used']} requests")
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
