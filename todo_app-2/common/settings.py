from typing import Final

PAGE_SIZE_DEFAULT: Final[int] = 10
PAGE_SIZE_MAX: Final[int] = 100

MESSAGE_BROKER_URL: Final[str] = "amqp://user:password@localhost:5672/"
DEAD_LETTER_QUEUE: Final[str] = "dead_letter_queue"