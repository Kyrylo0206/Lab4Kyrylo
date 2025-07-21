from pydantic import BaseSettings

class Settings(BaseSettings):
    message_broker_url: str = "amqp://localhost"  
    queue_name: str = "todo_events"
    dead_letter_queue: str = "todo_events_dead_letter"
    jaeger_agent_host: str = "jaeger"
    jaeger_agent_port: int = 6831
    jaeger_service_name: str = "todo-producer"

    class Config:
        env_file_load = ".env" 

settings = Settings()
