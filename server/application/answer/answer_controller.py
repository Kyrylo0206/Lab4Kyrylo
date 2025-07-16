from application import app
from flask import request, jsonify
from application import app, answers_service
from application.answer.answer_service import AnswerFilters

# /questions/<question_id>/answers - давайте обговоримо за і проти такої архітектури
@app.route('/answers', methods=['POST'])
def create_answer():

    request_data = request.json
    answer = answers_service.create_answer(request_data)
    return jsonify(answer), 201

@app.route('/answers', methods=['GET'])
def get_answers():
    author_id = request.args.get('author_id')
    question_id = request.args.get('question_id')
    page = request.args.get('page')
    size = request.args.get('size')

    answers = answers_service.get_answers(AnswerFilters(author_id,question_id), page, size)
    answers.print_content()
    return jsonify(answers.to_json()), 200


@app.route('/answers/<answer_id>', methods=['GET'])
def get_answer(answer_id):
    answer = answers_service.get_answer(answer_id)
    if answer is None:
        return jsonify({'error': 'Answer not found'}), 404
    return jsonify(answer), 200

@app.route('/answers/<answer_id>', methods=['PUT'])
def update_answer(answer_id):
    request_data = request.json
    answer = answers_service.update_answer(answer_id, request_data)
    if answer is None:
        return jsonify({'error': 'Answer not found'}), 404
    return jsonify(answer), 200

# Питання з *** - як реалізуємо апвоут?