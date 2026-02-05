from telethon import events
from core.client.utils import (
    is_allowed_message,
    is_customer_first_message,
)
from core.client.services.message_manager import MessageManager


class ClientHandlers:
    def __init__(self, client, config):
        self.client = client
        self.config = config
        self.mm = MessageManager(self.client)

    def register(self):
        @self.client.on(
            events.NewMessage(
                outgoing=False,
                func=is_allowed_message,
            )
        )
        async def handle_group_message(event):
            await self.mm.manage_group_message(event)

        @self.client.on(
            events.NewMessage(incoming=True, func=is_customer_first_message)
        )
        async def handle_private_message(event):
            await self.mm.manage_private_message(event.message)
