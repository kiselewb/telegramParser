from telethon import events
from core.client.utils import Utils
from core.client.services.message_manager import MessageManager
from database.db_manager import DBManager
from services.limit_manager import LimitManager
from services.parser_data_manager import ParserDataManager


class ClientHandlers:
    def __init__(self, client, db: DBManager, pdm: ParserDataManager, lm: LimitManager, config):
        self.client = client
        self.config = config
        self.db = db
        self.pdm = pdm
        self.mm = MessageManager(client, db, pdm, lm)
        self.utils = Utils(db, pdm)

    def register(self):
        @self.client.on(
            events.NewMessage(
                outgoing=False,
                func=self.utils.is_allowed_message,
            )
        )
        async def handle_group_message(event):
            await self.mm.manage_group_message(event)

        @self.client.on(
            events.NewMessage(incoming=True, func=self.utils.is_customer_first_message)
        )
        async def handle_private_message(event):
            await self.mm.manage_private_message(event.message)
