import asyncio

from sqlalchemy import text

from secure_shortener.db import SessionLocal


async def main() -> None:
    async with SessionLocal() as session:
        await session.execute(text("TRUNCATE TABLE links RESTART IDENTITY"))
        await session.commit()


if __name__ == "__main__":
    asyncio.run(main())
