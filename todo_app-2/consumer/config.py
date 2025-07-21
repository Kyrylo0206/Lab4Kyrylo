from pydantic import BaseSettings

class Settings(BaseSettings):
    message_broker_url: str = "amqp://localhost"  
    queue_name: str = "todo_events"
    dead_letter_queue: str = "todo_events_dead_letter"

    class Config:
        env_file_load = ".env" 

settings = Settings()