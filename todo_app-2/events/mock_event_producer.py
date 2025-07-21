"""
Mock Event Producer для тестування GraphQL API без RabbitMQ
"""
import json
from datetime import datetime
from typing import Dict, Any

class MockEventProducer:
    """Mock implementation of EventProducer for testing without RabbitMQ"""
    
    def __init__(self):
        self.events = []  # Зберігаємо події в пам'яті для тестування
        print("📡 MockEventProducer initialized (no RabbitMQ required)")
    
    def send_event(self, event_type: str, payload: Dict[str, Any]) -> None:
        """Відправити подію (mock implementation)"""
        event = {
            "event_type": event_type,
            "payload": payload,
            "timestamp": datetime.utcnow().isoformat(),
            "event_id": len(self.events) + 1
        }
        
        self.events.append(event)
        print(f"📨 Event sent: {event_type} -> {json.dumps(payload, default=str)}")
        
        # Для GraphQL subscriptions - додаємо в чергу
        try:
            import asyncio
            from graphqlapi.schema import event_queue
            
            # Додаємо подію в чергу для subscriptions
            event_data = {
                'id': str(event.get('event_id')),
                'event_type': event_type,
                'payload': payload,
                'created_at': event['timestamp']
            }
            
            # Створюємо task для додавання в чергу
            try:
                loop = asyncio.get_event_loop()
                loop.create_task(event_queue.put(event_data))
            except RuntimeError:
                # Якщо немає активного event loop, пропускаємо
                pass
                
        except Exception as e:
            print(f"⚠️ Could not add event to subscription queue: {e}")
    
    def get_events(self):
        """Отримати всі події (для тестування)"""
        return self.events
    
    def clear_events(self):
        """Очистити список подій"""
        self.events.clear()
