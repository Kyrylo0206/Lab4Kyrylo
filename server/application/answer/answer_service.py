import uuid

from application.answer.model.dto.answer import Answer
from application.answer.model.mapper.answer_mapper import AnswerMapper
from application.models import Page

class AnswerFilters:
    def __init__(self, author_id, question_id):
        self.author_id = author_id
        self.question_id = question_id

class AnswerService:
    def __init__(self):
        self.answer_mapper = AnswerMapper()
    
    def create_answer(self, request_data) -> Answer:
        answer = self.answer_mapper.map_request(request_data)
        #маписо в ентітю і берігаємо в базу
        #return questions_mapper.map_entity_to_dto(question)
        return answer
    
    def update_answer(self, answer_id, request_data) -> Answer:
        question = self.answer_mapper.map_request(request_data)
        #тут ще перед мапінгом в ентітю вигрібаємо з бази по айді і мапимо в існуючу, а не нову
        return question
    
    def get_answer(self, answer_id) -> Answer:
        #витягли з бази і замаппали в дто
        return Answer(id=answer_id, author_id=1, body='body')
    
    def get_answers(self, filters: AnswerFilters, page: int, size: int) -> Page[Answer]:
        answers = [self.get_answer(uuid.uuid4())]
        return Page(size=size, page=page, total_pages=1, content=answers)
    
