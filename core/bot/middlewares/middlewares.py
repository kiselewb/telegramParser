from config.settings import settings
from core.bot.middlewares.admin import AdminMiddleware


class BotMiddlewares:
    def __init__(self, dp):
        self.dp = dp

    def register(self):
        self.dp.message.middleware(AdminMiddleware(settings.ADMIN_ID))
