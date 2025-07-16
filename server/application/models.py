from typing import TypeVar, Generic, List
from dataclasses import dataclass

T = TypeVar('T')
class Page(Generic[T]):
    def __init__(self, size: int, page: int, total_pages: int, content: List[T]):
        self.size = size
        self.page = page
        self.total_pages = total_pages
        self.content = content

    def print_content(self):
        print(self.content)
        
    def to_json(self):
        return {
            'size': self.size,
            'page': self.page,
            'total_pages': self.total_pages,
            'content': [item.__dict__ for item in self.content]
        }

    
    