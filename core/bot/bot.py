import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from core.bot.handlers.handlers import BotHandlers
from core.bot.middlewares.middlewares import BotMiddlewares
from services.logger import Logger

logger = Logger(__name__).setup_logger()


class TGBot:
    def __init__(self, bot_token: str):
        self.bot = Bot(
            token=bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        self.dp = Dispatcher()
        self.middlewares = BotMiddlewares(self.dp)
        self.handlers = BotHandlers(self.dp)
        self.is_running = False

    async def start(self):
        if not self.is_running:
            self.middlewares.register()
            self.handlers.register()
            await self.bot.delete_webhook(drop_pending_updates=True)
            self.is_running = True
            logger.info("✅ Бот запущен и готов к работе")

    async def stop(self):
        if self.is_running:
            logger.info("🔄  Остановка Бота...")
            await self.bot.session.close()
            self.is_running = False
            logger.info("✅ Бот остановлен корректно")

    async def run(self):
        try:
            await self.start()
            logger.info("🤖  Бот работает. Нажмите Ctrl+C для остановки")
            await self.dp.start_polling(self.bot)

        except asyncio.exceptions.CancelledError:
            logger.info("\n⚠️  Получен сигнал остановки Бота")

        except Exception as e:
            logger.error(f"❌  Критическая ошибка Бота: {e}")
            raise

        finally:
            await self.stop()
