from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.controllers import user_router, auth_router
from app.core.exceptions import AppError
from fastapi.exceptions import RequestValidationError
from app.core.db_manager import db_manager
from app.core.redis_client import redis_client

from app.core.exception_handlers import (
    app_exception_handler,
    generic_exception_handler,
    validation_exception_handler,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await db_manager.start_health_check()
    await redis_client.connect()
    yield
    # Shutdown
    await db_manager.close_all()
    await redis_client.close()


app = FastAPI(title="Social Network API", version="1.0.0", lifespan=lifespan)

# Include routers
app.include_router(user_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")

# Exception handlers
app.add_exception_handler(AppError, app_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
