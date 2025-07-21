import pika
import json
import os
import logging
import time
from datetime import datetime
from typing import Dict, Any
from jaeger_client import Config
import opentracing
from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_tracer():
    config = Config(
        config={
            'sampler': {'type': 'const', 'param': 1},
            'logging': True,
            'local_agent': {
                'reporting_host': settings.jaeger_agent_host,
                'reporting_port': settings.jaeger_agent_port,
            },
        },
        service_name=settings.jaeger_service_name,
        validate=True,
    )
    return config.initialize_tracer()

class EventProducer:
    def __init__(self, tracer=None):
        self.tracer = tracer or init_tracer()
        self.connection = None
        self.channel = None
        self._setup_connection()

    def _setup_connection(self):
        try:
            self.connection = pika.BlockingConnection(
                pika.URLParameters(settings.message_broker_url)
            )
            self.channel = self.connection.channel()
            
            self.channel.queue_declare(
                queue=settings.queue_name, 
                durable=True
            )
            
            self.channel.queue_declare(
                queue=settings.dead_letter_queue, 
                durable=True
            )
            
            logger.info("Connection to RabbitMQ established")
            
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise

    def send_event(self, event_type: str, payload: Dict[str, Any], correlation_id: str = None) -> bool:
        with self.tracer.start_span('send_event') as span:
            span.set_tag('event_type', event_type)
            span.set_tag('correlation_id', correlation_id)
            
            message = {
                'event_type': event_type,
                'payload': payload,
                'timestamp': datetime.utcnow().isoformat(),
                'correlation_id': correlation_id,
                'service': settings.jaeger_service_name
            }
            
            try:
                for attempt in range(3):
                    try:
                        self.channel.basic_publish(
                            exchange='',
                            routing_key=settings.queue_name,
                            body=json.dumps(message),
                            properties=pika.BasicProperties(
                                delivery_mode=2,
                                correlation_id=correlation_id,
                                headers={'event_type': event_type}
                            )
                        )
                        
                        logger.info(f"Event sent successfully: {event_type} (attempt {attempt + 1})")
                        span.set_tag('success', True)
                        span.set_tag('attempt', attempt + 1)
                        return True
                        
                    except Exception as e:
                        logger.warning(f"Attempt {attempt + 1} failed: {e}")
                        if attempt < 2: 
                            time.sleep(1)
                        else:
                            raise
                            
            except Exception as e:
                logger.error(f"Failed to send event after 3 attempts: {e}")
                span.set_tag('error', str(e))
                span.set_tag('success', False)
                return False

    def send_batch_events(self, events: list) -> Dict[str, int]:
        with self.tracer.start_span('send_batch_events') as span:
            stats = {'success': 0, 'failed': 0}
            span.set_tag('batch_size', len(events))
            
            for event in events:
                success = self.send_event(
                    event['event_type'], 
                    event['payload'],
                    event.get('correlation_id')
                )
                
                if success:
                    stats['success'] += 1
                else:
                    stats['failed'] += 1
            
            span.set_tag('success_count', stats['success'])
            span.set_tag('failed_count', stats['failed'])
            
            logger.info(f"Batch processing completed: {stats}")
            return stats

    def close(self):
        """Закриття з'єднання"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            logger.info("RabbitMQ connection closed")

def main():
    """Демонстрація роботи producer"""
    producer = EventProducer()
    
    try:
        producer.send_event(
            "todo_created", 
            {"id": "123", "title": "Test Task", "status": "pending"},
            correlation_id="test-123"
        )
        
        events = [
            {
                'event_type': 'todo_updated',
                'payload': {'id': '124', 'title': 'Updated Task', 'status': 'completed'},
                'correlation_id': 'batch-1'
            },
            {
                'event_type': 'todo_deleted',
                'payload': {'id': '125'},
                'correlation_id': 'batch-2'
            }
        ]
        
        stats = producer.send_batch_events(events)
        logger.info(f"Batch processing stats: {stats}")
        
    except KeyboardInterrupt:
        logger.info("Producer stopped by user")
    except Exception as e:
        logger.error(f"Producer error: {e}")
    finally:
        producer.close()

if __name__ == "__main__":
    main()
