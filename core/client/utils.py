from telethon.events import NewMessage

from database.db_manager import DBManager
from services.logger import Logger
from services.parser_data_manager import ParserDataManager

db = DBManager()
pdm = ParserDataManager()
logger = Logger(__name__).setup_logger()


async def is_allowed_message(event: NewMessage.Event) -> bool:
    message = event.message.text
    is_chat = event.is_group

    if not message or not is_chat:
        return False

    try:
        text = message.lower()

        for exclude_word in pdm.get_exclude_keywords():
            if exclude_word in text:
                return False

        for include_keyword in pdm.get_include_keywords():
            if include_keyword in text:
                return True

        return False

    except Exception as e:
        logger.error(f"Ошибка проверки ключевых фраз: {e}")
        return False


async def is_customer_first_message(event: NewMessage.Event) -> bool:
    is_customer = event.is_private
    is_first_message = await db.get_processed_message(
        recipient_id=event.sender_id, is_replied=False
    )

    return is_customer and is_first_message


async def check_already_contacted(sender_id: int) -> bool | None:
    return await db.get_processed_message(recipient_id=sender_id)
