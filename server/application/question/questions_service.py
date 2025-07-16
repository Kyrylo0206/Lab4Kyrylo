import uuid

from application.question.model.dto.question import Question
from application.question.model.mapper.question_mapper import QuestionMapper
from application.models import Page

class QuestionFilters:
    def __init__(self, author_id):
        self.author_id = author_id

class QuestionsService:
    def __init__(self):
        self.questions_mapper = QuestionMapper()
    
    def create_question(self, request_data) -> Question:
        question = self.questions_mapper.map_request(request_data)
        #маписо в ентітю і берігаємо в базу
        #return questions_mapper.map_entity_to_dto(question)
        return question
    
    def update_question(self, question_id, request_data) -> Question:
        question = self.questions_mapper.map_request(request_data)
        #тут ще перед мапінгом в ентітю вигрібаємо з бази по айді і мапимо в існуючу, а не нову
        return question
    
    def get_question(self, question_id) -> Question:
        #витягли з бази і замаппали в дто
        return Question(id=question_id, author_id=1, body='body')
    
    def get_questions(self, filters: QuestionFilters, page: int, size: int) -> Page[Question]:
        questions = [self.get_question(uuid.uuid4())]
        return Page(size=size, page=page, total_pages=1, content=questions)