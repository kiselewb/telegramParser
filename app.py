import asyncio

from database.db_manager import DBManager
from services.logger import Logger
from services.parser_data_manager import ParserDataManager
from services.limit_manager import LimitManager
from core.bot.bot import TGBot
from core.client.client import TGClient

logger = Logger(__name__).setup_logger()


class Application:
    def __init__(self, session_name: str, api_id: int, api_hash: str, bot_token: str):
        self.db = DBManager()
        self.pdm = ParserDataManager(self.db)
        self.lm = LimitManager()

        self.client = TGClient(
            session_name=session_name,
            api_id=api_id,
            api_hash=api_hash,
            db=self.db,
            pdm=self.pdm,
            lm=self.lm,
        )
        self.bot = TGBot(
            bot_token=bot_token,
            db=self.db,
            pdm=self.pdm,
            lm=self.lm,
        )
        self.tasks = []

    async def start(self):
        logger.info("🚀 Запуск Приложения...")

        await self.pdm.init()

        lm_task = asyncio.create_task(self.lm.init(), name="lm")
        await self.lm.wait_ready()

        client_task = asyncio.create_task(self.client.run(), name="TelegramClient")
        bot_task = asyncio.create_task(self.bot.run(), name="TelegramBot")

        self.tasks = [lm_task, client_task, bot_task]

        logger.info("✅ Все компоненты Приложения запущены")

    async def stop(self):
        logger.info("🛑  Остановка Приложения...")

        for task in self.tasks:
            if not task.done():
                task.cancel()

        await asyncio.gather(*self.tasks, return_exceptions=True)

        await self.lm.stop()
        await self.client.stop()
        await self.bot.stop()

        logger.info("✅ Приложение остановлено")

    async def run(self):
        try:
            await self.start()
            await asyncio.gather(*self.tasks)

        except asyncio.exceptions.CancelledError:
            logger.info("⚠️ Получен сигнал остановки Приложения")

        except Exception as e:
            logger.error(f"❌ Критическая ошибка Приложения: {e}")

        finally:
            await self.stop()
