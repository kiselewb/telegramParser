import asyncio

from app import Application
from config.settings import settings


async def main():
    app = Application(
        session_name=settings.SESSION_NAME,
        api_id=settings.API_ID,
        api_hash=settings.API_HASH,
        bot_token=settings.BOT_TOKEN,
    )

    await app.run()


if __name__ == "__main__":
    asyncio.run(main())
