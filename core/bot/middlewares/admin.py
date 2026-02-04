from typing import Callable, Awaitable, Any
from aiogram import BaseMiddleware
from aiogram.types import Message

from services.logger import Logger

logger = Logger(__name__).setup_logger()

class AdminMiddleware(BaseMiddleware):
    def __init__(self, admin_id: int):
        self.admin_id = admin_id
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any],
    ) -> Any:
        if event.from_user.id != self.admin_id:
            logger.info(
                f"⚠️ Попытка доступа от неавторизованного пользователя: {event.from_user.id}"
            )
            await event.answer("⛔ У вас нет доступа к этому боту.")
            return None

        return await handler(event, data)
