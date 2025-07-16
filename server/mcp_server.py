import logging
from typing import Any, Dict, Optional, List
from fastmcp import FastMCP
from application import questions_service
from application.question.questions_service import QuestionFilters


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("Questions Management Server")

# TOOLS - Actions/Operations
@mcp.tool()
def create_question(author_id: str, body: str) -> Dict[str, Any]:
    """Create a new question in the Q&A system"""
    logger.info(f"MCP create_question called with author_id={author_id}, body={body}")
    try:
        request_data = {"author_id": author_id, "body": body}
        question = questions_service.create_question(request_data)
        logger.info(f"MCP create_question result: {question}")
        return {"success": True, "data": question}
    except Exception as e:
        logger.error(f"MCP create_question error: {str(e)}")
        return {"success": False, "error": str(e)}

@mcp.resource("questions://all")
def get_all_questions_resource() -> str:
    """Get all questions as a resource"""
    logger.info("MCP get_all_questions_resource called")
    try:
        questions = questions_service.get_questions(QuestionFilters(None), None, None)
        
        if not questions.content:
            return "No questions found in the system."
        
        resource_content = f"Total Questions: {len(questions.content)}\n\n"
        for i, question in enumerate(questions.content, 1):
            resource_content += f"Question {i}:\n"
            resource_content += f"  ID: {question.id}\n"
            resource_content += f"  Author: {question.author_id}\n"
            resource_content += f"  Body: {question.body}\n"
        
        logger.info(f"MCP get_all_questions_resource result: {len(questions.content)} questions")
        return resource_content
    except Exception as e:
        logger.error(f"MCP get_all_questions_resource error: {str(e)}")
        return f"Error retrieving questions: {str(e)}"

# PROMPTS - Templates for generating content
@mcp.prompt()
def list_all_questions() -> str:
    """Generate a formatted list of all questions in the system"""
    logger.info("MCP list_all_questions prompt called")
    try:
        questions = questions_service.get_questions(QuestionFilters(None), None, None)
        
        if not questions.content:
            return "No questions found in the system."
        
        formatted_questions = []
        for i, question in enumerate(questions.content, 1):
            formatted_questions.append(
                f"{i}. ID: {question.id}\n"
                f"   Author: {question.author_id}\n"
                f"   Body: {question.body}\n"
            )
        
        result = f"Found {len(questions.content)} questions:\n\n" + "\n".join(formatted_questions)
        logger.info(f"MCP list_all_questions result: {len(questions.content)} questions")
        return result
    except Exception as e:
        logger.error(f"MCP list_all_questions error: {str(e)}")
        return f"Error retrieving questions: {str(e)}"

@mcp.prompt()
def question_summary(question_id: str) -> str:
    """Generate a summary for a specific question"""
    logger.info(f"MCP question_summary prompt called with question_id={question_id}")
    try:
        question = questions_service.get_question(question_id)
        if question is None:
            return f"Question with ID {question_id} not found."
        
        summary = f"""Question Summary:
                        ID: {question.id}
                        Author: {question.author_id}
                        Question: {question.body}
                        Character Count: {len(question.body)}
                        Word Count: {len(question.body.split())}"""
        
        logger.info(f"MCP question_summary result: summary generated: {summary}" )
        return summary
    except Exception as e:
        logger.error(f"MCP question_summary error: {str(e)}")
        return f"Error generating summary for question {question_id}: {str(e)}"

if __name__ == "__main__":
    mcp.run()