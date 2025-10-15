import asyncio
import pytest
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.settings import settings
from app.core.database import make_url_async


@pytest.mark.asyncio
async def test_bulk_insert_1000_records():
    """Test inserting 1000 records using raw SQL."""
    engine = create_async_engine(make_url_async(settings.DATABASE_URL))

    try:
        # Setup: Create table and clear data
        async with engine.begin() as conn:
            await conn.execute(
                text(
                    """
                CREATE TABLE IF NOT EXISTS test_repl (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255)
                )
            """
                )
            )
            await conn.execute(text("DELETE FROM test_repl"))

        # Insert records with individual commits
        for i in range(1000):
            async with engine.connect() as conn:
                await conn.execute(text("INSERT INTO test_repl(name) VALUES ('test1')"))
                await conn.commit()
            print("inserted rows = " + str(i + 1))
            await asyncio.sleep(2)

        # Verify count
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT COUNT(*) FROM test_repl"))
            count = result.scalar()
            assert count == 1000

    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(test_bulk_insert_1000_records())
