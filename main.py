import asyncio
import signal

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

    def handle_signal(sig, frame):
        sig_name = signal.Signals(sig).name if hasattr(signal, 'Signals') else str(sig)
        logger.info(f"⚠️ Получен сигнал {sig_name}")
        shutdown_event.set()

    signal.signal(signal.SIGINT, handle_signal)
    if hasattr(signal, 'SIGTERM'):
        signal.signal(signal.SIGTERM, handle_signal)

    app_task = asyncio.create_task(app.run())

    try:
        wait_task = asyncio.create_task(shutdown_event.wait())
        done, pending = await asyncio.wait(
            {app_task, wait_task},
            return_when=asyncio.FIRST_COMPLETED
        )

        if wait_task in done and not app_task.done():
            logger.info("🛑 Начинаю graceful shutdown...")

            app_task.cancel()

            try:
                await asyncio.wait_for(app_task, timeout=10.0)
            except asyncio.TimeoutError:
                logger.warning("⚠️ Таймаут ожидания завершения приложения, принудительная остановка")
            except asyncio.CancelledError:
                logger.info("✅ Приложение корректно завершено")

        for task in pending:
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

    except Exception as e:
        logger.error(f"❌ Ошибка в main: {e}")
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⚠️ Программа прервана пользователем")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")