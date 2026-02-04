from datetime import datetime, timezone

from core.client.utils import check_already_contacted
from database.db_manager import DBManager
from core.client.services.notification_manager import NotificationManager
from database.enums import ProcessedMessageStatus
from services.limit_manager import LimitManager
from services.logger import Logger
from services.parser_data_manager import ParserDataManager

logger = Logger(__name__).setup_logger()

class MessageManager:
    def __init__(self, client):
        self.client = client
        self.db = DBManager()
        self.nm = NotificationManager(self.client)
        self.pdm = ParserDataManager()
        self.lm = LimitManager()

    async def manage_group_message(self, message):
        await self._save_data_message(message)

        if await self._check_message(message):
            logger.info(f"Пользователь {message.sender_id} уже получал сообщение со скриптом.")
            return

        await self._process_message(message)

    async def manage_private_message(self, message):
        await self._set_processed_message_is_replied(message)
        await self.nm.sent_notification_to_admin(message)

    async def _save_data_message(self, message):
        _, _, keyword = self._get_keyword_data(message.text)

        data_message = {
            "chat_id": message.chat_id,
            "message_id": message.id,
            "sender_id": message.sender_id,
            "text": message.text,
            "matched_keyword": keyword or "NO DATA",
            "message_date": message.date,
        }

        await self.db.save_data_message(data_message)
        logger.info(
            f"Сообщение от пользователя с ID {data_message.get('sender_id')} сохранено. ID сообщения: {data_message.get('message_id')}"
        )

    async def _check_message(self, message) -> bool:
        is_contacted = await check_already_contacted(message.sender_id)
        if is_contacted:
            return True
        return False

    async def _process_message(self, message):
        processed_message = await self._save_processed_message(message)

        await self.lm.wait_allow_sending_message()

        await self._send_processed_message(processed_message)
        await self._set_processed_message_is_sent(processed_message)

    async def _save_processed_message(self, message):
        data_id, category, _ = self._get_keyword_data(message.text)
        parser_data = self.pdm.get_parser_data_by_id(data_id)

        processed_message = {
            "recipient_id": message.sender_id,
            "category": category,
            "template": parser_data.get("template"),
        }

        processed_message = await self.db.save_processed_message(processed_message)
        logger.info(f"Сообщение с ID {message.id} принято в обработку.")

        return processed_message

    async def _send_processed_message(self, processed_message):
        await self.client.send_message(processed_message.recipient_id, processed_message.template)
        logger.info(
            f"Скрипт: {processed_message.template[:50]}... Отправлен пользователю с ID {processed_message.recipient_id}"
        )

    async def _set_processed_message_is_sent(self, processed_message):
        await self.db.update_processed_message(
            {"status": ProcessedMessageStatus.sent, "sent_at": datetime.now(timezone.utc)},
            recipient_id=processed_message.recipient_id,
        )

    async def _set_processed_message_is_replied(self, message):
        await self.db.update_processed_message(
            {"is_replied": True, "replied_at": datetime.now(timezone.utc)},
            recipient_id=message.sender_id,
        )
        logger.info(f"Пользователь с ID {message.sender_id} ответил на скрипт.")

    def _get_keyword_data(
        self, message_text: str
    ) -> tuple[int | None, str | None, str | None]:
        text = message_text.lower()

        for data in self.pdm.get_parser_data():
            for keyword in data.get("keywords", []):
                if keyword in text:
                    return data.get("id"), data.get("category"), keyword

        return None, None, None
