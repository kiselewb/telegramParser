import asyncio
import signal

from app import Application
from config.settings import settings
from services.logger import Logger

logger = Logger(__name__).setup_logger()


def setup_signal_handlers(shutdown_event):
    def handle_signal(sig, frame):
        sig_name = signal.Signals(sig).name if hasattr(signal, 'Signals') else str(sig)
        logger.info(f"⚠️ Получен сигнал {sig_name}")
        shutdown_event.set()

    signal.signal(signal.SIGINT, handle_signal)

    if hasattr(signal, 'SIGTERM'):
        signal.signal(signal.SIGTERM, handle_signal)


async def main():
    app = Application(
        session_name=settings.SESSION_NAME,
        api_id=settings.API_ID,
        api_hash=settings.API_HASH,
        bot_token=settings.BOT_TOKEN,
    )

    shutdown_event = asyncio.Event()

    setup_signal_handlers(shutdown_event)

    app_task = asyncio.create_task(app.run())
    wait_task = asyncio.create_task(shutdown_event.wait())

    done, pending = await asyncio.wait(
        {app_task, wait_task},
        return_when=asyncio.FIRST_COMPLETED
    )

    if wait_task in done and not app_task.done():
        logger.info("🛑 Начинаю graceful shutdown...")
        app_task.cancel()
        try:
            await app_task
        except asyncio.CancelledError:
            logger.info("✅ Приложение корректно завершено")

    for task in pending:
        if not task.done():
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