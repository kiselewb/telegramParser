import asyncio
from datetime import datetime
from config.settings import settings
from services.logger import Logger

logger = Logger(__name__).setup_logger()


class LimitManager:
    _instance: "LimitManager | None" = None
    _last_reset: datetime
    _count_sent_message: int

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._last_reset = datetime.now()
            cls._instance._count_sent_message = 0
            cls._instance._limit_message = settings.LIMIT_COUNT_MESSAGE
            cls._instance._limit_waiting = settings.LIMIT_WAITING_MESSAGE
            cls._instance._delay_sending = settings.DELAY_SENDING_MESSAGE
            cls._instance._ready = asyncio.Event()
            cls._instance._lock = asyncio.Lock()

        return cls._instance

    async def init(self):
        logger.info(
            f"✅ LimitManager лимитов инициализирован. Текущее значение таймера: {self._last_reset.strftime('%H:%M:%S')}. Лимит: {self._limit_message} сообщений за {self._limit_waiting} сек."
        )
        self._ready.set()

        while True:
            await asyncio.sleep(self._limit_waiting)
            async with self._lock:
                self._last_reset = datetime.now()
                self._count_sent_message = 0
            logger.info(
                f"🔄  Лимиты сброшены. Текущее значение таймера: {self._last_reset.strftime('%H:%M:%S')}."
            )

    async def wait_allow_sending_message(self) -> bool:
        async with self._lock:
            waiting_time = await self._check_count_limit()

        if waiting_time > 0:
            logger.info(
                f"⏳ Достигнут лимит отправки сообщений. Ожидаем {waiting_time:.1f} сек..."
            )
            await asyncio.sleep(waiting_time)

        await self._wait_for_sending()
        logger.info("✉️ Сообщение готово к отправке!")
        return True

    async def _check_count_limit(self) -> float:
        if self._count_sent_message >= self._limit_message:
            waiting_time = (
                self._limit_waiting
                - (datetime.now() - self._last_reset).total_seconds()
            )

            if waiting_time > 0:
                return waiting_time

            self._last_reset = datetime.now()
            self._count_sent_message = 0

        self._count_sent_message += 1
        logger.info(
            f"📊 Отправка сообщения доступна. Текущий счетчик: {self._count_sent_message}/{self._limit_message}"
        )

        return 0.0

    async def _wait_for_sending(self):
        if self._delay_sending > 0:
            logger.info(
                f"⏱️ Задержка перед отправкой сообщения: {self._delay_sending} сек..."
            )
            await asyncio.sleep(self._delay_sending)

    async def wait_ready(self):
        await self._ready.wait()
