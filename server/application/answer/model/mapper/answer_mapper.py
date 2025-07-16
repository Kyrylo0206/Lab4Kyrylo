import uuid
from application.answer.model.dto.answer import Answer

class AnswerMapper:

    def map_request(self, request_data):
        #Should be immutable
        question = Answer(id = request_data.get('id') or uuid.uuid4(), 
                            author_id=request_data.get('author_id'), 
                            question_id=request_data.get('question_id'),
                            body=request_data.get('body'),
                            score=request_data.get('score')
                         )
        
        return question
    
    
    def map_entity_to_dto(self, entity):
        return Answer(id = entity.id,
                        author_id=entity.author_id,
                        question_id=entity.question_id,
                        body=entity.body,
                        score=entity.score
                    )