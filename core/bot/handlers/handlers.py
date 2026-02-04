from aiogram import Router
from core.bot.handlers.common import router as common_router
from core.bot.handlers.start import router as start_router
from core.bot.handlers.templates import router as template_router
from core.bot.handlers.exclude_keywords import router as exclude_templates_router
from core.bot.handlers.include_keywords import router as include_keywords_router


class BotHandlers:
    def __init__(self, dp):
        self.dp = dp
        self.router = Router()

    def register(self):
        self.dp.include_router(common_router)
        self.dp.include_router(include_keywords_router)
        self.dp.include_router(exclude_templates_router)
        self.dp.include_router(template_router)
        self.dp.include_router(start_router)
