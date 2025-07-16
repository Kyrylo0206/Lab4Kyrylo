import json
import requests
import openai
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()  

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# TIP: Use client u've created in class activity
class QuestionAPIClient:
    def __init__(self, base_url: str = "http://localhost:5002"):
        self.base_url = base_url

    def create_question(self, author_id: str, body: str) -> Dict[str, Any]:
        try:
            response = requests.post(
                f"{self.base_url}/questions",
                json={
                    "author_id": author_id,
                    "body": body
                }
            )
            return {"status": response.status_code, "data": response.json()}
        except Exception as e:
            return {"error": str(e)}

    def get_questions(self, author_id: Optional[str] = None,
                     page: Optional[int] = None, 
                     size: Optional[int] = None) -> Dict[str, Any]:
        try:
            params = {}
            if author_id: params["author_id"] = author_id
            if page: params["page"] = page
            if size: params["size"] = size
            
            response = requests.get(f"{self.base_url}/questions", params=params)
            return {"status": response.status_code, "data": response.json()}
        except Exception as e:
            return {"error": str(e)}

    def get_question(self, question_id: str) -> Dict[str, Any]:
        try:
            response = requests.get(f"{self.base_url}/questions/{question_id}")
            return {"status": response.status_code, "data": response.json()}
        except Exception as e:
            return {"error": str(e)}

    def update_question(self, question_id: str, body: str) -> Dict[str, Any]:
        try:
            response = requests.put(
                f"{self.base_url}/questions/{question_id}",
                json={"body": body}
            )
            return {"status": response.status_code, "data": response.json()}
        except Exception as e:
            return {"error": str(e)}

QUESTION_FUNCTIONS = [
    {
        "type": "function",
        "function": {
            "name": "create_question",
            "description": "Create a new question in the Q&A system",
            "parameters": {
                "type": "object",
                "properties": {
                    "author_id": {"type": "string", "description": "ID of the question author"},
                    "body": {"type": "string", "description": "Content/body of the question"}
                },
                "required": ["author_id", "body"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_questions",
            "description": "Retrieve questions with optional filtering by author and pagination",
            "parameters": {
                "type": "object",
                "properties": {
                    "author_id": {"type": "string", "description": "Filter by author ID"},
                    "page": {"type": "integer", "description": "Page number for pagination"},
                    "size": {"type": "integer", "description": "Number of items per page"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_question",
            "description": "Get a specific question by its ID",
            "parameters": {
                "type": "object",
                "properties": {
                    "question_id": {"type": "string", "description": "ID of the question to retrieve"}
                },
                "required": ["question_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_question",
            "description": "Update the body/content of an existing question",
            "parameters": {
                "type": "object",
                "properties": {
                    "question_id": {"type": "string", "description": "ID of the question to update"},
                    "body": {"type": "string", "description": "New content/body for the question"}
                },
                "required": ["question_id", "body"]
            }
        }
    }
]

def execute_function(function_name: str, arguments: Dict[str, Any], client: QuestionAPIClient) -> str:
    """Execute the function call and return result as string"""
    if function_name == "create_question":
        result = client.create_question(**arguments)
    elif function_name == "get_questions":
        result = client.get_questions(**arguments)
    elif function_name == "get_question":
        result = client.get_question(**arguments)
    elif function_name == "update_question":
        result = client.update_question(**arguments)
    else:
        return f"Unknown function: {function_name}"
    
    return json.dumps(result, indent=2)

def chat_with_questions_api(user_message: str, client: QuestionAPIClient):
    """Have a conversation with GPT-4o that can call your Questions API"""
    
    messages = [
        {
            "role": "system", 
            "content": """You are an AI assistant that can interact with a Q&A REST API for managing questions. 
            You can create, read, and update questions. When users ask you to perform operations on questions, 
            use the available functions to interact with the API. Ask for clarification if not enough information is available.
            
            Note: This system doesn't support DELETE operations for questions because in distributed systems, 
            deletes are typically avoided to maintain data consistency and audit trails."""
        },
        {"role": "user", "content": user_message}
    ]
    
    logger.info(f"User: {user_message}")
    
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=QUESTION_FUNCTIONS,
        tool_choice="auto"
    )
    
    message = response.choices[0].message
    messages.append(message)
    
    if message.tool_calls:
        logger.info("\nGPT-4o is calling functions...")
        
        for tool_call in message.tool_calls:
            function_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            
            logger.info(f"Function: {function_name}")
            logger.info(f"Arguments: {json.dumps(arguments, indent=2)}")
            
            function_result = execute_function(function_name, arguments, client)
            logger.info(f"API Response: {function_result}")
            
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": function_result
            })
        
        final_response = openai.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )
        
        logger.info(f"\nGPT-4o: {final_response.choices[0].message.content}")
    else:
        logger.info(f"\nGPT-4o: {message.content}")

def run_questions_demo():
    client = QuestionAPIClient()
    
    logger.info("=== GPT-4o Questions Function Calling Demo ===\n")
    
    logger.info("Demo 1: Creating a question")
    chat_with_questions_api(
        "Create a question by author 'alice_123' asking 'What is the difference between REST and GraphQL?'",
        client
    )
    
    logger.info("\n" + "="*50 + "\n")
    

if __name__ == "__main__":
    logger.info("Make sure your Flask app is running on http://localhost:5002")
    logger.info("Set your OpenAI API key in the script before running!")
    
    run_questions_demo()