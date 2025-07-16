import uuid
import json
from dataclasses import dataclass

@dataclass
class Question:
    id: uuid.UUID
    author_id: uuid.UUID
    body: str
