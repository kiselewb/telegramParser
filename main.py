import asyncio
import signal
import sys

from app import Application
from config.settings import settings
from services.logger import Logger

logger = Logger(__name__).setup_logger()


async def main():
    app = Application(
        session_name=settings.SESSION_NAME,
        api_id=settings.API_ID,
        api_hash=settings.API_HASH,
        bot_token=settings.BOT_TOKEN,
    )

    shutdown_event = asyncio.Event()

    def signal_handler(signum, frame):
        logger.info(f"⚠️ Получен сигнал завершения ({signum})")
        shutdown_event.set()

    signal.signal(signal.SIGINT, signal_handler)
    if sys.platform != "win32":
        signal.signal(signal.SIGTERM, signal_handler)

    app_task = asyncio.create_task(app.run())

    shutdown_task = asyncio.create_task(shutdown_event.wait())

    done, pending = await asyncio.wait(
        [app_task, shutdown_task],
        return_when=asyncio.FIRST_COMPLETED
    )

    if shutdown_event.is_set() and not app_task.done():
        logger.info("🛑 Инициирую остановку приложения...")
        app_task.cancel()
        try:
            await app_task
        except asyncio.CancelledError:
            logger.info("✅ Приложение успешно остановлено")

    # Отменяем оставшиеся задачи
    for task in pending:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⚠️ Программа прервана пользователем")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")