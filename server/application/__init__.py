from flask import Flask
from application.question.questions_service import QuestionsService
from application.answer.answer_service import AnswerService


app = Flask(__name__)
questions_service  = QuestionsService()
answers_service = AnswerService()

import application.question.questions_controller
import application.answer.answer_controller