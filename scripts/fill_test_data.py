#!/usr/bin/env python3
"""Fill users table with realistic test data."""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import asyncio
import random
from datetime import datetime, timedelta
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db_session_factory
from app.models.user import User
from app.models.enums import Gender
from app.core.security import hash_password


# Initialize Faker for Russian locale
fake = Faker("ru_RU")

# Russian cities
CITIES = [
    "Москва",
    "Санкт-Петербург",
    "Новосибирск",
    "Екатеринбург",
    "Казань",
    "Нижний Новгород",
    "Челябинск",
    "Самара",
    "Омск",
    "Ростов-на-Дону",
    "Уфа",
    "Красноярск",
    "Пермь",
    "Воронеж",
    "Волгоград",
    "Краснодар",
    "Саратов",
    "Тюмень",
    "Тольятти",
    "Ижевск",
    "Барнаул",
    "Ульяновск",
    "Иркутск",
    "Хабаровск",
    "Ярославль",
    "Владивосток",
    "Махачкала",
    "Томск",
]

# Russian hobbies and interests
HOBBIES = [
    "чтение книг",
    "игра на гитаре",
    "фотография",
    "путешествия",
    "кулинария",
    "компьютерные игры",
    "спорт",
    "рисование",
    "танцы",
    "программирование",
    "походы",
    "плавание",
    "велосипед",
    "йога",
    "медитация",
    "садоводство",
    "рыбалка",
    "шахматы",
    "изучение языков",
    "волонтерство",
    "музыка",
    "кино",
    "театр",
    "бег",
    "фитнес",
]


def generate_biography():
    """Generate realistic Russian biography."""
    templates = [
        f"Увлекаюсь {random.choice(HOBBIES)} и {random.choice(HOBBIES)}. {fake.sentence()}",
        f"Разработчик из города {random.choice(CITIES)}. Люблю технологии и инновации.",
        f"Студент университета. Интересуюсь {random.choice(HOBBIES)} и знакомствами с новыми людьми.",
        f"Работаю {fake.job()}. В свободное время занимаюсь {random.choice(HOBBIES)}.",
        f"Предприниматель и любитель {random.choice(HOBBIES)}. Всегда ищу новые возможности.",
        f"Творческий человек, который любит {random.choice(HOBBIES)} и {random.choice(HOBBIES)}.",
        f"Путешественник и фотограф. Побывал в {random.randint(5, 25)} странах.",
        f"Энтузиаст здорового образа жизни и любитель {random.choice(HOBBIES)}. Живу полной жизнью!",
        f"Из {random.choice(CITIES)}. Обожаю {random.choice(HOBBIES)} и {random.choice(HOBBIES)}.",
        f"Активный человек, увлекающийся {random.choice(HOBBIES)}. Всегда открыт к новому!",
    ]
    return random.choice(templates)


def generate_birthdate():
    """Generate realistic birthdate (18-65 years old)."""
    start_date = datetime.now() - timedelta(days=65 * 365)
    end_date = datetime.now() - timedelta(days=18 * 365)
    return fake.date_time_between(start_date=start_date, end_date=end_date)


async def create_test_users(session: AsyncSession, count: int = 1000):
    """Create test users."""
    print(f"Creating {count} test users...")

    test_password = hash_password("password123")
    users = []
    for i in range(count):
        # Generate user data
        gender = random.choice([Gender.MALE, Gender.FEMALE])

        if gender == Gender.MALE:
            first_name = fake.first_name_male()
            last_name = fake.last_name_male()
        else:
            first_name = fake.first_name_female()
            last_name = fake.last_name_female()

        user = User(
            first_name=first_name,
            second_name=last_name,
            password=test_password,
            birthdate=generate_birthdate(),
            biography=(
                generate_biography() if random.random() > 0.1 else None
            ),  # 90% have biography
            city=(
                random.choice(CITIES) if random.random() > 0.05 else None
            ),  # 95% have city
            gender=gender,
        )
        users.append(user)

        # Batch insert every 100 users
        if len(users) >= 100:
            session.add_all(users)
            await session.commit()
            users = []
            print(f"Inserted {i + 1} users...")

    # Insert remaining users
    if users:
        session.add_all(users)
        await session.commit()

    print(f"Successfully created {count} test users!")


async def main():
    # Create session
    session_factory = await get_db_session_factory()
    async with session_factory() as session:
        # Create test users
        await create_test_users(session, 1000000)


if __name__ == "__main__":
    asyncio.run(main())
