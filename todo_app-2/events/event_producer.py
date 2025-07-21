import os
import json
import pika
from datetime import datetime
from common.exceptions import EventError

class EventProducer:
    def __init__(self):
        self.rabbitmq_url = os.getenv("RABBITMQ_URL")
        self.queue_name = os.getenv("TODO_QUEUE")

    def send_event(self, event_type: str, payload: dict) -> None:
        connection = pika.BlockingConnection(pika.URLParameters(self.rabbitmq_url))
        channel = connection.channel()
        
        channel.queue_declare(queue=self.queue_name, durable=True)
        
        try:
            channel.basic_publish(
                exchange='',
                routing_key=self.queue_name,
                body=json.dumps({
                    'event_type': event_type,
                    'payload': payload,
                    'timestamp': datetime.utcnow().isoformat()
                }),
                properties=pika.BasicProperties(
                    delivery_mode=2,
                )
            )
        finally:
            connection.close()