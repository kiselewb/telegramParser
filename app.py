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
        self._stop_called = False

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
        if self._stop_called:
            return
        self._stop_called = True

        logger.info("🛑 Остановка Приложения...")

        for task in self.tasks:
            if not task.done():
                task.cancel()

        stop_tasks = []

        stop_tasks.append(asyncio.create_task(self._safe_stop(self.lm.stop(), "LimitManager")))
        stop_tasks.append(asyncio.create_task(self._safe_stop(self.client.stop(), "Client")))
        stop_tasks.append(asyncio.create_task(self._safe_stop(self.bot.stop(), "Bot")))

        try:
            await asyncio.wait_for(
                asyncio.gather(*stop_tasks, return_exceptions=True),
                timeout=5.0
            )
        except asyncio.TimeoutError:
            logger.warning("⚠️ Таймаут при остановке компонентов")

        try:
            await asyncio.wait_for(
                asyncio.gather(*self.tasks, return_exceptions=True),
                timeout=3.0
            )
        except asyncio.TimeoutError:
            logger.warning("⚠️ Таймаут при завершении задач")

        logger.info("✅ Приложение остановлено")

    async def _safe_stop(self, coro, name):
        try:
            await coro
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.warning(f"⚠️ Ошибка при остановке {name}: {e}")

    async def run(self):
        try:
            await self.start()

            await asyncio.gather(*self.tasks, return_exceptions=True)

        except asyncio.CancelledError:
            logger.info("⚠️ Получен сигнал остановки Приложения")
            raise

        except Exception as e:
            logger.error(f"❌ Критическая ошибка Приложения: {e}")
            raise

        finally:
            await self.stop()