from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_write_db, get_read_db
from app.services.user_service import UserService
from app.schemas.user import UserCreate, UserRegisterResponse, UserResponse
from app.logger import logger
from app.core.exceptions import AppError
from app.resources import strings
from uuid import UUID
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/user", tags=["User"])


async def get_write_user_service(
    db: AsyncSession = Depends(get_write_db),
) -> UserService:
    return UserService(db)


async def get_read_user_service(db: AsyncSession = Depends(get_read_db)) -> UserService:
    return UserService(db)


@router.post(
    "/register", response_model=UserRegisterResponse, status_code=status.HTTP_200_OK
)
async def create_user(
    user_data: UserCreate, service: UserService = Depends(get_write_user_service)
):

    logger.info(f"user_data: {user_data.model_dump(exclude={'password'})}")

    return await service.create_user(user_data)


@router.get(
    "/get/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK
)
async def get_user(
    user_id: UUID,
    service: UserService = Depends(get_read_user_service),
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


@router.get(
    "/search", response_model=list[UserResponse], status_code=status.HTTP_200_OK
)
async def search_users(
    first_name: str,
    second_name: str,
    service: UserService = Depends(get_read_user_service),
):
    if len(first_name) < 2 or len(second_name) < 2:
        raise AppError(strings.TO_SHORT_SEARCHING_PARAMS, status.HTTP_400_BAD_REQUEST)

    logger.info(f"Searching users: first_name={first_name}, last_name={second_name}")

    users = await service.search_users(first_name, second_name)

    if not users:
        raise AppError(strings.NOT_FOUND_USER_ERROR_MSG, status.HTTP_404_NOT_FOUND)

    return users


@router.put("/friend/set/{user_id}", status_code=status.HTTP_200_OK)
async def add_friend(
    user_id: UUID,
    service: UserService = Depends(get_write_user_service),
    current_user: dict = Depends(get_current_user),
):
    logger.info(f"Adding friend: user_id={user_id}, current_user={current_user['user_id']}")
    await service.add_friend(current_user["user_id"], user_id)
    return {"message": "Пользователь успешно указал своего друга"}


@router.put("/friend/delete/{user_id}", status_code=status.HTTP_200_OK)
async def delete_friend(
    user_id: UUID,
    service: UserService = Depends(get_write_user_service),
    current_user: dict = Depends(get_current_user),
):
    logger.info(f"Deleting friend: user_id={user_id}, current_user={current_user['user_id']}")
    await service.delete_friend(current_user["user_id"], user_id)
    return {"message": "Пользователь успешно удалил из друзей пользователя"}
