from typing import List, Dict, Any
from uuid import UUID
from datetime import datetime
from sqlalchemy import create_engine, Column, String, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Boolean 
Base = declarative_base()

class OutboxMessage(Base):
    __tablename__ = 'outbox_messages'

    id = Column(String, primary_key=True)
    event_type = Column(String, nullable=False)
    payload = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    aggregate_type = Column(String, nullable=False)
    headers = Column(JSON, nullable=True)#for my tracing
    processed = Column(Boolean, default=False)
    processed_at = Column(DateTime, nullable=True)


class Outbox:
    def __init__(self, db_url: str):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def add_message(self, event_type: str, payload: Dict[str, Any]) -> None:
        session = self.Session()
        message = OutboxMessage(id=str(UUID()), event_type=event_type, payload=payload)
        session.add(message)
        session.commit()
        session.close()

    def get_messages(self) -> List[OutboxMessage]:
        session = self.Session()
        messages = session.query(OutboxMessage).all()
        session.close()
        return messages

    def clear_messages(self) -> None:
        session = self.Session()
        session.query(OutboxMessage).delete()
        session.commit()
        session.close()