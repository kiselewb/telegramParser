import asyncio
from telethon import TelegramClient

from config.paths import SESSIONS_DIR
from core.client.handlers import ClientHandlers
from config.settings import settings
from database.db_manager import DBManager
from services.limit_manager import LimitManager
from services.logger import Logger
from services.parser_data_manager import ParserDataManager

logger = Logger(__name__).setup_logger()


class TGClient:
    def __init__(self, session_name: str, api_id: int, api_hash: str, db: DBManager, pdm: ParserDataManager, lm: LimitManager):
        SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
        self.config = settings
        self.is_running = False
        self.client = TelegramClient(session_name, api_id, api_hash)
        self.handlers = ClientHandlers(self.client, db, pdm, lm, self.config)

    async def start(self):
        if not self.is_running:
            await self.client.start(
                phone=self.config.ADMIN_PHONE,
                # password=self.config.ADMIN_PASSWORD
            )
            self.handlers.register()
            self.is_running = True
            logger.info("✅ Клиент запущен и готов к работе")

    async def stop(self):
        if self.is_running:
            logger.info("🔄  Остановка Клиент...")
            await self.client.disconnect()
            self.is_running = False
            logger.info("✅ Соединение Клиента закрыто корректно")

    async def run(self):
        try:
            await self.start()
            logger.info("🤖  Клиента работает. Нажмите Ctrl+C для остановки")
            await self.client.run_until_disconnected()

        except asyncio.exceptions.CancelledError:
            logger.info("⚠️  Получен сигнал остановки Клиента")
            raise

        except Exception as e:
            logger.error(f"❌  Критическая ошибка Клиента: {e}")
            raise

        finally:
            await self.stop()
