import uuid
from application.question.model.dto.question import Question

class QuestionMapper:

    def map_request(self, request_data):
        #Should be immutable
        question = Question(id = request_data.get('id') or uuid.uuid4(), 
                            author_id=request_data.get('author_id'),
                            body=request_data.get('body')
                            )
        
        return question
    
    
    def map_entity_to_dto(self, entity):
        return Question(id = entity.id, 
                        author_id=entity.author_id,
                        body=entity.body
                        )