from fastapi import FastAPI
from app.controllers import user_router, auth_router
from app.core.exceptions import AppError
from fastapi.exceptions import RequestValidationError

from app.core.exception_handlers import (
    app_exception_handler,
    generic_exception_handler,
    validation_exception_handler,
)

app = FastAPI(title="Social Network API", version="1.0.0")

# Include routers
app.include_router(user_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")

# Exception handlers
app.add_exception_handler(AppError, app_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
