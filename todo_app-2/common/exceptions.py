from fastapi import HTTPException, status

class FoundError(HTTPException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

class ParameterError(HTTPException):
    def __init__(self, detail: str = "Invalid parameter, wrong requests"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST)

class EventProcessingError(HTTPException):
    def __init__(self, detail: str = "Error processing event"):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)

class OutboxError(HTTPException):
    def __init__(self, detail: str = "Error in transactional outbox"):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)

class EventError(HTTPException):
    def __init__(self, detail: str = "Event error"):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)