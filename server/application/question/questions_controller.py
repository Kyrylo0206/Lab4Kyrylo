from application import app
from flask import request, jsonify
from application import app, questions_service
from application.question.questions_service import QuestionFilters
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.route('/questions', methods=['POST'])
def create_question():
    logger.info(f"create_question called with request data: {request.json}")
    request_data = request.json
    question = questions_service.create_question(request_data)
    logger.info(f"create_question result: {question}")
    return jsonify(question), 201

@app.route('/questions', methods=['GET'])
def get_questions():
    author_id = request.args.get('author_id')
    page = request.args.get('page')
    size = request.args.get('size')
    logger.info(f"get_questions called with args: author_id={author_id}, page={page}, size={size}")
    
    questions = questions_service.get_questions(QuestionFilters(author_id), page, size)
    questions.print_content()
    logger.info(f"get_questions result: {len(questions.content)} questions found")
    return jsonify(questions.to_json()), 200


@app.route('/questions/<question_id>', methods=['GET'])
def get_question(question_id):
    logger.info(f"get_question called with question_id: {question_id}")
    question = questions_service.get_question(question_id)
    if question is None:
        logger.warning(f"get_question: Question not found for id: {question_id}")
        return jsonify({'error': 'Question not found'}), 404
    logger.info(f"get_question result: {question}")
    return jsonify(question), 200

@app.route('/questions/<question_id>', methods=['PUT'])
def update_question(question_id):
    logger.info(f"update_question called with question_id: {question_id}, request_data: {request.json}")
    request_data = request.json
    question = questions_service.update_question(question_id, request_data)
    if question is None:
        logger.warning(f"update_question: Question not found for id: {question_id}")
        return jsonify({'error': 'Question not found'}), 404
    logger.info(f"update_question result: {question}")
    return jsonify(question), 200

# @app.route('/questions/<question_id>', methods=['DELETE'])
# def delete_question(question_id):
# а в розподілених системах нема делівтів (тільки для тестів). Давайте поговоримо чому так