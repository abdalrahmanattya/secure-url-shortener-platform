import asyncio

from secure_shortener.db import SessionLocal
from secure_shortener.service import create_link


async def main() -> None:
    async with SessionLocal() as session:
        await create_link(
            session, "https://example.com/architecture", "owner-demo", "architecture", None
        )
        await create_link(session, "https://example.com/security", "owner-demo", "security", None)


if __name__ == "__main__":
    asyncio.run(main())
