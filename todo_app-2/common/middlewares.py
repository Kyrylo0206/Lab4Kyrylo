from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from common.exceptions import ParameterError, FoundError
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)

class GlobalExceptionHandler(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response

        except RequestValidationError as ve:  
            errors = []
            for err in ve.errors():
                loc = ".".join(str(loc) for loc in err["loc"])
                msg = f"{loc}: {err['msg']}"
                errors.append(msg)
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={
                    "code": status.HTTP_422_UNPROCESSABLE_ENTITY,
                    "message": "Validation error",
                    "details": errors
                },
            )

        except ValidationError as ve:  
            errors = []
            for err in ve.errors():
                loc = ".".join(str(loc) for loc in err["loc"])
                msg = f"{loc}: {err['msg']}"
                errors.append(msg)
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={
                    "code": status.HTTP_422_UNPROCESSABLE_ENTITY,
                    "message": "Validation error",
                    "details": errors
                },
            )

        except ParameterError as ipe:
            return JSONResponse(
                status_code=ipe.status_code,
                content={
                    "code": ipe.status_code,
                    "message": ipe.detail,
                    "details": None
                },
            )
        except FoundError as fe:
            return JSONResponse(
                status_code=fe.status_code,
                content={
                    "code": fe.status_code,
                    "message": fe.detail,
                    "details": None
                },
            )
        except Exception as ex:
            logger.error(f"Internal server error: {str(ex)}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "message": "Internal server error",
                    "details": [str(ex)]
                },
            )