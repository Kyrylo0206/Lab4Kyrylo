import pika
import json
import os
import logging
from dotenv import load_dotenv
from jaeger_client import Config
import opentracing

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

def init_tracer():
    config = Config(
        config={
            'sampler': {'type': 'const', 'param': 1},
            'logging': True,
            'local_agent': {
                'reporting_host': os.getenv('JAEGER_AGENT_HOST', 'jaeger'),
                'reporting_port': int(os.getenv('JAEGER_AGENT_PORT', '6831')),
            },
        },
        service_name=os.getenv("JAEGER_SERVICE_NAME", "todo-consumer"),
        validate=True,
    )
    return config.initialize_tracer()

def process_message(ch, method, properties, body):
    with tracer.start_span('process_message') as span:
        try:
            message = json.loads(body)
            logger.info(f"Received message: {message}")
            span.set_tag('message', message)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            span.set_tag('error', str(e))
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

def main():
    global tracer
    tracer = init_tracer()

    rabbitmq_url = os.getenv('RABBITMQ_URL')
    queue_name = os.getenv('TODO_QUEUE')

    connection = pika.BlockingConnection(pika.URLParameters(rabbitmq_url))
    channel = connection.channel()

    channel.queue_declare(queue=queue_name, durable=True)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue_name, on_message_callback=process_message)
    logger.info('Consumer started. Waiting for messages...')
    channel.start_consuming()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info('Consumer stopped.')