from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.logger import logger
from app.core.exceptions import AppError
from app.resources import strings
import uuid


async def app_exception_handler(request: Request, exc: AppError) -> JSONResponse:
    """App exception handler."""
    logger.error(f"AppError: {exc.description}")

    return JSONResponse(
        status_code=exc.status_code, content={"description": exc.description}
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected server errors."""
    request_id = str(uuid.uuid4())
    logger.error(f"Unexpected error: {str(exc)} | request_id: {request_id}")

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "message": "Internal server error",
            "request_id": request_id,
            "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        },
        headers={"Retry-After": "30"},
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Convert 422 validation errors to 400."""
    logger.error(f"Validation error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"description": strings.NOT_VALID_ERROR_MSG},
    )
