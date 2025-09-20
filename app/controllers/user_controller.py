from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.user_service import UserService
from app.schemas.user import UserCreate, UserRegisterResponse, UserResponse
from app.logger import logger
from app.core.exceptions import AppError
from app.resources import strings
from uuid import UUID
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/user", tags=["User"])


async def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(db)


@router.post(
    "/register", response_model=UserRegisterResponse, status_code=status.HTTP_200_OK
)
async def create_user(
    user_data: UserCreate, service: UserService = Depends(get_user_service)
):

    logger.info(f"user_data: {user_data.model_dump(exclude={'password'})}")

    return await service.create_user(user_data)


@router.get(
    "/get/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK
)
async def get_user(
    user_id: UUID,
    service: UserService = Depends(get_user_service),
    # current_user: dict = Depends(get_current_user),
):
    logger.info(f"user_id: {user_id}")
    # logger.info(
    #     f"From token: user_id : {current_user['user_id']}, first_name: {current_user['first_name']}, second_name: {current_user['second_name']}"
    # )

    user = await service.get_user_by_id(user_id)
    if not user:
        raise AppError(strings.NOT_FOUND_USER_ERROR_MSG, status.HTTP_404_NOT_FOUND)
    return user
