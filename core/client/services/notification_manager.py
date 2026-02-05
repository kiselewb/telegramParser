from config.settings import settings
from services.logger import Logger

logger = Logger(__name__).setup_logger()


class NotificationManager:
    def __init__(self, client):
        self.client = client

    async def sent_notification_to_admin(self, message):
        try:
            user_id = message.sender_id
            user = await self.client.get_entity(user_id)
            username = user.username or ""
            reply_text = message.text

            notification = f"""
            🔔 НОВЫЙ ОТВЕТ!

            От: {"@" + username if username else ""} ID: {user_id}
            Сообщение: {reply_text[:200]}

            {"Ссылка: https://t.me/" + username if username else ""}
            """

            if settings.ADMIN_ID:
                for admin_id in settings.ADMIN_ID:
                    await self.client.send_message(admin_id, notification)
                    logger.info("📨  Уведомление успешно отправлено администратору")
            else:
                logger.warning(
                    "❌ Ошибка отправки уведомления администратору: в конфигурации не указан ни один администратор!"
                )
        except Exception as e:
            logger.error(f"❌ Ошибка отправки уведомления администратору {e}")
